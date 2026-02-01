PRAGMA foreign_keys = ON;

CREATE UNIQUE INDEX IF NOT EXISTS idx_users_api_key ON users(api_key);

CREATE INDEX IF NOT EXISTS idx_wallets_user_id ON wallets(user_id);
