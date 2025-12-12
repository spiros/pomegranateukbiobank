""" Schema file for the 'cohort_phenotype_first' table. """

SCHEMA_COHORT_PHENOTYPE_FIRST_MERGE = """
SELECT
    b.eid,
    b.country,
    b.dob,
    b.gp_ehr,
    b.gp_ehr_data_provider,
    b.f31 AS 'sex',
    IF(b.f31 = 0, 'female', 'male') AS 'sex_label',
    b.f53 AS 'date_baseline_assessment',
    b.f54 AS 'AssessmentCentre',
    b.f21003 AS 'age_baseline',
    b.f189 AS 'TownsendIndex',
    b.f21001 AS 'BMI',
    b.f50 AS 'height',
    b.f21002 AS 'weight',
    b.f95 AS 'sys_bp',
    b.f94 AS 'diast_bp',
    b.f20116 AS 'smoking_status',
    b.f20117 AS 'alcohol_status',
    b.f21000 AS 'ethnic_background',
    b.f40000 AS 'death_date',
    f.field_id_label,
    f.phenotype,
    f.field_id,
    f.eventdate
FROM
    baseline_cohort b
LEFT JOIN
    phenotype_first f
ON
    b.eid = f.eid
"""

SCHEMA_COHORT_PHENOTYPE_FIRST_INDEX = """
CREATE INDEX r ON cohort_phenotype_first(eid, phenotype(25), field_id);
"""

SCHEMA_COHORT_PHENOTYPE_FIRST_MERGE_BASIC = """
SELECT
    b.eid,
    b.country,
    b.dob,
    b.gp_ehr,
    b.gp_ehr_data_provider,
    b.gp_ehr_single_reg,
    b.gp_ehr_deduct_date,
    b.f31 AS 'sex',
    IF(b.f31 = 0, 'female', 'male') AS 'sex_label',
    b.f53 AS 'date_baseline_assessment',
    b.f54 AS 'AssessmentCentre',
    b.f21003 AS 'age_baseline',
    b.f40000 AS 'death_date',
    f.field_id_label,
    f.phenotype,
    f.field_id,
    f.eventdate
FROM
    baseline_cohort b
LEFT JOIN
    phenotype_first f
ON
    b.eid = f.eid
"""
