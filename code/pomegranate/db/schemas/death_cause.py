""" Schema for the 'death_cause' table. """

SCHEMA_DEATH_CAUSE = """
DROP TABLE IF EXISTS death_cause;
CREATE TABLE IF NOT EXISTS death_cause(
  eid INT(7) UNSIGNED,
  ins_index INT(1) UNSIGNED,
  arr_index INT(1) UNSIGNED,
  `level` INT(1) UNSIGNED,
  cause_icd10 VARCHAR(5)
);

CREATE INDEX e ON death_cause(eid,level,cause_icd10);
"""
