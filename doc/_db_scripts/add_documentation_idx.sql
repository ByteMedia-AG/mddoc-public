-- Drop tables and triggers
DROP TABLE doc_documentation_idx;
DROP TRIGGER doc_documentation_ai;
DROP TRIGGER doc_documentation_ad;
DROP TRIGGER doc_documentation_au;

-- Create the virtual table
CREATE VIRTUAL TABLE doc_documentation_idx USING fts5(id, title, info, warning, text, updated_at, deleted_at, successor_id, content=doc_documentation, content_rowid=id,  tokenize="trigram");

-- Initially populate the index
INSERT INTO doc_documentation_idx (rowid, title, info, warning, text) SELECT id, title, info, warning, text FROM doc_documentation;

-- Create the insert, delete and update triggers
CREATE TRIGGER doc_documentation_ai AFTER INSERT ON doc_documentation BEGIN
    INSERT INTO doc_documentation_idx(rowid, title, info, warning, text) VALUES (new.id, new.title, new.info, new.warning, new.text);
END;
CREATE TRIGGER doc_documentation_ad AFTER DELETE ON doc_documentation BEGIN
  INSERT INTO doc_documentation_idx(doc_documentation_idx, rowid, title, info, warning, text) VALUES('delete', old.id, old.title, old.info, old.warning, old.text);
END;
CREATE TRIGGER doc_documentation_au AFTER UPDATE ON doc_documentation BEGIN
  INSERT INTO doc_documentation_idx(doc_documentation_idx, rowid, title, info, warning, text) VALUES('delete', old.id, old.title, old.info, old.warning, old.text);
  INSERT INTO doc_documentation_idx(rowid, title, info, warning, text) VALUES (new.id, new.title, new.info, new.warning, new.text);
END;