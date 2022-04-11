import sqlite3
import json


JSON = ['inventory', 'meta']
DEFAULT_META = '''{"badges": [], "emoji": "", "color": "0x99aab5", "font": ""}'''
SUM = ['bank', 'wallet', 'level', 'exp']


def _connect_db() -> sqlite3.Connection:
    return sqlite3.connect('./moneydash/data.sqlite')


db = _connect_db()
cur = db.cursor()
cur.execute(f'''CREATE TABLE IF NOT EXISTS users (
    uId INT,
    bank INT,
    wallet INT,
    inventory TEXT,
    job TEXT,
    company INT,
    meta TEXT,
    level INT,
    exp INT
)''')


def create_account(uId) -> None:
    db = _connect_db()
    cur = db.cursor()

    cur.execute(f'''SELECT * FROM users WHERE uId = {uId}''')
    data = cur.fetchone()
    if data is None:
        cur.execute(
            f'''INSERT INTO users VALUES({uId}, 0, 0, '{{"items": []}}', 'None', 0, '{DEFAULT_META}', 1, 0)''')
        db.commit()
    cur.close()
    db.close()


def get_account(uId) -> dict:
    '''Returned dict: {'uId': int, 'bank': int, 'wallet': int, 'inventory': dict, 'job': str, 'company': int, meta: 'dict', 'level': int, 'exp': int}'''
    db = _connect_db()
    cur = db.cursor()
    cur.execute(f'''SELECT * FROM users WHERE uId = {uId}''')
    d = cur.fetchone()
    cur.close()
    db.close()
    return {'uId': d[0], 'bank': d[1], 'wallet': d[2], 'inventory': json.loads(d[3]), 'job': d[4], 'company': d[5], 'meta': json.loads(d[6]), 'level': d[7], 'exp': d[8]}


def update_account(uId, *args) -> None:
    db = _connect_db()
    cur = db.cursor()
    for st in args:
        if st[0] in JSON:
            val = f"'{json.dumps(st[1])}'"
        elif st[0] in SUM:
            val = f"{st[0]} + {st[1]}"
        else:
            val = f"'{st[1]}'"
        cur.execute(f'''UPDATE users SET {st[0]} = {val} WHERE uId = {uId}''')
    db.commit()
    cur.close()
    db.close()


def stats() -> dict:
    db = _connect_db()
    cur = db.cursor()
    st = cur.execute(
        '''SELECT SUM(bank), SUM(wallet), AVG(bank), AVG(wallet) FROM users''').fetchone()
    return {'bank_sum': st[0], 'wallet_sum': st[1], 'wallet_avg': st[2], 'bank_avg': st[3]}
