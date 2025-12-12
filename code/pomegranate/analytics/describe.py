""" Module to describe a cohort of patients. """

from tableone import TableOne
import MySQLdb.cursors
import pandas as pd
import numpy as np
from tabulate import tabulate
from datetime import datetime

from pomegranate.db.ukbdb import UKBDatabase
from pomegranate.db.db_config import BASELINE_COHORT_NICENAMES
from pomegranate.db.db_config import BASELINE_COHORT_FIELD_VALUES


def describe_phenotype(phenotype: str) -> str:
    """
    Produces a tabular (text) report of a phenotype
    and the individual components it has
    defined in the main phenotype tables.

    Arguments
    ---------

    phenotype (str): phenotype short name

    Returns
    -------

    summary table (str)

    Example
    -------

    >>> describe_phenotype(phenotype='fatty_liver')
    """

    sql_count_pheno = """
    SELECT COUNT(DISTINCT(eid)) AS n
    FROM phenotypes p
    WHERE p.phenotype=%s
    """

    sql_count_pheno_first = """
    SELECT COUNT(DISTINCT(eid)) AS n
    FROM phenotype_first p
    WHERE p.phenotype=%s
    """

    sql_report_by_field = """
        SELECT
            l.field_id,
            l.title,
            count(distinct(eid)) AS num_patients,
            count(*) AS num_events
        FROM
            lkp_fields l,
            phenotypes p
        WHERE
            l.field_id = p.field_id
        AND
            p.phenotype=%s
        GROUP BY l.field_id, l.title;
    """

    sql_report_by_category = """
    SELECT
        CASE
            WHEN p.field_id IN (41202, 41204, 41200, 41240) THEN 'ehr_hospital'
            WHEN p.field_id IN (40001, 40002) THEN 'ehr_death'
            WHEN p.field_id IN (42040, 42039) THEN 'ehr_primary_care'
            WHEN p.field_id IN (40006) THEN 'ehr_cancer'
            ELSE 'selfreport'
        END AS 'field_id_label',
        COUNT(distinct(eid)) AS num_patients,
        COUNT(*) AS num_events
    FROM
        phenotypes p
    WHERE
        p.phenotype=%s
    GROUP BY field_id_label;
    """

    Database = UKBDatabase(cursorclass=MySQLdb.cursors.DictCursor)
    args = [phenotype]

    try:
        data_by_field = Database.query(sql_report_by_field, args).fetchall()
        data_by_category = Database.query(sql_report_by_category, args).fetchall()
        data_count_pheno = Database.query(sql_count_pheno, args).fetchall()[0]['n']
        data_count_pheno_first = Database.query(sql_count_pheno_first, args).fetchall()[0]['n']
    except Exception as e:
        raise

    report_by_field = tabulate(
        data_by_field,
        tablefmt='grid',
        headers={'field_id': 'field id', 'title': 'title', 'num_events': 'events (n)', 'num_patients': 'unique patients (n)'}
    )

    report_by_category = tabulate(
        data_by_category,
        tablefmt='grid',
        headers={'field_id_label': 'source', 'num_events': 'events (n)', 'num_patients': 'unique patients (n)'}
    )

    report = f"""
Report for phenotype '{phenotype}' - generated {datetime.now()}

Unique patients in 'phenotype' table: {data_count_pheno}
Unique patients in 'phenotype_first' table: {data_count_pheno_first}

1. Phenotype summary by UKB field ('phenotype' table).
{report_by_field}

2. Phenotype summary by top level category ('phenotype' table).
{report_by_category}

Note: the number of unique patients reported in the table is likely to add to a larger number
than the overall number of unique patients reported at the top of the report as patients
can have an event in more than one field or source.
    """

    return report


def describe_cohort(eids: list) -> str:
    """
    Produces a "table 1" descriptive analysis for a given
    cohort of patients.

    Arguments
    ---------

    eids (list): list of UK Biobank eids

    Returns
    -------

    table one summary (str)
    """

    Database = UKBDatabase(cursorclass=MySQLdb.cursors.DictCursor)

    # TODO: move columns to fetch in a config file?
    try:
        cohort_data = Database.get_patient_cohort(eids)
    except Exception:
        raise

    df_cohort = pd.DataFrame(cohort_data)

    # Set nicenames for column names as extracted from the
    # baseline cohort table.

    columns = list(df_cohort.columns)

    for i, c in enumerate(columns):
        if c in BASELINE_COHORT_NICENAMES.keys():
            columns[i] = BASELINE_COHORT_NICENAMES[c]

    df_cohort.columns = columns

    # Replace "-3 Prefer not to answer" with missing
    # for alcohol, smoking
    # http://biobank.ctsu.ox.ac.uk/crystal/coding.cgi?id=90

    for c in ['smoking', 'alcohol']:
        df_cohort[c] = df_cohort[c].replace('-3', np.nan)

    # Recode ethnicity
    # http://biobank.ctsu.ox.ac.uk/crystal/coding.cgi?id=1001
    # Keep only first digit to map to parent nodes
    # 1 White
    # 2 Mixed
    # 3 Asian
    # 4 Black
    # 5 Chinese
    # 6 Other

    df_cohort['ethnic'] = df_cohort['ethnic'].str[0]
    df_cohort['ethnic'] = df_cohort['ethnic'].replace('-3', np.nan)
    df_cohort['ethnic'] = df_cohort['ethnic'].replace('-1', np.nan)

    # Recode all values into something human-friendly
    print(BASELINE_COHORT_FIELD_VALUES)
    df_cohort.replace(BASELINE_COHORT_FIELD_VALUES, inplace=True)

    return _create_table_one(df_cohort)


def _create_table_one(df):
    """
    Internal function, do not use directly.
    """

    col = ['sex', 'age_assess', 'depriv', 'bmi', 'height', 'weight', 'sysbp', 'diasbp', 'smoking', 'ethnic', 'alcohol', 'gp_ehr']
    cat = ['ethnic', 'smoking', 'alcohol']
    groupby = ['sex']

    return TableOne(df, columns=col, categorical=cat, groupby=groupby)
