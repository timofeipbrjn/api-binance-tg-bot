CREATE TABLE IF NOT EXISTS users (
    tg_id BIGINT PRIMARY KEY,
    username VARCHAR(64),
    registered_at TIMESTAMP DEFAULT NOW(),
    default_currency VARCHAR(10) DEFAULT 'USDT'
);

CREATE TABLE IF NOT EXISTS user_favorites (
    id SERIAL PRIMARY KEY,
    tg_id BIGINT REFERENCES users(tg_id) ON DELETE CASCADE,
    ticker VARCHAR(20) NOT NULL,
    added_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(tg_id, ticker)
);

CREATE TABLE IF NOT EXISTS query_history (
    id SERIAL PRIMARY KEY,
    tg_id BIGINT REFERENCES users(tg_id) ON DELETE CASCADE,
    ticker VARCHAR(20) NOT NULL,
    price NUMERIC NOT NULL,
    quiried_at TIMESTAMP DEFAULT NOW()
);
