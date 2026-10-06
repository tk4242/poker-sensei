# ビルドはリポジトリのルートを文脈にする（app/docker-compose.yml の context: ..）
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 SENSEI_REPO_ROOT=/srv/poker-sensei SENSEI_DATA_DIR=/data
WORKDIR /srv/poker-sensei
COPY app/requirements.txt app/requirements.txt
RUN pip install --no-cache-dir -r app/requirements.txt && useradd -r -u 10001 sensei && mkdir -p /data && chown sensei /data
COPY tools tools
COPY curriculum curriculum
COPY sources sources
COPY learner learner
COPY app app
USER sensei
WORKDIR /srv/poker-sensei/app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s CMD python -c "import urllib.request;urllib.request.urlopen('http://127.0.0.1:8000/health')"
# 1プロセス＋スレッド（ログイン失敗の記録・SQLite と相性がよい）
CMD ["gunicorn", "-b", "0.0.0.0:8000", "-w", "1", "--threads", "8", "--timeout", "300", "--access-logfile", "-", "sensei:create_app()"]
