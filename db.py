import mysql.connector
from mysql.connector import Error
from config import Config


# ─────────────────────────────────────────────
#  Connection helpers
# ─────────────────────────────────────────────

def get_connection(use_db=True):
    """Return a raw mysql-connector connection."""
    kwargs = dict(
        host=Config.MYSQL_HOST,
        port=Config.MYSQL_PORT,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        autocommit=False,
    )
    if use_db:
        kwargs['database'] = Config.MYSQL_DB
    try:
        return mysql.connector.connect(**kwargs)
    except Error as exc:
        print(f"[CyberSafe DB] Connection error: {exc}")
        return None


def query(sql, params=(), one=False):
    """Run a SELECT and return dict rows (or a single row)."""
    conn = get_connection()
    if conn is None:
        return None
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params)
        rows = cur.fetchall()
        return (rows[0] if rows else None) if one else rows
    except Error as exc:
        print(f"[CyberSafe DB] Query error: {exc}")
        return None
    finally:
        cur.close(); conn.close()


def execute(sql, params=(), return_id=False):
    """Run INSERT / UPDATE / DELETE and optionally return lastrowid."""
    conn = get_connection()
    if conn is None:
        return None
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        conn.commit()
        return cur.lastrowid if return_id else cur.rowcount
    except Error as exc:
        conn.rollback()
        print(f"[CyberSafe DB] Execute error: {exc}")
        return None
    finally:
        cur.close(); conn.close()


# ─────────────────────────────────────────────
#  SQL script parser (handles quoted ';')
# ─────────────────────────────────────────────

def _split_sql(text):
    stmts, buf = [], []
    sq = dq = esc = False
    i = 0
    while i < len(text):
        c = text[i]
        if esc:
            buf.append(c); esc = False; i += 1; continue
        if c == '\\':
            buf.append(c); esc = True; i += 1; continue
        if not sq and not dq:
            if c == '-' and i+1 < len(text) and text[i+1] == '-':
                while i < len(text) and text[i] != '\n':
                    i += 1
                continue
            if c == '/' and i+1 < len(text) and text[i+1] == '*':
                i += 2
                while i+1 < len(text) and not (text[i] == '*' and text[i+1] == '/'):
                    i += 1
                i += 2; continue
        if c == "'" and not dq: sq = not sq
        elif c == '"' and not sq: dq = not dq
        elif c == ';' and not sq and not dq:
            s = ''.join(buf).strip()
            if s: stmts.append(s)
            buf = []; i += 1; continue
        buf.append(c); i += 1
    s = ''.join(buf).strip()
    if s: stmts.append(s)
    return stmts


def init_db(schema_path):
    """Read schema.sql and run every statement against the server."""
    conn = get_connection(use_db=False)
    if conn is None:
        raise RuntimeError("Cannot connect to MySQL – is XAMPP running?")
    cur = conn.cursor()
    with open(schema_path, encoding='utf-8') as f:
        stmts = _split_sql(f.read())
    try:
        for s in stmts:
            cur.execute(s)
        conn.commit()
        print(f"[CyberSafe DB] Schema applied ({len(stmts)} statements).")
    except Error as exc:
        conn.rollback()
        raise exc
    finally:
        cur.close(); conn.close()
