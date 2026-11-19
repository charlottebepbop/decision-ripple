// Full-text index over decision titles and note bodies. Indexes live in vault/.cypherlite/,
// which is not committed, so a fresh clone runs this once (scripts/serve.sh does it).
CREATE FULLTEXT INDEX decision_text IF NOT EXISTS FOR (d:Decision) ON EACH [d.title, d.text];
