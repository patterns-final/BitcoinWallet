PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS wallets (
    address       TEXT PRIMARY KEY,
    user_id       TEXT NOT NULL,
    balance_sats  INTEGER NOT NULL DEFAULT 0 CHECK (balance_sats >= 0),
    created_at    TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at    TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_wallets_user_id ON wallets(user_id);