"""
    Module for date related functions.
    E.g. loading constants (baseline, censoring, DOB, DOD)
    and date-related QC.
"""
from typing import Optional, List
import pandas as pd
from datetime import datetime

from pomegranate.db.ukbdb import UKBDatabase
from pomegranate.etl_config import (
    PRIMARY_CARE_CENSORING,
    HOSPITAL_EHR_CENSORING,
    CANCER_CENSORING,
    DEATH_CENSORING)


def clean_dates_UKB(
    df: pd.DataFrame,
    date_field: str = "eventdate",
    dates: list = ["1900-01-01", "1901-01-01", "2037-07-07"]
) -> pd.DataFrame:
    """
    Returns a DataFrame with rows excluded that have dates specified
    in the `dates` list in the `date_field` column
    of the input DataFrame `df`.

    Parameters
    ----------
    df : pandas.DataFrame
        Input DataFrame to be filtered.
    date_field : str, default 'eventdate'
        Name of the column containing the dates to be excluded.
    dates : list of str,
        default ["1900-01-01", "1901-01-01", "2037-07-07"]
        List of date strings in '%Y-%m-%d' format
        to be excluded from the `date_field` column of `df`.
        UKB uses 1900-01-01 and 1901-01-01 to indicate missing dates.
        UKB uses 2037-07-07 to indicate dates that are not yet known.

    Returns
    -------
    pandas.DataFrame
        A new DataFrame with rows excluded that have dates
        specified in the `dates` list in the `date_field` column
        of the input DataFrame `df`.
    """
    dates = [datetime.strptime(x, "%Y-%m-%d").date() for x in dates]
    df = df[~df[date_field].isin(dates)]
    df = df.reset_index(drop=True)
    return df


def clean_dates_HES(
    df: pd.DataFrame,
    date_fields: list = ["admidate", "disdate", "epistart", "epiend"],
    dates: list = ["1800-01-01", "1801-01-01", "2037-07-07"]
) -> pd.DataFrame:
    """
    Returns a DataFrame with rows excluded that have dates specified
    in the `dates` list in the `date_fields` column
    of the input DataFrame `df`.

    Parameters
    ----------
    df : pandas.DataFrame
        Input DataFrame to be filtered.
    date_fields: list, default ["admidate", "disdate", "epistart", "epiend"]
        List of the columns containing the dates to be excluded.
        Defaults to the four main HES APC dates used.
    dates : list of str,
        default ["1800-01-01", "1801-01-01", "2037-07-07"]
        List of date strings in '%Y-%m-%d' format
        to be excluded from the `date_fields` columns of `df`.
        HES data dictionary:
            1800-01-01 = Null
            1801-01-01 = invalid date submitted
        UK BioBank data dictionary:
            2037-07-07 = Where the date is in the future,
            and is presumed to be a placeholder or other system default

    Returns
    -------
    pandas.DataFrame
        A new DataFrame with rows excluded that have dates
        specified in the `dates` list in the `date_fields` columns
        of the input DataFrame `df`.
    """
    dates = [datetime.strptime(x, "%Y-%m-%d").date() for x in dates]
    for date_field in date_fields:
        try:
            df = df[~df[date_field].isin(dates)]
        except KeyError:
            print(f"Date field '{date_field}' not present in input dataframe")
    df = df.reset_index(drop=True)
    return df


