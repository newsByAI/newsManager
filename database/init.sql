CREATE TABLE IF NOT EXISTS articles (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL UNIQUE,
    url TEXT,
    published_at TIMESTAMP,
    content_preview TEXT
);
