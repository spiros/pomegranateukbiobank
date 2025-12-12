""" A module with general DB configuration parameters. """

from pomegranate.db.schemas.baseline import SCHEMA_BASELINE
from pomegranate.db.schemas.death import SCHEMA_DEATH
from pomegranate.db.schemas.death_cause import SCHEMA_DEATH_CAUSE
from pomegranate.db.schemas.gp_clinical import SCHEMA_GP_CLINICAL
from pomegranate.db.schemas.gp_registrations import SCHEMA_GP_REGISTRATIONS
from pomegranate.db.schemas.gp_prescriptions import SCHEMA_GP_PRESCRIPTIONS
from pomegranate.db.schemas.hesin import SCHEMA_HESIN
from pomegranate.db.schemas.hesin_diag import SCHEMA_HESIN_DIAG
from pomegranate.db.schemas.hesin_oper import SCHEMA_HESIN_OPER

from pomegranate.db.schemas.phenotypes import SCHEMA_PHENOTYPES

DB_TABLES = {
    'baseline': SCHEMA_BASELINE,
    'death': SCHEMA_DEATH,
    'death_cause': SCHEMA_DEATH_CAUSE,
    'hesin': SCHEMA_HESIN,
    'hesin_diag': SCHEMA_HESIN_DIAG,
    'hesin_oper': SCHEMA_HESIN_OPER,
    'gp_registrations': SCHEMA_GP_REGISTRATIONS,
    'gp_prescriptions': SCHEMA_GP_PRESCRIPTIONS,
    'gp_clinical': SCHEMA_GP_CLINICAL,
    'phenotypes': SCHEMA_PHENOTYPES,
}

BASELINE_COHORT_NICENAMES = {
    "f31": "sex",
    "f34": "yob",
    "f52": "mob",
    "f53": "date_assess",
    "f54": "assess_centre",
    "f21003": "age_assess",
    "f189": "depriv",
    "f21001": "bmi",
    "f50": "height",
    "f21002": "weight",
    "f95": "sysbp",
    "f94": "diasbp",
    "f20116": "smoking",
    "f20117": "alcohol",
    "f21000": "ethnic",
    "f40000": "dod",
}

BASELINE_COHORT_FIELD_VALUES = {
    "sex": {"0": "F", "1": "M"},
    "smoking": {"0": "Never", "1": "Ex", "2": "Current"},
    "alcohol": {"0": "Never", "1": "Ex", "2": "Current"},
    "ethnic": {
        "1": "White",
        "2": "Mixed",
        "3": "Asian",
        "4": "Black",
        "5": "Chinese",
        "6": "Other",
    },
}
