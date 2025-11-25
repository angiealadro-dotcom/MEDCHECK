-- Migration: Add medication_errors table
CREATE TABLE IF NOT EXISTS medication_errors (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  organization_id INTEGER NOT NULL,
  reported_by_user_id INTEGER NOT NULL,
  checklist_entry_id INTEGER,
  error_type TEXT NOT NULL,
  severity TEXT NOT NULL,
  stage TEXT NOT NULL,
  description TEXT,
  contributing_factors TEXT,
  occurred_at TEXT DEFAULT (datetime('now')),
  detected_at TEXT DEFAULT (datetime('now')),
  resolved INTEGER DEFAULT 0,
  resolution_notes TEXT,
  created_at TEXT DEFAULT (datetime('now')),
  FOREIGN KEY (organization_id) REFERENCES organizations(id),
  FOREIGN KEY (reported_by_user_id) REFERENCES users(id),
  FOREIGN KEY (checklist_entry_id) REFERENCES checklist_entries(id)
);

CREATE INDEX IF NOT EXISTS idx_med_errors_org ON medication_errors(organization_id);
CREATE INDEX IF NOT EXISTS idx_med_errors_occurred ON medication_errors(occurred_at);
CREATE INDEX IF NOT EXISTS idx_med_errors_severity ON medication_errors(severity);
CREATE INDEX IF NOT EXISTS idx_med_errors_type ON medication_errors(error_type);
