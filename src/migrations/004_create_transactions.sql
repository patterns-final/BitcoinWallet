PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS transactions (
    id                    TEXT PRIMARY KEY,
    from_wallet_address   TEXT NOT NULL,
    to_wallet_address     TEXT NOT NULL,
    amount_satoshis       INTEGER NOT NULL CHECK (amount_satoshis > 0),
    fee_satoshis          INTEGER NOT NULL CHECK (fee_satoshis >= 0),
    is_internal_transfer  INTEGER NOT NULL DEFAULT 0,
    created_at            TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_transactions_from_wallet ON transactions(from_wallet_address);
CREATE INDEX IF NOT EXISTS idx_transactions_to_wallet ON transactions(to_wallet_address);
CREATE INDEX IF NOT EXISTS idx_transactions_created_at ON transactions(created_at);