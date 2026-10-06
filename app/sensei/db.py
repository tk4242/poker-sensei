"""SQLite（標準ライブラリ）。1人用なのでこれで十分。データは DATA_DIR/sensei.db。"""
import json
import sqlite3
from datetime import datetime, timedelta

from flask import current_app, g

SCHEMA = """
CREATE TABLE IF NOT EXISTS attempts(
  id INTEGER PRIMARY KEY, ts TEXT NOT NULL, mode TEXT NOT NULL, kind TEXT NOT NULL,
  qkey TEXT NOT NULL, tag TEXT NOT NULL, stage INTEGER, correct INTEGER NOT NULL,
  dontknow INTEGER NOT NULL DEFAULT 0, elapsed_ms INTEGER, batch_id INTEGER);
CREATE INDEX IF NOT EXISTS attempts_ts ON attempts(ts);
CREATE TABLE IF NOT EXISTS srs(
  qkey TEXT PRIMARY KEY, kind TEXT, tag TEXT, box INTEGER NOT NULL, due TEXT NOT NULL,
  last TEXT, lapses INTEGER NOT NULL DEFAULT 0, snapshot TEXT);
CREATE TABLE IF NOT EXISTS batches(
  id INTEGER PRIMARY KEY, created TEXT NOT NULL, mode TEXT NOT NULL, title TEXT,
  req_id TEXT, lesson_id TEXT, questions TEXT NOT NULL, graded INTEGER NOT NULL DEFAULT 0, result TEXT);
CREATE TABLE IF NOT EXISTS exams(
  id INTEGER PRIMARY KEY, ts TEXT NOT NULL, req_id TEXT NOT NULL, score INTEGER, total INTEGER, passed INTEGER);
CREATE TABLE IF NOT EXISTS lessons_done(lesson_id TEXT PRIMARY KEY, ts TEXT NOT NULL, score INTEGER, total INTEGER);
CREATE TABLE IF NOT EXISTS play_sessions(
  id INTEGER PRIMARY KEY, date TEXT, venue TEXT, event TEXT, buyin REAL, currency TEXT,
  entries INTEGER, finish INTEGER, itm INTEGER, prize REAL, hours REAL, condition INTEGER,
  tilt INTEGER, tilt_types TEXT, opponents TEXT, good TEXT, improve TEXT, notes TEXT, created TEXT);
CREATE TABLE IF NOT EXISTS hands(
  id INTEGER PRIMARY KEY, date TEXT, title TEXT, event TEXT, phase TEXT, blinds TEXT, eff_bb REAL,
  hero_pos TEXT, hero_cards TEXT, villain TEXT, preflop TEXT, flop TEXT, turn TEXT, river TEXT,
  result TEXT, self_review TEXT, question TEXT, ai_review TEXT, created TEXT);
CREATE TABLE IF NOT EXISTS checkins(
  id INTEGER PRIMARY KEY, ts TEXT NOT NULL, kind TEXT NOT NULL, data TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS study_log(
  id INTEGER PRIMARY KEY, date TEXT NOT NULL, minutes INTEGER NOT NULL, topic TEXT, note TEXT);
CREATE TABLE IF NOT EXISTS coach_log(
  id INTEGER PRIMARY KEY, ts TEXT NOT NULL, question TEXT, answer TEXT, citations TEXT);
CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE IF NOT EXISTS login_failures(ip TEXT, ts TEXT);
"""


def now():
    return datetime.now().replace(microsecond=0)


def iso(dt):
    return dt.isoformat(timespec="seconds")


def today():
    return now().date().isoformat()


def connect(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path, timeout=10)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA foreign_keys=ON")
    return con


def init_db(path):
    con = connect(path)
    con.executescript(SCHEMA)
    con.commit()
    con.close()


def get_db():
    if "db" not in g:
        g.db = connect(current_app.config["DB_PATH"])
    return g.db


def close_db(_exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def q(sql, args=(), one=False):
    cur = get_db().execute(sql, args)
    rows = cur.fetchall()
    return (rows[0] if rows else None) if one else rows


def ex(sql, args=()):
    db = get_db()
    cur = db.execute(sql, args)
    db.commit()
    return cur.lastrowid


def get_setting(key, default=None):
    row = q("SELECT value FROM settings WHERE key=?", (key,), one=True)
    if row is None:
        return default
    try:
        return json.loads(row["value"])
    except (TypeError, ValueError):
        return row["value"]


def set_setting(key, value):
    ex("INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
       (key, json.dumps(value, ensure_ascii=False)))


def days_ago(n):
    return iso(now() - timedelta(days=n))
