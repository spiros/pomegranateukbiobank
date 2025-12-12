"""
Collection of misc helper functions.
"""

import pandas as pd
import numpy as np
from scipy.stats import iqr


def infer_field_info(field_name: str) -> tuple:
    """
    Given a UK Biobank baseline field name, returns
    a list with the field id, the instance and the
    array enumerator.

    '123-1.0' => [123,1,0]

    """

    try:
        field_id, field_instance = field_name.split('.')[0].split('-')
        field_n = field_name.split('.')[1]
    except Exception:
        field_id = field_name.split('-')[0]
        field_instance = 0
        field_n = 0

    return [int(field_id), int(field_instance), int(field_n)]


def describe_values(
        input_values: list,
        minimum: float = None,
        maximum: float = None) -> dict:

    """
    Generate descriptive statistics for a
    list of values.
    """

    output = {
        'count_all': None,
        'count_missing': None,
        'count_invalid': None,
        'min': None,
        'max': None,
        'count_below_min': None,
        'count_above_max': None,
        'decile_10': None,
        'decile_20': None,
        'decile_30': None,
        'decile_40': None,
        'decile_50': None,
        'decile_60': None,
        'decile_70': None,
        'decile_80': None,
        'decile_90': None,
        'median': None,
        'std': None
    }

    output['count_all'] = len(input_values)
    output['count_missing'] = pd.isnull(input_values).sum()

    # convert to numeric, coerce errors to NaN
    input_values = pd.to_numeric(input_values, errors='coerce')
    output['count_invalid'] = pd.isnull(input_values).sum() - output['count_missing']

    # drop missing
    input_values = input_values[np.isfinite(input_values)]

    if len(input_values) == 0:
        return output

    # min max
    output['min'] = min(input_values)
    output['max'] = max(input_values)

    # check lower and upper thresholds
    if minimum is not None:
        output['count_below_min'] = np.sum(input_values < minimum)

    if maximum is not None:
        output['count_above_max'] = np.sum(input_values > maximum)

    # deciles
    for decile in range(10, 100, 10):
        output[f"decile_{decile}"] = np.percentile(input_values, decile)

    # median
    output['median'] = np.median(input_values)

    # sd
    output['std'] = np.std(input_values)

    # IQR
    output['IQR'] = iqr(input_values)

    return output


def word_to_regex(word):
    """
    Regex is looking for a space before word or a phrase that starts with word
    So that e.g. for prednisolone, don't find methylprednisolone.
    """
    return r'\s' + word + '|^' + word
