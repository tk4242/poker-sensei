"""ポーカー先生 Webアプリ（Flask）。起動: gunicorn 'sensei:create_app()'"""
import math
from datetime import timedelta

from flask import Flask, render_template, request
from werkzeug.middleware.proxy_fix import ProxyFix

from . import auth, content, db
from .config import Config


def seat_xy(n):
    """席の座標（画面下中央が席0、時計回り）。dx/dy はディーラーボタンの位置。"""
    cx, cy, rx, ry = 200, 148, 172, 116
    out = []
    for i in range(n):
        a = math.radians(90 + i * 360 / n)
        x, y = cx + rx * math.cos(a), cy + ry * math.sin(a)
        out.append({"x": round(x, 1), "y": round(y, 1),
                    "dx": round(cx + (x - cx) * 0.66, 1), "dy": round(cy + (y - cy) * 0.62, 1)})
    return out


def create_app(**overrides):
    cfg = Config(**overrides)
    if not cfg.TESTING:
        problems = cfg.check()
        if problems:
            raise RuntimeError("設定が足りません:\n- " + "\n- ".join(problems))
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=cfg.SECRET_KEY, APP_USER=cfg.APP_USER, APP_PASSWORD=cfg.APP_PASSWORD,
        APP_PASSWORD_HASH=cfg.APP_PASSWORD_HASH, DB_PATH=cfg.DB_PATH, TESTING=cfg.TESTING,
        ANTHROPIC_API_KEY=cfg.ANTHROPIC_API_KEY, COACH_MODEL=cfg.COACH_MODEL, COACH_EFFORT=cfg.COACH_EFFORT,
        SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax", SESSION_COOKIE_SECURE=cfg.SECURE_COOKIES,
        SESSION_COOKIE_NAME="sensei_session", PERMANENT_SESSION_LIFETIME=timedelta(days=30),
        MAX_CONTENT_LENGTH=1024 * 1024,
    )
    # Caddy（リバースプロキシ）1段の後ろで動かす前提
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
    db.init_db(cfg.DB_PATH)
    app.teardown_appcontext(db.close_db)
    app.before_request(auth.csrf_protect)

    from .views import coach_bp, learn_bp, main_bp, practice_bp, records_bp
    app.register_blueprint(auth.bp)
    for bp in (main_bp, learn_bp, practice_bp, records_bp, coach_bp):
        app.register_blueprint(bp)

    @app.before_request
    def require_login():
        if request.endpoint in ("auth.login", "static", "main.health"):
            return None
        from flask import redirect, session, url_for
        if not session.get("user"):
            return redirect(url_for("auth.login", next=request.full_path))
        return None

    @app.after_request
    def security_headers(resp):
        resp.headers.setdefault("X-Content-Type-Options", "nosniff")
        resp.headers.setdefault("X-Frame-Options", "DENY")
        resp.headers.setdefault("Referrer-Policy", "same-origin")
        resp.headers.setdefault("Content-Security-Policy",
                                "default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; "
                                "frame-ancestors 'none'; base-uri 'self'; form-action 'self'")
        return resp

    app.jinja_env.globals["seat_xy"] = seat_xy

    @app.context_processor
    def inject():
        return {"csrf_token": auth.csrf_token, "TAG_JP": content.TAG_JP, "LABEL_JP": content.LABEL_JP}

    @app.errorhandler(400)
    def bad_request(e):
        return render_template("error.html", message=getattr(e, "description", "不正なリクエスト")), 400

    @app.errorhandler(404)
    def not_found(_e):
        return render_template("error.html", message="ページが見つかりません。"), 404

    problems = content.validate_bank()
    if problems:
        app.logger.warning("問題集の形式エラー: %s", problems[:10])
    return app
