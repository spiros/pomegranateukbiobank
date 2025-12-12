""" Configuration for ETL. """

NAME_COHORT_EVENTS = 'cohort_phenotype_first'

COUNTRIES = {
    'E': 'England',
    'S': 'Scotland',
    'W': 'Wales'
}

PRIMARY_CARE_PROVIDERS = {
    1: 'England Vision',
    2: 'Scotland',
    3: 'England TPP',
    4: 'Wales SAIL'
}

PRIMARY_CARE_CENSORING = {
    1: '31-05-2017',
    2: '31-03-2017',
    3: '31-05-2016',
    4: '31-08-2017'
}

# NOTE: England and Wales are now derived from the same source
DEATH_CENSORING = {
    'E': '31-08-2020',
    'W': '31-08-2020',
    'S': '31-08-2020',
}

HOSPITAL_EHR_CENSORING = {
    'E': '30-06-2020',
    'S': '31-08-2016',
    'W': '28-02-2016'
}

CANCER_CENSORING = {
    'E': '31-03-2016',
    'S': '31-10-2015',
    'W': '31-12-2016'
}

EHR_FIELDS = {
    '41202': 'Diagnoses - main ICD10',
    '41204': 'Diagnoses - secondary ICD10',
    '41200': 'Operative procedures - main OPCS4',
    '41240': 'Operative procedures - secondary OPCS4',
    '40001': 'Underlying (primary) cause of death: ICD10',
    '40002': 'Contributory (secondary) causes of death: ICD10',
    '42040': 'GP clinical event records',
    '42039': 'GP prescription records',
    '40006': 'Cancer registry type of cancer ICD-10'
}

STANDARD_FIELDS = {
    20001: 'self reported cancer',
    20002: 'self reported non-cancer',
    20003: 'self report medication',
    20004: 'self report procedure',
    41202: 'primary hosp dx',
    41204: 'secondary hosp dx',
    41200: 'hospital opcs primary',
    41210: 'hospital opcs secondary',
    40001: 'primary death',
    40002: 'secondary death',
    42040: 'gp dx',
    42039: 'gp rx',
    40006: 'cancer registry'
}

# Map individual UKB field_id's to top level source categories
FIELD_MAPS = {
    41202: 'ehr_hospital',
    41204: 'ehr_hospital',
    41200: 'ehr_hospital',
    41240: 'ehr_hospital',
    40001: 'ehr_death',
    40002: 'ehr_death',
    42040: 'ehr_primary_care',
    42039: 'ehr_primary_care',
    40006: 'ehr_cancer'
}

ONT_MAPS = {
    'icd10': [41202, 41204, 40001, 40002],
    'icd10_cancer': [40006],
    'snomed': ['SNOMED-CT'],
    'read': [42040],  # read2 and ctv2 are combined to `read`
    'bnf': [42039],
    'dmd': [42039],
}
