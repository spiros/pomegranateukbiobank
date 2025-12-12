"""
Script to extract all constituent parts of a phenotype
and store the data in the database for further processing.

Run like extract_phenotype -p COPD
Or to recalculate: extract_phenotype -p COPD --refresh
"""

import argparse

from pomegranate.db.ukbdb import UKBDatabase
from pomegranate.phenotype import Phenotype

import pomegranate.catalogue
import logging

PRESCRIPTIONS = 42039


def field_to_function(phenotype: Phenotype, f, db: UKBDatabase):
    kwargs = {}
    try:
        extraction_func = db.extract_field_map[f]
    except KeyError:
        logging.info(f"Non-standard field {f} in phenotype {phenotype.name}")
        extraction_func = db.extract_field_value
        kwargs["field_id"] = f

    return extraction_func, kwargs


def process_already_extracted(
    phenotype: Phenotype, field_id, db: UKBDatabase, refresh: bool
) -> bool:
    """
    Valid phenotypes are either skipped or deleted (to be re-extracted) if already extracted.
    """

    # Get fields and phenotypes to check if already exist:
    if phenotype.is_biomarker:
        biomarker = BiomarkerPhenotype(phenotype.name)
        f_use, p_list = biomarker.fields_and_phenotypes(db, field_id)
    else:
        f_use = field_id
        p_list = [phenotype.name]

    skip_extracted = False
    processed_phenotypes = db.get_phenotypes_by_field(f_use)
    for p in p_list:
        if p in processed_phenotypes:
            if refresh:
                n = db.delete_phenotype_entries_by_field(phenotype.name, f_use)
                logging.info(
                    f"{phenotype.name} : {f_use} : refresh : deleted {n} data points."
                )
            else:
                skip_extracted = True
                logging.info(f"{phenotype.name} : {f_use} : skip : already extracted.")
                continue

    return skip_extracted


def extract_phenotypes(
    phenotypes_to_process: list[str],
    db: UKBDatabase,
    fields=None,
    refresh: bool = False,
    testing: bool = True,
):
    """
    Extract phenotypes in list `phenotypes_to_process` from database `db`.

    phenotypes_to_process (list[str]): list of phenotype variable names (a.k.a. phenotype stems)
    db (UKBDatabase): uk-biobank database object
    fields (None | list | field):
        if None: extract all fields defined in phenotype yaml
        if list: extract fields in list
        if individual field: extract that field
    refresh (bool): if True, update phenotype table with recalculated phenotypes
    testing (bool): if True, do not write to or delete tables. Instead return recalculated entries.
    """

    insert = not testing
    if testing:
        dfs = ()
    for phenotype_name in phenotypes_to_process:
        phenotype = Phenotype(phenotype_name)

        if phenotype.is_complex:
            logging.info(f"Skipping complex phenotype: {phenotype_name}")
            continue

        # Fields defined for phenotype:
        phenotype_definition_fields = phenotype.get_definition_fields()
        if fields and isinstance(fields, list):
            fields_to_process = fields
        elif fields and not isinstance(fields, list):
            fields_to_process = [fields]
        else:
            fields_to_process = phenotype_definition_fields

        for f in fields_to_process:
            if f in ["SNOMED-CT", PRESCRIPTIONS]:
                logging.warning(
                    f"Extraction not implemented for: field {f} in phenotype {phenotype.name}"
                )
                continue

            logging.info(f"{phenotype_name} : {f} : start.")

            # Skip undefined fields
            if f not in phenotype_definition_fields:
                logging.info(
                    f"{phenotype_name} : {f} : skip, field not defined for phenotype."
                )
                continue

            # Validate fields
            field_definition = phenotype.get_field_definition(f)
            if field_definition is None:
                logging.info(f"{phenotype_name} : {f} : skip, invalid field")
                continue

            # Get already processed fields (and delete if refreshing) if not testing
            if not testing:
                already_extracted = process_already_extracted(phenotype, f, db, refresh)
                if already_extracted:
                    continue

            # Extract:
            extraction_func, kwargs = field_to_function(phenotype, f, db)
            n = extraction_func(
                phenotype=phenotype_name,
                insert=insert,
                **kwargs,
            )
            if insert:
                logging.info(
                    f"{phenotype_name} : {f} : extract : added {n} data points."
                )
            else:
                logging.info(
                    f"Testing {phenotype_name} : {f} : extract : found {len(n)} data points."
                )
                dfs += n
        logging.info(f"Extraction finished for phenotype {phenotype_name}")
    if testing:
        return dfs


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-8s %(message)s",
        datefmt="%m-%d-%Y %H:%M",
    )

    argparser = argparse.ArgumentParser()
    argparser.add_argument("-p", "--phenotype", help="Phenotype stem", required=False)
    argparser.add_argument(
        "-f", "--fields", nargs="+", type=int, help="Fields", required=False
    )
    argparser.add_argument(
        "--refresh",
        action="store_true",
        required=False,
        help="Re-extracts existing fields and phenotypes",
    )
    argparser.add_argument(
        "--testing",
        action="store_true",
        required=False,
        help="In testing mode tables aren't altered and returns df of entries.",
    )
    # TODO: Add a bit that updates all tables based on removed eids. Specifically, weird things will happen if
    # baseline, hesin, hesin_diag, gp_clinical are not updated

    args = argparser.parse_args()
    if args.testing and args.refresh:
        msg = """
        Cannot refresh tables in testing-mode.
        In testing-mode, tables are always re-created but not saved.
        """
        logging.error(msg)

    db = UKBDatabase()

    # Get phenotypes to process:
    phenotypes_to_process = []
    c = pomegranate.catalogue.Catalogue()
    if args.phenotype:
        if c.is_valid_phenotype(args.phenotype) is False:
            raise ValueError(f"Invalid phenotype specified: {args.phenotype}")
        phenotypes_to_process.append(args.phenotype)
    else:
        phenotypes_to_process = c.get_all_phenotypes().variable_name.values

    # Process phenotypes:
    extract_phenotypes(
        phenotypes_to_process, db, args.fields, args.refresh, args.testing
    )
    if not args.testing:
        db.commit()

if __name__ == '__main__':
    main()
