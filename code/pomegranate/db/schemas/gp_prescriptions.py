""" SQL schema for the 'gp_prescriptions' table. """

SCHEMA_GP_PRESCRIPTIONS = """
DROP TABLE IF EXISTS gp_prescriptions;
CREATE TABLE IF NOT EXISTS gp_prescriptions (
    eid INT(7) UNSIGNED,
    data_provider INT(1),
    issue_date DATE,
    read_2 VARCHAR(15),
    bnf_code VARCHAR(155),
    dmd_code VARCHAR(155),
    drug_name VARCHAR(255),
    quantity VARCHAR(255)
);

CREATE INDEX gprx ON gp_prescriptions(eid, data_provider,read_2,bnf_code,dmd_code);
"""
