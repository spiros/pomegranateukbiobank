""" Schema for the 'baseline_cohort' table. """

SCHEMA_BASELINE_COHORT = """
DROP TABLE IF EXISTS baseline_cohort;
CREATE TABLE baseline_cohort AS
    SELECT
        DISTINCT(eid)
    FROM
        baseline;

CREATE INDEX e ON baseline_cohort(eid);

ALTER TABLE baseline_cohort
    ADD COLUMN f31 VARCHAR(50),
    ADD COLUMN f34 VARCHAR(50),
    ADD COLUMN f52 VARCHAR(50),
    ADD COLUMN f53 VARCHAR(50),
    ADD COLUMN f54 VARCHAR(50),
    ADD COLUMN country CHAR(1),
    ADD COLUMN dob DATE,
    ADD COLUMN f21003 VARCHAR(50),
    ADD COLUMN f189 VARCHAR(50),
    ADD COLUMN f21001 VARCHAR(50),
    ADD COLUMN f50 VARCHAR(50),
    ADD COLUMN f21002 VARCHAR(50),
    ADD COLUMN f95 VARCHAR(50),
    ADD COLUMN f94 VARCHAR(50),
    ADD COLUMN f20116 VARCHAR(50),
    ADD COLUMN f20117 VARCHAR(50),
    ADD COLUMN f21000 VARCHAR(50),
    ADD COLUMN f40000 DATE,
    ADD COLUMN gp_ehr INT(1),
    ADD COLUMN gp_ehr_data_provider INT(1);

UPDATE baseline_cohort c, baseline b
SET c.f31 = b.value
WHERE b.field = 31
AND b.eid = c.eid
AND b.i = 0
AND b.n = 0;

UPDATE baseline_cohort c, baseline b
SET c.f34 = b.value
WHERE b.field = 34
AND b.eid = c.eid
AND b.i = 0
AND b.n = 0;

UPDATE baseline_cohort c, baseline b
SET c.f52 = b.value
WHERE b.field = 52
AND b.eid = c.eid
AND b.i = 0
AND b.n = 0;

UPDATE baseline_cohort c, baseline b
SET c.f53 = b.value
WHERE b.field = 53
AND b.eid = c.eid
AND b.i = 0
AND b.n = 0;

UPDATE baseline_cohort c, baseline b
SET c.f21003 = b.value
WHERE b.field = 21003
AND b.eid = c.eid
AND b.i = 0
AND b.n = 0;

UPDATE baseline_cohort c, baseline b
SET c.f189 = b.value
WHERE b.field = 189
AND b.eid = c.eid
AND b.i = 0
AND b.n = 0;

UPDATE baseline_cohort c, baseline b
SET c.f21001 = b.value
WHERE b.field = 21001
AND b.eid = c.eid
AND b.i = 0
AND b.n = 0;

UPDATE baseline_cohort c, baseline b
SET c.f50 = b.value
WHERE b.field = 50
AND b.eid = c.eid
AND b.i = 0
AND b.n = 0;

UPDATE baseline_cohort c, baseline b
SET c.f21002 = b.value
WHERE b.field = 21002
AND b.eid = c.eid
AND b.i = 0
AND b.n = 0;

UPDATE  baseline_cohort c, baseline b
SET c.f94 = b.value
WHERE b.field = 94
AND b.eid = c.eid
AND b.i = 0
AND b.n = 0;

UPDATE baseline_cohort c, baseline b
SET c.f95 = b.value
WHERE b.field = 95
AND b.eid = c.eid
AND b.i = 0
AND b.n = 0;

UPDATE baseline_cohort c, baseline b
SET c.f20116 = b.value
WHERE b.field = 20116
AND b.eid = c.eid
AND b.i = 0
AND b.n = 0;

UPDATE baseline_cohort c, baseline b
SET c.f20117 = b.value
WHERE b.field = 20117
AND b.eid = c.eid
AND b.i = 0
AND b.n = 0;

UPDATE baseline_cohort c, baseline b
SET c.f21000 = b.value
WHERE b.field = 21000
AND b.eid = c.eid
AND b.i = 0
AND b.n = 0;

UPDATE baseline_cohort c, baseline b
SET c.f54 = b.value
WHERE b.field = 54
AND b.eid = c.eid
AND b.i = 0
AND b.n = 0;

UPDATE baseline_cohort c
SET c.country = IF( -- Glasgow, Edinburgh
                    c.f54 IN (11005, 11004), 'S',
                   -- Cardiff, Swansea, Wrexham
                   IF(c.f54 IN (11003, 11022, 11023), 'W',
                   'E'));

UPDATE baseline_cohort c, baseline b
SET c.f40000 = b.value
WHERE b.field = 40000
AND b.eid = c.eid
AND b.i = 0
AND b.n = 0;

UPDATE baseline_cohort c
SET c.dob = STR_TO_DATE(
    CONCAT(f34, '-', f52, '-', 1),
    '%Y-%m-%d'
);

UPDATE baseline_cohort c, gp_registrations g
SET c.gp_ehr = 1 WHERE c.eid = g.eid;

UPDATE baseline_cohort c, gp_clinical n
SET c.gp_ehr = 1 WHERE c.eid = n.eid;

UPDATE baseline_cohort c, gp_prescriptions p
SET c.gp_ehr = 1 WHERE c.eid = p.eid;

UPDATE baseline_cohort c
SET c.gp_ehr = 0 WHERE c.gp_ehr IS NULL;

UPDATE baseline_cohort c, gp_registrations g
SET c.gp_ehr_data_provider = g.data_provider
WHERE c.eid = g.eid;

UPDATE baseline_cohort c, gp_clinical n
SET c.gp_ehr_data_provider = n.data_provider
WHERE c.eid = n.eid;

UPDATE baseline_cohort c, gp_prescriptions p
SET c.gp_ehr_data_provider = p.data_provider
WHERE c.eid = p.eid;

DROP TABLE IF EXISTS temp_single_reg;

CREATE TABLE temp_single_reg AS
    SELECT eid from gp_registrations g
    GROUP BY g.eid
    HAVING count(*) = 1;

CREATE INDEX temp_r ON temp_single_reg(eid);

ALTER TABLE temp_single_reg
ADD COLUMN gp_ehr_deduct_date DATE;

UPDATE temp_single_reg t, gp_registrations g
SET t.gp_ehr_deduct_date = g.deduct_date
WHERE t.eid = g.eid;

ALTER TABLE baseline_cohort
ADD COLUMN gp_ehr_single_reg int (1) default 0;

ALTER TABLE baseline_cohort
ADD COLUMN gp_ehr_deduct_date DATE;

UPDATE baseline_cohort c, temp_single_reg t
SET c.gp_ehr_single_reg = 1, c.gp_ehr_deduct_date = t.gp_ehr_deduct_date
WHERE c.eid = t.eid;

"""
