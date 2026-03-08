DELETE FROM Users
WHERE id > 16

UPDATE sqlite_sequence
SET seq = 0
WHERE name = 'session';

DELETE FROM session
WHERE id > 0;

ALTER TABLE session ADD COLUMN created_at DATETIME DEFAULT (datetime('now'));
ALTER TABLE session ADD COLUMN last_seen_at DATETIME DEFAULT (datetime('now'));
