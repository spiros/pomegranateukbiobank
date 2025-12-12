""" Script to create and populate the `phenotype_first` table. """

from pomegranate.db.schemas.phenotype_first import SCHEMA_PHENOTYPE_FIRST
from pomegranate.db.schemas.phenotype_first import INDEX_PHENOTYPE_FIRST
from pomegranate.db.schemas.phenotype_first import POST_CREATE_PHENOTYPE_FIRST
from pomegranate.db.schemas.cohort_phenotype_first import SCHEMA_COHORT_PHENOTYPE_FIRST_INDEX

from pomegranate.analytics.cohort_maker import extract_population
from pomegranate.etl_config import NAME_COHORT_EVENTS
from pomegranate.db.ukbdb import UKBDatabase

import pandas as pd 
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%m-%d-%Y %H:%M'
)

Database = UKBDatabase()

logging.info(f"Identifying first events.")

try:
    Database.drop_table_if_exists('phenotype_first')
    n = Database.query(SCHEMA_PHENOTYPE_FIRST).rowcount
    logging.info(f"\tIdentified {n} events.")
    Database.query(INDEX_PHENOTYPE_FIRST)
    logging.info(f"\tGenerating index.")
    Database.query(POST_CREATE_PHENOTYPE_FIRST)
    logging.info(f"\tPost-processing complete.")
except Exception as e:
    print(f"Failed to identify first events: {e}")
finally:
    logging.info(f"Wrote {n} events.")


