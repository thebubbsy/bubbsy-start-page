CREATE TABLE IF NOT EXISTS clicks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id TEXT NOT NULL,
  element_tag TEXT,
  element_id TEXT,
  element_classes TEXT,
  element_text TEXT,
  target_href TEXT,
  page_path TEXT,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  ip TEXT,
  country TEXT,
  user_agent TEXT
);

CREATE INDEX IF NOT EXISTS idx_clicks_timestamp ON clicks(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_clicks_session ON clicks(session_id);
