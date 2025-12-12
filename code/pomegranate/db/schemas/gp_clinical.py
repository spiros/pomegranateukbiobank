""" Schema for the 'gp_clinical' table. """

SCHEMA_GP_CLINICAL = """
DROP TABLE IF EXISTS gp_clinical;
CREATE TABLE IF NOT EXISTS gp_clinical (
    eid INT(7) UNSIGNED,
    data_provider INT(1),
    eventdate DATE,
    read_2 VARCHAR(15),
    read_3 VARCHAR(15),
    value1 VARCHAR(255),
    value2 VARCHAR(255),
    value3 VARCHAR(255),
    read_code VARCHAR(255)
);

CREATE INDEX gpca ON gp_clinical(eid,read_code);
"""
