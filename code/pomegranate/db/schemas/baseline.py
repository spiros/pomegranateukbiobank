""" Schema for the 'baseline' table. """

SCHEMA_BASELINE = """
DROP TABLE IF EXISTS baseline;
CREATE TABLE IF NOT EXISTS baseline(
    eid INT,
    field INT(5),
    i INT(2),
    n INT(2),
    value TEXT
);

CREATE INDEX b ON baseline(eid,field,i,n);
"""
