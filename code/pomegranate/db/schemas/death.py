""" Schema for the 'death' table. """

SCHEMA_DEATH = """
DROP TABLE IF EXISTS death;
CREATE TABLE IF NOT EXISTS death(
  eid INT(7) unsigned,
  ins_index INT(1) UNSIGNED,
  dsource VARCHAR(5),
  source INT(1) UNSIGNED,
  date_of_death DATE
);

CREATE INDEX e ON death(eid);
"""
