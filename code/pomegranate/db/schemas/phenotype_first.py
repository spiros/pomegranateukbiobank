""" Schema file for the 'phenotype_first' table. """

# TODO: Move field id labels to configuration file

SCHEMA_PHENOTYPE_FIRST = """
CREATE TABLE phenotype_first AS
SELECT
    p.eid,
    p.phenotype,
    p.field_id,
    CASE
        WHEN p.field_id IN (41202, 41204, 41200, 41240) THEN 'ehr_hospital'
        WHEN p.field_id IN (40001, 40002) THEN 'ehr_death'
        WHEN p.field_id IN (42040, 42039) THEN 'ehr_primary_care'
        WHEN p.field_id IN (40006) THEN 'ehr_cancer'
        ELSE 'selfreport'
    END AS 'field_id_label',
    MIN(p.eventdate) AS eventdate
FROM
    phenotypes p,
    baseline_cohort b
WHERE p.eid = b.eid
GROUP BY p.eid, p.phenotype, p.field_id;
"""

INDEX_PHENOTYPE_FIRST = """
CREATE INDEX r ON phenotype_first(eid, phenotype, field_id);
"""

POST_CREATE_PHENOTYPE_FIRST = """
UPDATE
  baseline_cohort b,
  phenotype_first p
SET p.eventdate = b.dob
WHERE b.eid = p.eid
AND p.eventdate <= b.dob
AND p.eventdate NOT IN ('1900-01-01', '1901-01-01');
"""
