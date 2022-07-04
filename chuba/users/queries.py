
CREATE_USERS_TABLE: str = """
CREATE TABLE if not EXISTS users (
    id INTEGER PRIMARY KEY,
    promo TEXT UNIQUE DEFAULT NULL,
    subscription DATE DEFAULT NULL,
    vipsubscription DATE DEFAULT NULL,
    last_payment_id TEXT DEFAULT NULL,
    subscription_id TEXT DEFAULT NULL
)
"""

CREATE_USER: str = """
INSERT OR IGNORE INTO users (id) VALUES (?)
"""

GET_USER: str = """
SELECT * FROM users WHERE id=?
"""

UPDATE_USER: str = """
UPDATE users
    SET
        id = ?,
        promo = ?,
        subscription = ?,
        vipsubscription = ?,
        last_payment_id = ?,
        subscription_id = ?
    WHERE id = ?
"""

GET_EXPIRIED_SUBSCRIPTIONS: str = """
SELECT *
    FROM users
    WHERE strftime('%s', CURRENT_DATE) > strftime('%s', subscription)
"""

GET_EXPIRIED_VIPSUBSCRIPTIONS: str = """
SELECT *
    FROM users
    WHERE strftime('%s', CURRENT_DATE) > strftime('%s', vipsubscription)
"""
