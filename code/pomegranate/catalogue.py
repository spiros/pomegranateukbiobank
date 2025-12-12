"""
Module for manipulating the phenotype catalogue.
"""

import pkg_resources
import pandas as pd
import os
from yaml import load, dump

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from pomegranate.phenotype_config import METADATA_FIELDS, METADATA_OPTIONAL_FIELDS
from pomegranate.phenotype import Phenotype

# Turn of YAML aliases in PyYAML which forces
# the Dumper to avoid referencing and this way
# values (e.g. ICD-10 codes) are verbatim written
# every time.
# https://stackoverflow.com/questions/13518819/avoid-references-in-pyyaml
Dumper.ignore_aliases = lambda *args: True


class Catalogue:
    """
    Phenotype catalogue class.
    """

    def __init__(self) -> None:
        """
        Creates a new instance of the class.
        """

        # During init, the catalogue loops through all YAML files and
        # loads then in an internal data structure.

        all_phenotypes = [
            os.path.splitext(f)[0]
            for f in pkg_resources.resource_listdir(
                "pomegranate", "data/phenotypes/ukbiobank/"
            )
            if f.endswith(".yaml")
        ]

        df = pd.DataFrame(columns=list(METADATA_FIELDS.keys()))
        for p in all_phenotypes:
            phenotype = Phenotype(p)
            metadata = phenotype.metadata
            row = {}
            for k in METADATA_FIELDS.keys():
                row[k] = [metadata[k]]
            for k in METADATA_OPTIONAL_FIELDS.keys():
                try:
                    row[k] = [metadata[k]]
                except KeyError:
                    row[k] = None
            df = pd.concat([df, pd.DataFrame.from_dict(row)], ignore_index=True)

        self._data = df

    def get_catalogue(self) -> pd.DataFrame:
        """
        Returns a (reference) to a dataframe with the catalogue.
        """

        return self._data

    def get_categories(self) -> list:
        """
        Returns a list of phenotype categories.
        """

        return list(set(self._data.group.values))

    def get_phenotypes_by_category(self, category: str) -> list:
        """
        Returns a list of phenotypes for a given category.
        """

        return self._data[self._data["group"] == category]["variable_name"].values

    def is_valid_phenotype(self, phenotype: str) -> bool:
        """
        Returns True if a given string represents
        a valid phenotype variable name.
        """

        if phenotype not in (self._data.variable_name.values):
            return False
        else:
            return True

    def get_all_phenotypes(
        self,
        include_cancer: bool = True,
        include_neonatal: bool = True,
        include_elix: bool = False,
        include_complex: bool = False,
    ) -> pd.DataFrame:
        """
        Returns a Pandas dataframe of all phenotypes.

        Arguments
        ---------

        include_cancer (Bool) - include cancer phenotypes
                                (default True)
        include_neonatal (Bool) - include neonatal phenotypes
                                 (default False)
        include_elix (Bool) - include Elixhauser comorbidity phenotypes
                                (default False)

        Returns
        -------

        Dataframe (pd.DataFrame)

        """
        # TODO: Add include_biomarker

        df = self._data.copy(deep=True)

        if include_cancer is False:
            df = df[df["is_cancer"] == "0"]

        if include_neonatal is False:
            df = df[df["is_adult"] == "1"]

        if include_elix is True:
            raise NotImplementedError("Elixhauser phenotypes not implemented yet")

        if include_complex is True:
            raise NotImplementedError("Complex phenotypes not implemented yet")

        return df

    def get_phenotype(self, phenotype) -> dict:
        """
        Returns a dictionary containing the catalogue entry
        for a phenotype.
        """

        return self._data[self._data["variable_name"] == phenotype].to_dict("records")[
            0
        ]

    def get_complex_phenotypes(self):
        """
        Returns a list of all complex phenotypes.
        """
        return list(
            self._data[~self._data["complex_logic"].isna()]["variable_name"].values
        )
