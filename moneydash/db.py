import sqlite3
import json


JSON = ['inventory', 'job', 'company']
SUM = ['bank', 'wallet']


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
    company TEXT
)''')


def create_account(uId) -> None:
    db = _connect_db()
    cur = db.cursor()

    cur.execute(f'''SELECT * FROM users WHERE uId = {uId}''')
    data = cur.fetchone()
    if data is None:
        cur.execute(
            f'''INSERT INTO users VALUES({uId}, 0, 0, '{{"items": []}}', '{{}}', '{{}}')''')
        db.commit()
    cur.close()
    db.close()


def get_account(uId) -> dict:
    '''Returned dict: {'uId': int, 'bank': int, 'wallet': int, 'inventory': dict, 'job': dict, 'company': dict}'''
    db = _connect_db()
    cur = db.cursor()
    cur.execute(f'''SELECT * FROM users WHERE uId = {uId}''')
    d = cur.fetchone()
    cur.close()
    db.close()
    return {'uId': d[0], 'bank': d[1], 'wallet': d[2], 'inventory': json.loads(d[3]), 'job': json.loads(d[4]), 'company': json.loads(d[5])}


def update_account(uId, *args) -> None:
    db = _connect_db()
    cur = db.cursor()
    for st in args:
        if st[0] in JSON:
            val = f"'{json.dumps(st[1])}'"
        elif st[0] in SUM:
            val = f"{st[0]} + {st[1]}"
        else:
            val = st[1]
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
