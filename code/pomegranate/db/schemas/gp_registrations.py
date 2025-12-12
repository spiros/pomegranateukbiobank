""" SQL schema for the 'gp_registrations' table. """

SCHEMA_GP_REGISTRATIONS = """
DROP TABLE IF EXISTS gp_registrations;
CREATE TABLE IF NOT EXISTS gp_registrations (
    eid INT(7) UNSIGNED,
    data_provider INT(1),
    reg_date DATE,
    deduct_date DATE
);

CREATE INDEX gpreg ON gp_registrations(eid, data_provider);
"""

SCHEMA_GP_REGISTRATIONS_POST_PROCESS = """
UPDATE
    gp_registrations g,
    baseline b
SET
    g.reg_date = STR_TO_DATE(CONCAT(b.value, '-07-01'), '%Y-%m-%d')
WHERE
    YEAR(g.reg_date) IN (1902, 1903)
AND
    g.eid = b.eid
AND
    b.field = 34
AND
    b.i = 0
AND
    b.i = 0;
"""
