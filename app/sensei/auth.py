"""本人だけが使うためのログイン（1ユーザー）、CSRF 対策、ログイン失敗の回数制限。"""
import hashlib
import hmac
import secrets
from datetime import timedelta
from functools import wraps

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, session, url_for

from .db import ex, iso, now, q

bp = Blueprint("auth", __name__)

MAX_FAILURES = 5          # この回数を超えたら
LOCK_MINUTES = 15         # この時間ロック
SCRYPT = dict(n=2 ** 14, r=8, p=1)


def hash_password(password, salt=None):
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, dklen=32, **SCRYPT)
    return f"scrypt:{SCRYPT['n']}:{SCRYPT['r']}:{SCRYPT['p']}:{salt.hex()}:{digest.hex()}"


def verify_hash(password, stored):
    try:
        algo, n, r, p, salt, digest = stored.strip().split(":")
        if algo != "scrypt":
            return False
        got = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), dklen=32,
                             n=int(n), r=int(r), p=int(p))
        return hmac.compare_digest(got.hex(), digest)
    except (ValueError, TypeError):
        return False


def check_credentials(user, password):
    cfg = current_app.config
    user_ok = hmac.compare_digest(user.encode(), cfg["APP_USER"].encode())
    if cfg.get("APP_PASSWORD_HASH"):
        pw_ok = verify_hash(password, cfg["APP_PASSWORD_HASH"])
    else:
        pw_ok = bool(cfg.get("APP_PASSWORD")) and hmac.compare_digest(
            password.encode(), cfg["APP_PASSWORD"].encode())
    return user_ok and pw_ok


def client_ip():
    return request.remote_addr or "?"


def locked(ip):
    since = iso(now() - timedelta(minutes=LOCK_MINUTES))
    row = q("SELECT COUNT(*) c FROM login_failures WHERE ip=? AND ts>=?", (ip, since), one=True)
    return row["c"] >= MAX_FAILURES


def csrf_token():
    if "csrf" not in session:
        session["csrf"] = secrets.token_hex(16)
    return session["csrf"]


def csrf_protect():
    """POST はすべてトークン確認（ログインも含む）。"""
    if request.method != "POST":
        return
    sent = request.form.get("csrf") or request.headers.get("X-CSRF-Token", "")
    if not sent or not hmac.compare_digest(sent, session.get("csrf", "")):
        abort(400, "フォームの有効期限が切れました。ページを再読み込みしてください。")


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user"):
            return redirect(url_for("auth.login", next=request.full_path))
        return view(*args, **kwargs)
    return wrapped


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        ip = client_ip()
        if locked(ip):
            flash(f"ログイン失敗が続いたため {LOCK_MINUTES} 分ロック中です。時間をおいてください。", "error")
            return render_template("login.html"), 429
        if check_credentials(request.form.get("user", ""), request.form.get("password", "")):
            ex("DELETE FROM login_failures WHERE ip=?", (ip,))
            session.clear()
            session.permanent = True
            session["user"] = current_app.config["APP_USER"]
            nxt = request.args.get("next", "")
            # 自サイト内のパスだけ許可（オープンリダイレクト対策）
            if not nxt.startswith("/") or nxt.startswith("//"):
                nxt = url_for("main.home")
            return redirect(nxt)
        ex("INSERT INTO login_failures(ip,ts) VALUES(?,?)", (ip, iso(now())))
        flash("ユーザー名かパスワードが違います。", "error")
        return render_template("login.html"), 401
    return render_template("login.html")


@bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
