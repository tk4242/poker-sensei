"""設定（環境変数から読む）。VPS では app/.env に書き、docker compose が読み込む。"""
import os
from pathlib import Path

REPO_ROOT = Path(os.environ.get("SENSEI_REPO_ROOT") or Path(__file__).resolve().parents[2])
APP_DIR = REPO_ROOT / "app"
CONTENT_DIR = APP_DIR / "content"
CURRICULUM_DIR = REPO_ROOT / "curriculum"
DATA_DIR = Path(os.environ.get("SENSEI_DATA_DIR") or APP_DIR / "data")


class Config:
    def __init__(self, **overrides):
        env = os.environ
        self.SECRET_KEY = env.get("SECRET_KEY", "")
        self.APP_USER = env.get("APP_USER", "koja")
        # どちらか一方: 平文（.env は chmod 600）か、`python -m sensei hash-password` の出力
        self.APP_PASSWORD = env.get("APP_PASSWORD", "")
        self.APP_PASSWORD_HASH = env.get("APP_PASSWORD_HASH", "")
        self.DB_PATH = Path(env.get("SENSEI_DB") or DATA_DIR / "sensei.db")
        # HTTPS（Caddy 経由）なら 1。ローカルの http で試すときだけ 0
        self.SECURE_COOKIES = env.get("SECURE_COOKIES", "1") == "1"
        self.ANTHROPIC_API_KEY = env.get("ANTHROPIC_API_KEY", "")
        self.COACH_MODEL = env.get("COACH_MODEL", "claude-opus-5-5")
        self.COACH_EFFORT = env.get("COACH_EFFORT", "medium")
        # 知識ベースの料金の目安（USD / 100万トークン、検索1回）。最新の料金は公式の料金ページで確認
        self.KNOWLEDGE_PRICE_IN = env.get("KNOWLEDGE_PRICE_IN", "4")
        self.KNOWLEDGE_PRICE_OUT = env.get("KNOWLEDGE_PRICE_OUT", "20")
        self.KNOWLEDGE_PRICE_SEARCH = env.get("KNOWLEDGE_PRICE_SEARCH", "0.01")
        self.TESTING = False
        for k, v in overrides.items():
            setattr(self, k, v)

    def check(self):
        problems = []
        if len(self.SECRET_KEY) < 32:
            problems.append("SECRET_KEY が未設定か短すぎます（32文字以上。`python3 -c \"import secrets;print(secrets.token_hex(32))\"`）")
        if not (self.APP_PASSWORD or self.APP_PASSWORD_HASH):
            problems.append("APP_PASSWORD か APP_PASSWORD_HASH を設定してください")
        if self.APP_PASSWORD and len(self.APP_PASSWORD) < 12:
            problems.append("APP_PASSWORD は12文字以上にしてください")
        return problems
