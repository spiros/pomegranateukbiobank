""" SQL schema for the 'hesin_diag' table. """

SCHEMA_HESIN_DIAG = """
DROP TABLE IF EXISTS hesin_diag;
CREATE TABLE IF NOT EXISTS hesin_diag(
    eid INT(7) UNSIGNED,
    ins_index INT(5) UNSIGNED,
    arr_index INT(5) UNSIGNED,
    level INT(1) UNSIGNED,
    diag_icd9 CHAR(7),
    diag_icd9_nb CHAR(7),
    diag_icd10 CHAR(7),
    diag_icd10_nb CHAR(7)
);

CREATE INDEX hesr ON hesin_diag(eid, ins_index, level, diag_icd10);
"""
