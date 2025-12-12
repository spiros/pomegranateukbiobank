""" Schema for the 'phenotypes' table. """

SCHEMA_PHENOTYPES = """
DROP TABLE IF EXISTS phenotypes;
CREATE TABLE IF NOT EXISTS phenotypes(
    eid INT(15),
    phenotype VARCHAR(128),
    field_id INT(10),
    field_value VARCHAR(155),
    eventdate DATE,
    data_value FLOAT
);

CREATE INDEX psf ON phenotypes(phenotype, field_id, eventdate);
"""