def get_baseline_date(eids: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Returns a DataFrame with the baseline date for each subject.

    Args:
    eids : list of strs, default None
        List of eids to extract.
        If None (default), extracts all eids.

    Returns:
    pd.DataFrame:
        A pandas DataFrame with columns 'eid' and 'date_baseline_assessment'.
    """
    cols = ["eid", "date_baseline_assessment"]
    sql = """
    SELECT
        eid,
        f53 AS 'date_baseline_assessment'
    FROM
        baseline_cohort
    """
    if eids is not None:
        sql += f" WHERE eid IN {tuple(eids)}"
    df = pd.DataFrame(data=UKBDatabase().query(sql).fetchall(), columns=cols)
    df["date_baseline_assessment"] = pd.to_datetime(
        df["date_baseline_assessment"])
    assert len(df) == df.eid.nunique(), AssertionError(
        "There are duplicate eids in the baseline cohort."
    )
    return df


def get_time_since_baseline(
    df: pd.DataFrame,
    id_col: str = "eid",
    date_col: str = "eventdate"
) -> pd.DataFrame:
    """
    This function calculates the number of days
    between a given event date
    and the baseline assessment date
    for each individual in a pandas DataFrame.

    Args:
    df (pd.DataFrame):
        A pandas DataFrame containing the event dates
        and baseline assessment dates for each individual.
    id_col (str, optional):
        The name of the column in df containing the unique identifier
        for each individual. Default is 'eid'.
    date_col (str, optional):
        The name of the column in df containing the event dates
        for each individual. Default is 'eventdate'.

    Returns:
    pd.DataFrame:
        A pandas DataFrame with an additional column named
        'time_since_baseline' that contains the
        number of days between the event date
        and the corresponding individual's baseline assessment date.
    """
    baseline_dates = get_baseline_date()
    df = df.merge(baseline_dates, on=id_col)
    df["time_since_baseline"] = (
        df[date_col] - df["date_baseline_assessment"]
    ).dt.days
    return df


def get_dod(eids: Optional[List[str]] = None,
            drop_alive: bool = True) -> pd.DataFrame:
    """
    Returns a DataFrame with the death date for each subject.
    This is derived from the baseline_cohort table, rather than raw deaths.

    Args:
    eids : list of strs, default None
        List of eids to extract.
    drop_alive : bool, default True
        If True (default), drops subjects with missing death dates.

    Returns:
    pd.DataFrame:
        A pandas DataFrame with columns 'eid' and 'dod'.

    """
    cols = ["eid", "dod"]
    sql = """
    SELECT
        eid,
        f40000 AS 'dod'
    FROM
        baseline_cohort
    """
    if eids is not None:
        sql += f" WHERE eid IN {tuple(eids)}"

    df = pd.DataFrame(data=UKBDatabase().query(sql).fetchall(), columns=cols)
    df["dod"] = pd.to_datetime(df["dod"])
    assert len(df) == df.eid.nunique(), AssertionError(
        "There are duplicate eids in the baseline_cohort."
    )
    if drop_alive:
        df = df.loc[~df.dod.isna()]
    return df


def get_dob(eids: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Returns a DataFrame with the date of birth for each subject.
    This is derived from the baseline_cohort table.

    Args:
    eids : list of strs, default None
        List of eids to extract.
        If None (default), extracts all eids.

    Returns:
    pd.DataFrame:
        A pandas DataFrame with columns 'eid' and 'dob'.
    """
    cols = ["eid", "dob"]
    sql = """
    SELECT
        eid,
        dob
    FROM
        baseline_cohort
    """
    if eids is not None:
        sql += f" WHERE eid IN {tuple(eids)}"

    df = pd.DataFrame(data=UKBDatabase().query(sql).fetchall(), columns=cols)
    df["dob"] = pd.to_datetime(df["dob"])
    assert len(df) == df.eid.nunique(), AssertionError(
        "There are duplicate eids in baseline_cohort."
    )
    return df


def get_phenotype_first(phenotypes: Optional[List[str]] = None,
                        fields: Optional[List[str]] = None,
                        first_only: bool = True,
                        limit: Optional[int] = None
                        ) -> pd.DataFrame:
    """
    Returns a DataFrame with the first recorded date for each phenotype.

    Args:
    phenotypes : list of str, default None
        List of phenotype names to extract.
        If None (default), extracts all phenotypes.
    fields : list of str, default None
        List of field IDs to extract.
        If None (default), extracts all fields.
    first_only : bool, default True
        If True (default), returns only the first eventdate,
        for each eid/phenotype.
    limit : int, default None
        Limit the number of rows returned by SQL query.
        If None (default), returns all rows.

    Returns:
    pd.DataFrame:
        A pandas DataFrame with columns 'eid', 'phenotype', 'eventdate',
        and 'field_id'.
    """
    # Coerce to list if single string
    if isinstance(phenotypes, str):
        phenotypes = [phenotypes]
    cols = ['eid', 'phenotype', 'eventdate', 'field_id']
    sql = f"""
    SELECT
        {','.join(cols)}
    FROM
        phenotype_first
    """
    if phenotypes is None:
        print('No phenotypes specified, returning ALL phenotypes!')
    elif len(phenotypes) == 1:
        sql += f" WHERE phenotype = '{phenotypes[0]}'"
    else:
        sql += f" WHERE phenotype IN {tuple(phenotypes)}"
    if fields is not None:
        if phenotypes is None:
            sql += " WHERE"
        else:
            sql += " AND"
        sql += f" field_id IN {tuple(fields)}"
    if limit is not None:
        print(f"""
              Limiting SQL query to {limit} rows
              (may return fewer due to duplicate dates or different fields)
              """)
        sql += f" LIMIT {limit}"
    df = pd.DataFrame(
        data=UKBDatabase().query(sql).fetchall(),
        columns=cols
    )
    df = clean_dates_UKB(df)
    df['eventdate'] = pd.to_datetime(df['eventdate'])
    if first_only:
        print("filtering to first eventdate for each eid/phenotype")
        df = df.loc[df.groupby(['eid', 'phenotype'])['eventdate'].idxmin()]
        assert df.groupby(['eid', 'phenotype']).size().max() == 1, ValueError()
    return df


def get_min_censor_date() -> pd.Timestamp:
    """
    Returns the minimum censoring date across all data sources and providers.
    References:
        pomegranate.etl_config
        analytics.cohort_maker extract_population()

    Returns:
    pd.Timestamp:
        The minimum censoring date across all data sources and providers.
    """
    MIN_CENSORING_DATE = min(
        min(PRIMARY_CARE_CENSORING.values()),
        min(HOSPITAL_EHR_CENSORING.values()),
        min(CANCER_CENSORING.values()),
        min(DEATH_CENSORING.values())
    )
    # format 28-02-2016
    MIN_CENSORING_DATE = pd.to_datetime(MIN_CENSORING_DATE,
                                        format="%d-%m-%Y")
    return MIN_CENSORING_DATE


# TODO: add individualised censoring dates accounting for different providers
# See: analytics.cohort_maker extract_population() for censor date logic
