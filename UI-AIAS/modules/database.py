"""
database.py
Gestión de la base de datos local SQLite3.
Tablas: historial_consultas, diagnosticos_guardados, logs_analizados.
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).resolve().parent.parent / "admin_suite.db"


class DatabaseManager:
    """ORM ligero sobre SQLite3."""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def _init_db(self) -> None:
        sql = """
        CREATE TABLE IF NOT EXISTS historial_consultas (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha     TEXT NOT NULL,
            modulo    TEXT NOT NULL,
            prompt    TEXT NOT NULL,
            respuesta TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS diagnosticos_guardados (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha      TEXT NOT NULL,
            sistema_os TEXT NOT NULL,
            titulo     TEXT NOT NULL,
            datos      TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS logs_analizados (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha          TEXT NOT NULL,
            nombre_archivo TEXT NOT NULL,
            resumen_ia     TEXT NOT NULL
        );
        """
        with self._connect() as conn:
            conn.executescript(sql)

    # ── Consultas ─────────────────────────────────────────────────────────
    def save_query(self, modulo: str, prompt: str, respuesta: str) -> None:
        sql = "INSERT INTO historial_consultas (fecha,modulo,prompt,respuesta) VALUES (?,?,?,?)"
        with self._connect() as conn:
            conn.execute(sql, (datetime.now().isoformat(sep=" ", timespec="seconds"),
                               modulo, prompt, respuesta))

    def get_queries(self, limit: int = 20) -> list:
        sql = "SELECT id,fecha,modulo,prompt,respuesta FROM historial_consultas ORDER BY id DESC LIMIT ?"
        with self._connect() as conn:
            return [dict(r) for r in conn.execute(sql, (limit,)).fetchall()]

    # ── Diagnósticos ──────────────────────────────────────────────────────
    def save_diagnostic(self, sistema_os: str, titulo: str, datos: str) -> None:
        sql = "INSERT INTO diagnosticos_guardados (fecha,sistema_os,titulo,datos) VALUES (?,?,?,?)"
        with self._connect() as conn:
            conn.execute(sql, (datetime.now().isoformat(sep=" ", timespec="seconds"),
                               sistema_os, titulo, datos))

    def get_diagnostics(self, limit: int = 10) -> list:
        sql = "SELECT id,fecha,sistema_os,titulo,datos FROM diagnosticos_guardados ORDER BY id DESC LIMIT ?"
        with self._connect() as conn:
            return [dict(r) for r in conn.execute(sql, (limit,)).fetchall()]

    # ── Logs ──────────────────────────────────────────────────────────────
    def save_log_analysis(self, nombre_archivo: str, resumen_ia: str) -> None:
        sql = "INSERT INTO logs_analizados (fecha,nombre_archivo,resumen_ia) VALUES (?,?,?)"
        with self._connect() as conn:
            conn.execute(sql, (datetime.now().isoformat(sep=" ", timespec="seconds"),
                               nombre_archivo, resumen_ia))

    def get_log_analyses(self, limit: int = 10) -> list:
        sql = "SELECT id,fecha,nombre_archivo,resumen_ia FROM logs_analizados ORDER BY id DESC LIMIT ?"
        with self._connect() as conn:
            return [dict(r) for r in conn.execute(sql, (limit,)).fetchall()]

    # ── Utilidades ────────────────────────────────────────────────────────
    def get_stats(self) -> dict:
        with self._connect() as conn:
            q = conn.execute("SELECT COUNT(*) FROM historial_consultas").fetchone()[0]
            d = conn.execute("SELECT COUNT(*) FROM diagnosticos_guardados").fetchone()[0]
            l = conn.execute("SELECT COUNT(*) FROM logs_analizados").fetchone()[0]
        return {"consultas": q, "diagnosticos": d, "logs": l}

    def clear_all(self) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM historial_consultas")
            conn.execute("DELETE FROM diagnosticos_guardados")
            conn.execute("DELETE FROM logs_analizados")