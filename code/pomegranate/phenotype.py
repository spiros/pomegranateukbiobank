""" A module to abstract phenotypes. """

import pkg_resources
from yaml import load, dump
import os

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

import pandas as pd

from pomegranate.exceptions import GenericException
from pomegranate.error_codes import ErrorCode
from pomegranate.phenotype_config import CODE_FIELDS
from pomegranate.etl_config import STANDARD_FIELDS


class Phenotype:
    """
    Object class for phenotypes providing access to some basic
    functions for introspecting phenotypes.
    """

    def __init__(self, phenotype: str, input_dir=None, db_str: str = 'ukbiobank'):
        """Create a new object."""
        # TODO: Add docstrings

        assert db_str in ['ukbiobank', 'genesandhealth']

        if input_dir is None:
            self.file = pkg_resources.resource_filename(
                "pomegranate.data", f"phenotypes/{db_str}/{phenotype}.yaml"
            )
        # for testing
        else:
            self.file = os.path.join(input_dir, f'{phenotype}.yaml')

        try:
            with open(self.file, "r") as f:
                self.yaml = load(f, Loader=Loader)
        except FileNotFoundError as e:
            not_found_exception = GenericException(ErrorCode.PHENOTYPE_NOT_FOUND, e)
            raise not_found_exception

        for k in self.yaml.keys():
            setattr(self, k, self.yaml[k])
        self.name = self.metadata['variable_name']

        self.prescriptions = self.init_prescriptions()
        self.is_cancer, self.is_biomarker, self.is_complex = self.init_flags()
        self.codes_df = self.get_codes_df()

    def get_codes_df(self):
        columns = list(CODE_FIELDS.keys())
        dfs = []
        for key in self.definitions:
            # skip non-standard or empty fields
            if key not in STANDARD_FIELDS:
                continue
            if len(self.definitions[key]['values']) == 0:
                continue

            df = pd.DataFrame(self.definitions[key]['values'])
            # Add optional columns:
            for col in columns:
                if col not in df.columns:
                    df[col] = [None] * len(df)
            # Add field column
            df['field'] = [key] * len(df)
            dfs.append(df[columns + ['field']])

        return pd.concat(dfs)

    def init_flags(self) -> tuple[bool, bool, bool]:
        # TODO: Indicate biomarkers in YAML metadata  (like is_cancer) instead
        #  of hard-coding:
        BIOMARKER_NAMES = ["HighLDL", "HighTotChol", "HighTrig", "LowHDL"]
        is_biomarker = self.name in BIOMARKER_NAMES

        try:
            is_cancer = bool(int(self.metadata['is_cancer']))
        except KeyError:
            is_cancer = False

        try:
            _ = self.metadata['complex_logic']
            is_complex = True
        except KeyError:
            is_complex = False

        return (is_cancer, is_biomarker, is_complex)

    def init_prescriptions(self) -> list:
        prescription_values = self.get_prescription_values()
        presc_names = ['bnf', 'dmd', 'welsh_read']
        if prescription_values is not None:
            prescriptions = {presc_names[i]: prescription_values[i] for i in range(len(presc_names))}
        else:
            prescriptions = None
        return prescriptions

    def get_definition_fields(self, baseline=False) -> list:
        """
        Returns a list of UK Biobank field
        identifiers which are present in the
        definition file.

        Fields with no values defined (i.e. empty)
        are ommitted.

        if baseline=False don't return baseline fields
        """

        fields_to_ignore = ['limits']
        baseline = 'baseline_fields'
        if not baseline:
            fields_to_ignore += [baseline]
        all_fields = self.definitions.keys()
        output = []

        # adjust to ignore biomarker-specific fields
        fields = [f for f in all_fields if f not in fields_to_ignore]

        for f in fields:
            if f == baseline:
                output.append(f)
            elif len(self.definitions[f]["values"]) > 0:
                output.append(f)

        return output

    def get_field_definition(self, field_id) -> dict:
        """
        Returns a data structure with the definition
        of a field.
        """

        definition_fields = self.get_definition_fields()

        if field_id not in ["SNOMED-CT", 'baseline_fields']:
            field_id = int(field_id)

        if field_id not in definition_fields:
            return None

        return self.definitions[field_id]

    def get_metadata(self) -> dict:
        """
        Returns metadata information for the phenotype.
        """

        return self.metadata

    def get_values_for_field(self, field_id, type: str = "any") -> dict:

        """
        Returns a list of values for a field in the
        phenotype definition.

        The `type` parameter specifies what type of value
        should be returned i.e. 'any', 'prevalent'.
        """

        # skip biomarker fields
        if field_id in ["baseline_fields", "limits"]:
            return None

        if field_id not in ["SNOMED-CT"]:
            field_id = int(field_id)

        field_definition = self.definitions[field_id]
        field_values = field_definition["values"]

        values = [x["code"] for x in field_values if x["type"] == type]

        # For primary care diagnoses, we keep the
        # first five characters of the Read code.
        # For everything else, we remove any dot
        # characters.
        # For example, ICD-10 I44.0 -> I440

        if field_id == 42040:
            values = [x[0:5] for x in values]
        else:
            values = [x.replace(".", "") for x in values]

        return values

    def get_age_field_id(self, field_id):
        field_definition = self.get_field_definition(field_id)
        field_metadata = field_definition["metadata"]
        assert "time_qualifier" in field_metadata
        time_qual_type = field_metadata["time_qualifier"]["type"]
        assert time_qual_type == 'age'
        age_field_id = field_metadata["time_qualifier"]["field_id"]
        return age_field_id

    def get_prescription_values(self, as_codes: bool = True):
        """
        Returns a list of prescription codes per ontology
        """
        field_id = 42039
        if field_id not in self.definitions:
            all_v = []
        else:
            all_v = self.definitions[field_id]["values"]
        if len(all_v) > 0:
            bnf_v = [e for e in all_v if e["ontology"] == "bnf"]
            dmd_v = [e for e in all_v if e["ontology"] == "dmd"]
            read_v = [e for e in all_v if e["ontology"] == "welsh_read"]

            if as_codes:

                def extract_codes(lst):
                    return [x["code"] for x in lst]

                bnf_v = extract_codes(bnf_v)
                dmd_v = extract_codes(dmd_v)
                read_v = extract_codes(read_v)
            return bnf_v, dmd_v, read_v
        else:
            return None
