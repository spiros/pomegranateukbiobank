"""A module for UK Biobank specific functions."""

import logging

import pandas as pd
from pomegranate.db.mysql import MySQLDatabase
from pomegranate.phenotype import Phenotype


class UKBDatabase(MySQLDatabase):
    """
    Collection of UK Biobank specific queries.
    """

    def __init__(self, **kwargs):
        MySQLDatabase.__init__(self, **kwargs)

        self.extract_field_map = {
            20001: self.extract_cancer_self_report,
            20002: self.extract_non_cancer_self_report,
            20004: self.extract_procedures_self_report,
            41200: self.extract_hospital_primary_procedures,
            41210: self.extract_hospital_secondary_procedures,
            41202: self.extract_all_hospital_primary_diagnoses,
            41204: self.extract_all_hospital_secondary_diagnoses,
            40001: self.extract_primary_mortality,
            40002: self.extract_secondary_mortality,
            42040: self.extract_all_primary_care_diagnoses,
            40006: self.extract_cancer_registry_data,
        }

    @staticmethod
    def list_to_sql(lst: list[str]) -> str:
        return "(" + ",".join([f"'{x}'" for x in lst]) + ")"

    def query_insert(self, sql_list: list[str], table: str, insert=False):
        """
        Adds 'INSERT INTO' if insert==True, to insert sql output into table and
        returns either rowcount (if insert) or all entries.
        """

        if insert is True:
            sql_list = ["INSERT INTO {table} " + sql for sql in sql_list]
            return sum([self.query(sql).rowcount for sql in sql_list])
        else:
            return sum([self.query(sql).fetchall() for sql in sql_list], ())

    def get_individuals_by_phenotype(self, phenotype_name: str) -> set:
        """
        Gets a set of identifiers (eids) in phenotype table with phenotype `phenotype_name`.
        """

        sql = f"""
        SELECT DISTINCT(eid)
        FROM phenotypes
        WHERE phenotype='{phenotype_name}';
        """

        return set([x[0] for x in self.query(sql).fetchall()])

    def get_phenotype_entries(self):
        """
        Return all entries from the `phenotype` table.
        """

        sql = """
            SELECT DISTINCT(phenotype) FROM phenotypes
        """

        r = self.query(sql, [])
        return [x[0] for x in r]

    def get_phenotypes_by_field(self, field_id: int):
        """
        Return all entries from the `phenotype` table
        by field.
        """

        sql = f"""
            SELECT DISTINCT(phenotype) FROM phenotypes
            WHERE field_id = {field_id}
        """

        r = self.query(sql)
        return [x[0] for x in r]

    def get_phenotype_events_by_field(
        self, field_ids: list[int] = None, phenotypes: list[str] = None
    ):
        """
        Return all entries from the `phenotype` table
        by field, optionally limiting to a phenotype string.

        Useful for testing extract_phenotype.py
        """

        sql = "SELECT * FROM phenotypes"

        if field_ids is not None:
            sql += f" WHERE field_id IN {UKBDatabase.list_to_sql(field_ids)}"

        if phenotypes is not None:
            if "WHERE" in sql:
                sql += f" AND phenotype IN {UKBDatabase.list_to_sql(phenotypes)}"
            else:
                sql += f" WHERE phenotype IN {UKBDatabase.list_to_sql(phenotypes)}"
        sql += ";"

        return self.query(sql).fetchall()

    def delete_phenotype_from_table(self, phenotype: str, table: str):
        """
        Deletes all entries for phenotype `phenotype` in table `table`.

        phenotype (str): variable_name/phenotype stem, e.g. 'AECOPD'
        table (str): table name, e.g. `complex_phenotypes`
        """
        sql = f"""
        SELECT COUNT(phenotype) FROM {table} WHERE phenotype='{phenotype}';
        """
        num_lines = self.query(sql).fetchall()[0][0]

        sql2 = f"""
        DELETE FROM {table} WHERE phenotype='{phenotype}';
        """
        self.query(sql2)
        logging.info(
            f"Deleted {num_lines} lines from table '{table}' where phenotype='{phenotype}'."
        )

        # using phenotype instead of * just for speed
        sql3 = f"""
        SELECT COUNT(phenotype) FROM {table};
        """
        logging.info(f"Lines remaining in {table}: {self.query(sql3).fetchall()[0][0]}")

    def delete_phenotype_entries_by_field(self, phenotype: str, field_id: int):
        """
        Delete all entries in the `phenotype` table for a given
        phenotype by field.
        """

        sql = """
            DELETE FROM phenotypes WHERE
            field_id = %s
            AND phenotype = %s
        """

        self.query(sql, [field_id, phenotype])

        return self.cursor.rowcount

    def extract_field_value(self, phenotype: str, field_id, insert: bool):
        """
        For non-standard fields
        # TODO: Write better docstring
        """
        field_metadata = Phenotype(phenotype).get_field_definition(field_id)["metadata"]

        assert "time_qualifier" in field_metadata
        time_qual_type = field_metadata["time_qualifier"]["type"]
        assert time_qual_type in ["age", "baseline"]
        logging.info(f"Time qualifier: {time_qual_type}")

        if time_qual_type == "age":
            n = self.extract_field_value_with_age_qualifier(
                phenotype=phenotype,
                field_id=field_id,
                insert=insert,
            )
        elif time_qual_type == "baseline":
            n = self.extract_field_value_with_baseline_qualifier(
                phenotype=phenotype, field_id=field_id, insert=insert
            )
        return n

    def extract_field_value_with_baseline_qualifier(
        self, phenotype: str, field_id: int, values: list = None, **kwargs
    ):
        """
        Extract baseline information for a particular field
        from the `baseline` table using the baseline visit
        as the event date.

        The _eventdate_ associated with the phenotype is set to
        the date of the _first_ visit to the assessment centre.
        """

        insert = kwargs.get("insert", False)
        if not values:
            values = Phenotype(phenotype).get_values_for_field(field_id)

        sql = f"""
        SELECT
            b1.eid,
            '{phenotype}' AS 'phenotype',
            {field_id} AS 'field_id',
            b1.value AS field_value,
            STR_TO_DATE(b2.value, '%Y-%m-%d') AS eventdate,
            NULL as data_value
        FROM
            baseline b1
        LEFT JOIN baseline b2
            ON b2.eid = b1.eid
            AND b2.i = 0
            AND b2.n = 0
            AND b2.field = 53
        WHERE
            b1.value IN {UKBDatabase.list_to_sql(values)}
        AND
            b1.field = {field_id}
        """

        return self.query_insert([sql], "phenotypes", insert)

    def extract_field_value_with_date_qualifier(
        self, phenotype: str, field_id: int, values: list, date_field_id: int, **kwargs
    ):
        """
        Extract baseline information for a particular field
        from the `baseline` table using a date qualified field.
        """

        insert = kwargs.get("insert", False)

        sql = f"""
        SELECT
            b1.eid,
            '{phenotype}' AS 'phenotype',
            {field_id} AS 'field_id',
            b1.value AS field_value,
            IF (
                b2.value > 0,
                STR_TO_DATE(CONCAT(ROUND(b2.value),'-01-01'), "%Y-%m-%d"),
                STR_TO_DATE('1900-01-01', "%Y-%m-%d")
            ) AS eventdate,
            NULL as data_value
        FROM
             baseline b1
        LEFT OUTER JOIN baseline b2
            ON b2.eid = b1.eid
            AND b2.i = b1.i
            AND b2.n = b1.n
            AND b2.field = {date_field_id}
        WHERE
            b1.value IN {UKBDatabase.list_to_sql(values)}
        AND
            b1.field = {field_id}
        """

        return self.query_insert([sql], "phenotypes", insert)

    def extract_field_value_with_age_qualifier(
        self,
        phenotype: str,
        field_id: int,
        values: list = None,
        age_field_id: int = None,
        **kwargs,
    ):
        """
        Extract baseline information for a particular field
        from the `baseline` table using a age qualified field.
        """
        insert = kwargs.get("insert", False)
        phen = Phenotype(phenotype)
        if not values:
            values = phen.get_values_for_field(field_id)
        if not age_field_id:
            age_field_id = phen.get_age_field_id(field_id)

        sql = f"""
        SELECT
            b1.eid,
            '{phenotype}' AS 'phenotype',
            {field_id} AS 'field_id',
            b1.value AS field_value,
            IF (
                b2.value > 0,
                STR_TO_DATE(CONCAT(ROUND(b2.value+b3.value),'-01-01'), '%Y-%m-%d'),
                STR_TO_DATE('1900-01-01', '%Y-%m-%d')
            ) AS eventdate,
            NULL as data_value
        FROM
             baseline b1
        LEFT OUTER JOIN baseline b2
            ON b2.eid = b1.eid
            AND b2.i = b1.i
            AND b2.n = b1.n
            AND b2.field = {age_field_id}
        LEFT OUTER JOIN baseline b3
            ON b3.eid = b1.eid
            AND b3.i = 0
            AND b3.n = 0
            AND b3.field = 34
        WHERE
            b1.value IN {UKBDatabase.list_to_sql(values)}
        AND
            b1.field = {field_id}
        """

        return self.query_insert([sql], "phenotypes", insert)

    def extract_field_value_without_date_qualifier(
        self, phenotype: str, field_id: int, values: list, **kwargs
    ):
        """
        Extract baseline information for a particular field
        from the `baseline` table without a date qualified field.
        """

        insert = kwargs.get("insert", False)

        sql = f"""
        SELECT
            b1.eid,
            '{phenotype}' AS 'phenotype',
            {field_id} AS 'field_id',
            b1.value AS field_value,
            NULL AS eventdate,
            NULL as data_value
        FROM
            baseline b1
        WHERE
            b1.value IN {UKBDatabase.list_to_sql(values)}
        AND
            b1.field = {field_id}
        """

        return self.query_insert([sql], "phenotypes", insert)

    def extract_cancer_registry_data(
        self,
        phenotype: str,
        field_id: int = 40006,
        values: list = None,
        date_field_id: int = 40005,
        **kwargs,
    ):
        """
        Exract cancer registry data from the `baseline`
        table.
        """

        insert = kwargs.get("insert", False)
        if not values:
            values = Phenotype(phenotype).get_values_for_field(field_id)

        placeholders = "|".join(values)

        sql = """
        SELECT
            b1.eid,
            '%s' AS 'phenotype',
            '%s' AS 'field_id',
            b1.value AS field_value,
            b2.value AS eventdate,
            NULL as data_value
        FROM
             baseline b1
        LEFT OUTER JOIN baseline b2
            ON b2.eid = b1.eid
            AND b2.i = b1.i
            AND b2.n = b1.n
            AND b2.field = %s
        WHERE
            b1.value REGEXP '^(%s)'
        AND
            b1.field = %s
        """ % (
            phenotype,
            field_id,
            date_field_id,
            placeholders,
            field_id,
        )

        return self.query_insert([sql], "phenotypes", insert)

    def extract_non_cancer_self_report(
        self, phenotype: str, values: list = None, **kwargs
    ):
        """
        Extract non-cancer self report data from the `baseline` table.
        """

        insert = kwargs.get("insert", False)
        field = 20002
        if not values:
            values = Phenotype(phenotype).get_values_for_field(field)
        logging.info(
            f"Extracting {len(values)} values from phenotype {phenotype} with field {field}."
        )

        return self.extract_field_value_with_date_qualifier(
            phenotype=phenotype,
            field_id=field,
            values=values,
            date_field_id=20008,
            insert=insert,
        )

    def extract_procedures_self_report(
        self, phenotype: str, values: list = None, **kwargs
    ):
        """
        Extract self report procedure information
        from the `baseline` table. More information can be found
        on the Showcase: https://biobank.ctsu.ox.ac.uk/crystal/label.cgi?id=100076
        """

        insert = kwargs.get("insert", False)
        field = 20004
        if not values:
            values = Phenotype(phenotype).get_values_for_field(field)
        logging.info(
            f"Extracting {len(values)} values from phenotype {phenotype} with field {field}."
        )

        return self.extract_field_value_with_date_qualifier(
            phenotype=phenotype,
            field_id=field,
            values=values,
            date_field_id=20010,
            insert=insert,
        )

    def extract_cancer_self_report(self, phenotype: str, values: list = None, **kwargs):
        """
        Extract cancer self report data from the `baseline` table.
        """

        insert = kwargs.get("insert", False)
        field = 20001
        if not values:
            values = Phenotype(phenotype).get_values_for_field(field)
        logging.info(
            f"Extracting {len(values)} values for phenotype {phenotype} and field {field}."
        )

        return self.extract_field_value_with_date_qualifier(
            phenotype=phenotype,
            field_id=field,
            values=values,
            date_field_id=20006,
            insert=insert,
        )

    def extract_all_hospital_primary_diagnoses(self, phenotype: str, **kwargs):
        """
        Extracts all primary hospital diagnoses: both prevalent and incident
        """
        field = 41202  # Diagnoses - main ICD10
        insert = kwargs.get("insert", False)
        n = 0 if insert else ()

        pheno = Phenotype(phenotype)
        incident_field_values = pheno.get_values_for_field(field)
        if len(incident_field_values) > 0:
            n += self.extract_hospital_primary_diagnoses(
                phenotype=phenotype,
                values=incident_field_values,
                prevalent=False,
                **kwargs,
            )

        prevalent_field_values = pheno.get_values_for_field(field, type="prevalent")
        if len(prevalent_field_values) > 0:
            n += self.extract_hospital_primary_diagnoses(
                phenotype=phenotype,
                values=prevalent_field_values,
                prevalent=True,
                **kwargs,
            )

        return n

    def extract_all_hospital_secondary_diagnoses(self, phenotype: str, **kwargs):
        """
        Extracts all secondary hospital diagnoses: both prevalent and incident
        """

        field = 41204  # Diagnoses - secondary ICD10
        insert = kwargs.get("insert", False)
        n = 0 if insert else ()

        phen = Phenotype(phenotype)
        incident_field_values = phen.get_values_for_field(field)
        if len(incident_field_values) > 0:
            n += self.extract_hospital_secondary_diagnoses(
                phenotype=phenotype,
                values=incident_field_values,
                prevalent=False,
                **kwargs,
            )

        prevalent_field_values = phen.get_values_for_field(field, type="prevalent")

        if len(prevalent_field_values) > 0:
            n += self.extract_hospital_secondary_diagnoses(
                phenotype=phenotype,
                values=prevalent_field_values,
                prevalent=True,
                **kwargs,
            )
        return n

    def extract_hospital_primary_diagnoses(
        self, phenotype: str, values: list, prevalent: bool = False, **kwargs
    ):
        """
        Return (or insert) all hospital EHR primary
        diagnoses records for a given phenotype and
        the specified ICD codes.

        Events will be recorded using the date of admission
        if its not missing and the date of the start of the
        episode if the date of admission is missing.

        Input
        -----

        phenotype (str) = name of phenotype
        icd_codes (list) = list of ICD-10 codes
        insert (boolean) = set to True if records
        to be inserted in the 'phenotypes' table.

        Returns
        -------

        n (int) = affected rows if insert == True
        """

        insert = kwargs.get("insert", False)

        date_column = """
                IF(
                    hi.admidate IS NOT NULL,
                    hi.admidate,
                    hi.epistart
                ) AS eventdate
        """

        if prevalent is True:
            date_column = 'STR_TO_DATE("1900-01-01", "%Y-%m-%d") AS eventdate'

        sql = """
          SELECT
                hi.eid,
                '%s' AS 'phenotype',
                41202 AS 'field',
                hd.diag_icd10 AS field_value,
                %s,
                NULL as data_value
            FROM
                hesin hi,
                hesin_diag hd
            WHERE
                hi.eid = hd.eid
            AND
                hi.ins_index = hd.ins_index
            AND
                hd.level = 1
            AND
                hd.diag_icd10 REGEXP '^(%s)' """ % (
            phenotype,
            date_column,
            "|".join(values),
        )

        return self.query_insert([sql], "phenotypes", insert)

    # TODO: refactor this now that new HES data have all info in one table.
    def extract_hospital_secondary_diagnoses(
        self, phenotype: str, values: list, prevalent: bool = False, **kwargs
    ):
        """
        Return (or insert) all hospital EHR secondary
        diagnoses records for a given phenotype and
        the specified ICD codes.

        Input
        -----

        phenotype (str) = name of phenotype
        icd_codes (list) = list of ICD-10 codes
        insert (boolean) = set to True if records to be
                           inserted in the 'phenotypes'
                           table.

        Returns
        -------

        n (int) = affected rows if insert == True
        """

        insert = kwargs.get("insert", False)

        date_column = """
                IF(
                    hi.admidate IS NOT NULL,
                    hi.admidate,
                    hi.epistart
                ) AS eventdate
        """

        if prevalent is True:
            date_column = "STR_TO_DATE('1900-01-01', '%Y-%m-%d') AS eventdate"

        sql = """
          SELECT
                hi.eid,
                '%s' AS 'phenotype',
                41204 AS 'field',
                hd.diag_icd10 AS field_value,
                %s,
                NULL as data_value
            FROM
                hesin hi,
                hesin_diag hd
            WHERE
                hi.eid = hd.eid
            AND
                hi.ins_index = hd.ins_index
            AND
                hd.level = 2
            AND
                hd.diag_icd10 REGEXP '^(%s)' """ % (
            phenotype,
            date_column,
            "|".join(values),
        )

        return self.query_insert([sql], "phenotypes", insert)

    def extract_hospital_primary_procedures(
        self, phenotype: str, values: list = None, **kwargs
    ):
        """
        Return (or insert) all hospital EHR primary
        procedure records for a given phenotype and
        the specified OPCS codes.

        Input
        -----

        phenotype (str) = name of phenotype
        opcs_codes (list) = list of OPCS-4 codes
        insert (boolean) = set to True if records
        to be inserted in the 'phenotypes' table.

        Returns
        -------

        n (int) = affected rows if insert == True
        """

        insert = kwargs.get("insert", False)
        field = 41200
        if not values:
            values = Phenotype(phenotype).get_values_for_field(field)
        logging.info(
            f"Extracting {len(values)} values from phenotype {phenotype} with field {field}."
        )

        sql = """
          SELECT
                ho.eid,
                '%s' AS 'phenotype',
                41200 AS 'field_id',
                ho.oper4 AS field_value,
                COALESCE(
                    ho.opdate,
                    hi.admidate,
                    hi.epistart,
                    STR_TO_DATE('1900-01-01', '%%Y-%%m-%%d')
                ) AS eventdate,
                NULL as data_value
            FROM
                hesin hi,
                hesin_oper ho
            WHERE
                hi.eid = ho.eid
            AND
                hi.ins_index = ho.ins_index
            AND
                ho.level = 1
            AND
                ho.oper4 REGEXP '^(%s)' """ % (
            phenotype,
            "|".join(values),
        )

        return self.query_insert([sql], "phenotypes", insert)

    def extract_hospital_secondary_procedures(
        self, phenotype: str, values: list = None, **kwargs
    ):
        """
        Return (or insert) all hospital EHR secondary
        diagnoses records for a given phenotype and
        the specified ICD codes.

        Input
        -----

        phenotype (str) = name of phenotype
        opcs_codes (list) = list of OPCS-4 codes
        insert (boolean) = set to True if records to be
                           inserted in the 'phenotypes'
                           table.

        In the event that the date of operation in the secondary
        operations table `hesin_oper` is missing, the date will
        be set using the date of operation from the main admission
        table `hesin`. If that is also missing, use the date of
        episode `epistart` from the `hesin` table.

        Returns
        -------

        n (int) = affected rows if insert == True
        """

        insert = kwargs.get("insert", False)
        field = 41210
        if not values:
            values = Phenotype(phenotype).get_values_for_field(field)

        sql = """
          SELECT
                ho.eid,
                '%s' AS 'phenotype',
                41210 AS 'field_id',
                ho.oper4 AS field_value,
                COALESCE(
                    ho.opdate,
                    hi.admidate,
                    hi.epistart,
                    STR_TO_DATE('1900-01-01', '%%Y-%%m-%%d')
                ) AS eventdate,
                NULL as data_value
            FROM
                hesin hi,
                hesin_oper ho
            WHERE
                hi.eid = ho.eid
            AND
                hi.ins_index = ho.ins_index
            AND
                ho.level = 2
            AND
                ho.oper4 REGEXP '^(%s)' """ % (
            phenotype,
            "|".join(values),
        )

        return self.query_insert([sql], "phenotypes", insert)

    def extract_primary_mortality(self, phenotype: str, values: list = None, **kwargs):
        """
        More info: http://biobank.ctsu.ox.ac.uk/crystal/label.cgi?id=100093
        """

        insert = kwargs.get("insert", False)
        field = 40001
        if not values:
            values = Phenotype(phenotype).get_values_for_field(field)

        sql = """
            SELECT
                b1.eid,
                '%s'             AS 'phenotype',
                40001            AS 'field_id',
                b2.cause_icd10   AS field_value,
                b1.date_of_death AS eventdate,
                NULL as data_value
            FROM
                death b1,
                death_cause b2
            WHERE
                b1.eid = b2.eid
            AND
                b2.level = 1
            AND
                b2.cause_icd10 REGEXP '^(%s)'
            """ % (
            phenotype,
            "|".join(values),
        )

        return self.query_insert([sql], "phenotypes", insert)

    def extract_secondary_mortality(
        self, phenotype: str, values: list = None, **kwargs
    ):
        """
        More info: http://biobank.ctsu.ox.ac.uk/crystal/label.cgi?id=100093
        """

        insert = kwargs.get("insert", False)
        field = 40002
        if not values:
            values = Phenotype(phenotype).get_values_for_field(field)

        sql = """
            SELECT
                b1.eid,
                '%s'             AS 'phenotype',
                40002            AS 'field_id',
                b2.cause_icd10   AS field_value,
                b1.date_of_death AS eventdate,
                NULL as data_value
            FROM
                death b1,
                death_cause b2
            WHERE
                b1.eid = b2.eid
            AND
                b2.level = 2
            AND
                b2.cause_icd10 REGEXP '^(%s)'
            """ % (
            phenotype,
            "|".join(values),
        )

        return self.query_insert([sql], "phenotypes", insert)

    def extract_all_primary_care_diagnoses(self, phenotype: str, **kwargs):
        """
        For biomarkers, extracts biomarker.
        For non-biomarkers, extracts incident and prevalent primary care diagnoses.
        """

        gp_field = 42040
        insert = kwargs.get("insert", False)
        n = 0 if insert else ()
        phen = Phenotype(phenotype)

        if phen.is_biomarker:
            biomarker = BiomarkerPhenotype(phenotype)
            n += self.extract_biomarker(biomarker, insert)
        else:
            incident_field_values = phen.get_values_for_field(gp_field)
            logging.info(
                f"""Found {len(incident_field_values)} incident field value(s)
                for phenotype {phenotype} in field {gp_field}."""
            )
            if len(incident_field_values) > 0:
                n += self.extract_incident_primary_care_diagnoses(
                    phenotype=phenotype, values=incident_field_values, **kwargs
                )

            prevalent_field_values = phen.get_values_for_field(
                gp_field, type="prevalent"
            )
            logging.info(
                f"""Found {len(prevalent_field_values)} prevalent field value(s)
                for phenotype {phenotype} in field {gp_field}."""
            )
            if len(prevalent_field_values) > 0:
                n += self.extract_prevalent_primary_care_diagnoses(
                    phenotype=phenotype, values=prevalent_field_values, **kwargs
                )

        return n

    def extract_prevalent_primary_care_diagnoses(
        self, phenotype: str, values: list, **kwargs
    ):
        """
        Return (or insert) all GP EHR clinical data
        for a given phenotype and the given read codes.

        Input
        -----

        phenotype (str) = name of phenotype
        read_codes (list) = list of Read codes
        insert (boolean) = set to True if records
        to be inserted in the 'phenotypes' table.

        Returns
        -------

        n (int) = affected rows if insert == True
        """

        insert = kwargs.get("insert", False)

        sql = f"""
            SELECT
                eid,
                '{phenotype}' AS 'phenotype',
                42040 AS 'field_id',
                read_code AS field_value,
                STR_TO_DATE('1900-01-01', '%Y-%m-%d') AS eventdate,
                NULL as data_value
            FROM
                gp_clinical
            WHERE
                read_code IN {UKBDatabase.list_to_sql(values)};
            """

        return self.query_insert([sql], "phenotypes", insert)

    def extract_incident_primary_care_diagnoses(
        self, phenotype: str, values: list, **kwargs
    ):
        """
        Return (or insert) all GP EHR clinical data
        for a given phenotype and the given read codes.

        Input
        -----

        phenotype (str) = name of phenotype
        read_codes (list) = list of Read codes
        insert (boolean) = set to True if records
        to be inserted in the 'phenotypes' table.

        Returns
        -------

        n (int) = affected rows if insert == True
        """

        insert = kwargs.get("insert", False)

        sql = f"""
            SELECT
                eid,
                '{phenotype}' AS 'phenotype',
                42040 AS 'field_id',
                read_code AS field_value,
                IF(
                    eventdate IS NOT NULL,
                    eventdate,
                    STR_TO_DATE('1900-01-01', '%Y-%m-%d')
                )  AS eventdate,
                NULL as data_value
            FROM
                gp_clinical
            WHERE
                read_code IN {UKBDatabase.list_to_sql(values)};
            """

        return self.query_insert([sql], "phenotypes", insert)

    def get_hospital_diagnoses_for_patients(self, eids: list):
        """
        Returns primary and secondary hospital diagnoses
        for a given list of patients.
        """

        sql = f"""
            SELECT
                e.eid,
                e.diag_icd10
            FROM
                hesin e
            WHERE
                e.diag_icd10 IS NOT NULL
            AND
                e.eid IN %(1)s

            UNION

            SELECT
                e.eid,
                e.diag_icd10
            FROM
                hesin_diag10 e
            WHERE
                e.diag_icd10 IS NOT NULL
            AND
                e.eid IN %(2)s
        """

        return self.query(sql, {"1": tuple(eids), "2": tuple(eids)})

    def extract_baseline_biomarker(self, phenotype: str, field_id: int, **kwargs):
        """
        Extract baseline information for a biomarker
        and using the date of assessment as the
        event date.
        """

        insert = kwargs.get("insert", False)

        sql = """
        SELECT
            b1.eid,
            '%s' AS 'phenotype',
            '%s' AS 'field_id',
            b1.value AS field_value,
            STR_TO_DATE(b2.value, "%%Y-%%m-%%d") AS eventdate,
            NULL as data_value
        FROM
             baseline b1
        LEFT OUTER JOIN baseline b2
            ON b2.eid = b1.eid
            AND b2.i = b1.i
            AND b2.n = b1.n
            AND b2.field = 53
        WHERE
            b1.field = %s
        """ % (
            phenotype,
            field_id,
            field_id,
        )

        return self.query_insert([sql], "phenotypes", insert)

    def get_patient_cohort(self, eids: list):
        """
        Extract baseline information from the _baseline_cohort_
        table for a given set of patients identified by
        eids.

        Arguments
            eids (list) : list of eids
        """

        sql = f"""
        SELECT *
        FROM baseline_cohort b
        WHERE b.eid IN {UKBDatabase.list_to_sql(eids)}
        """

        return self.query(sql, eids).fetchall()

    def extract_biomarker_ehr(
        self, pheno_tag: str, serum_codes: list, plasma_codes: list, **kwargs
    ):
        """
        Return (or insert) all GP EHR clinical data
        for entries with a valid serum or plasma measurement

        Input
        -----

        pheno_tag (str) = phenotype label for entries
        serum_codes (list) = list of serum Read codes
        plasma_codes (list) = list of plasma Read codes
        insert (boolean) = set to True if records
        to be inserted in the 'phenotypes' table.

        Returns
        -------
        (Number of) measurement entries added to phenotypes

        """

        null_mmol_units = "('MEA000','MEA096','mmol/l','mmol/L','MMOL/L','Mmol/mol','Unknown','No UOM assigned')"

        plasma_place = "','".join(plasma_codes)
        serum_place = "','".join(serum_codes)

        insert = kwargs.get("insert", False)

        # basic query structure
        sql_struct = """
            SELECT
                a.eid,
                '%s' AS phenotype,
                42040 AS field_id,
                a.field_value,
                a.eventdate,
                a.data_value
            FROM(
                SELECT
                    eid,
                    read_code AS field_value,
                    eventdate,
                    IF(data_provider = 2, value2, value1) AS data_value,
                    IF(data_provider = 2, value3, NULL) AS units
                FROM
                    gp_clinical
            ) AS a
            WHERE
                a.field_value IN ('%s') AND
                (a.units IS NULL OR
                a.units IN %s)
        """

        plasma_sql = sql_struct % (pheno_tag + "_plasma", plasma_place, null_mmol_units)
        serum_sql = sql_struct % (pheno_tag + "_serum", serum_place, null_mmol_units)

        return self.query_insert([plasma_sql, serum_sql], "phenotypes", insert)


    def extract_diagnosis_entries(self, phenotype: str, test_dir: str = None):
        """
        Mimicking how the YAML diagnoses are extracted in extract_phenotype
        Just converting the entries to DF rather than inserting into DB
        """
        # TODO: REWRITE/DELETE using extract_phenotype

        # we are NOT inserting into phenotypes right now - just pulling entries
        to_insert = False

        # init df
        # TODO: load columns from elsewhere
        diag_columns = [
            "eid",
            "phenotype",
            "field_id",
            "field_value",
            "eventdate",
            "data_value",
        ]
        diagnosis_entries = pd.DataFrame(columns=diag_columns)

        # Extract phenotype name from metadata - this is just needed to work w existing db fxns
        # call Phenotype to explore YAML
        if test_dir is None:
            pheno = Phenotype(phenotype)
        # in a temporary folder for testing
        else:
            pheno = Phenotype(phenotype, input_dir=test_dir)
        phenotype_name = pheno.metadata["variable_name"]
        phenotype_definition_fields = pheno.get_definition_fields()
        for f in phenotype_definition_fields:

            if f in ["SNOMED-CT", 42039]:  # 42039 is prescriptions
                continue

            # Get definitions
            field_definition = pheno.get_field_definition(f)
            # Get metadata
            field_metadata = field_definition["metadata"]
            # Get values
            field_values = pheno.get_values_for_field(f)

            if f == 20001:
                field_entries = pd.DataFrame(
                    self.extract_cancer_self_report(
                        phenotype=phenotype_name, values=field_values, insert=to_insert
                    )
                )

            elif f == 20002:
                field_entries = pd.DataFrame(
                    self.extract_non_cancer_self_report(
                        phenotype=phenotype_name, values=field_values, insert=to_insert
                    )
                )

            elif f == 41200:
                field_entries = pd.DataFrame(
                    self.extract_hospital_primary_procedures(
                        phenotype=phenotype_name, values=field_values, insert=to_insert
                    )
                )

            elif f == 20004:
                field_entries = pd.DataFrame(
                    self.extract_procedures_self_report(
                        phenotype=phenotype_name, values=field_values, insert=to_insert
                    )
                )

            elif f == 41210:
                field_entries = pd.DataFrame(
                    self.extract_hospital_secondary_procedures(
                        phenotype=phenotype_name, values=field_values, insert=to_insert
                    )
                )

            elif f == 41202:
                incident_field_values = pheno.get_values_for_field(f)
                if len(incident_field_values) > 0:
                    inc_df = pd.DataFrame(
                        self.extract_hospital_primary_diagnoses(
                            phenotype=phenotype_name,
                            values=incident_field_values,
                            insert=to_insert,
                            prevalent=False,
                        )
                    )
                else:
                    inc_df = pd.DataFrame()

                prevalent_field_values = pheno.get_values_for_field(f, type="prevalent")
                if len(prevalent_field_values) > 0:
                    prev_df = pd.DataFrame(
                        self.extract_hospital_primary_diagnoses(
                            phenotype=phenotype_name,
                            values=prevalent_field_values,
                            insert=to_insert,
                            prevalent=True,
                        )
                    )
                else:
                    prev_df = pd.DataFrame()
                # combine entries
                field_entries = pd.concat([inc_df, prev_df], ignore_index=True)

            elif f == 41204:
                incident_field_values = pheno.get_values_for_field(f)
                if len(incident_field_values) > 0:
                    inc_df = pd.DataFrame(
                        self.extract_hospital_secondary_diagnoses(
                            phenotype=phenotype_name,
                            values=incident_field_values,
                            insert=to_insert,
                            prevalent=False,
                        )
                    )
                else:
                    inc_df = pd.DataFrame()

                prevalent_field_values = pheno.get_values_for_field(f, type="prevalent")
                if len(prevalent_field_values) > 0:
                    prev_df = pd.DataFrame(
                        self.extract_hospital_secondary_diagnoses(
                            phenotype=phenotype_name,
                            values=prevalent_field_values,
                            insert=to_insert,
                            prevalent=True,
                        )
                    )
                else:
                    prev_df = pd.DataFrame()
                # combine entries
                field_entries = pd.concat([inc_df, prev_df], ignore_index=True)

            elif f == 40001:
                field_entries = pd.DataFrame(
                    self.extract_primary_mortality(
                        phenotype=phenotype_name, values=field_values, insert=to_insert
                    )
                )

            elif f == 40002:
                field_entries = pd.DataFrame(
                    self.extract_secondary_mortality(
                        phenotype=phenotype_name, values=field_values, insert=to_insert
                    )
                )

            elif f == 42040:
                incident_field_values = pheno.get_values_for_field(f)
                if len(incident_field_values) > 0:
                    inc_df = pd.DataFrame(
                        self.extract_incident_primary_care_diagnoses(
                            phenotype=phenotype_name,
                            values=incident_field_values,
                            insert=to_insert,
                        )
                    )
                else:
                    inc_df = pd.DataFrame()

                prevalent_field_values = pheno.get_values_for_field(f, type="prevalent")
                if len(prevalent_field_values) > 0:
                    prev_df = pd.DataFrame(
                        self.extract_prevalent_primary_care_diagnoses(
                            phenotype=phenotype_name,
                            values=prevalent_field_values,
                            insert=to_insert,
                        )
                    )
                else:
                    prev_df = pd.DataFrame()
                # combine entries
                field_entries = pd.concat([inc_df, prev_df], ignore_index=True)

            elif f == 40006:
                field_entries = pd.DataFrame(
                    self.extract_cancer_registry_data(
                        phenotype=phenotype_name,
                        field_id=f,
                        values=field_values,
                        date_field_id=40005,
                        insert=to_insert,
                    )
                )

            # This is a non-standardized field.
            else:
                if "type" in field_metadata and field_metadata["type"] == "biomarker":
                    field_entries = pd.DataFrame(
                        self.extract_baseline_biomarker(
                            phenotype=phenotype_name, field_id=f, insert=to_insert
                        )
                    )
                else:
                    if "time_qualifier" in field_metadata:
                        if field_metadata["time_qualifier"]["type"] == "age":
                            field_entries = pd.DataFrame(
                                self.extract_field_value_with_age_qualifier(
                                    phenotype=phenotype_name,
                                    field_id=f,
                                    values=field_values,
                                    age_field_id=field_metadata["time_qualifier"][
                                        "field_id"
                                    ],
                                    insert=to_insert,
                                )
                            )
                        elif field_metadata["time_qualifier"]["type"] == "baseline":
                            field_entries = pd.DataFrame(
                                self.extract_field_value_with_baseline_qualifier(
                                    phenotype=phenotype_name,
                                    field_id=f,
                                    values=field_values,
                                    insert=to_insert,
                                )
                            )
                        elif field_metadata["time_qualifier"]["type"] == "year":
                            field_entries = pd.DataFrame(
                                self.extract_field_value_with_date_qualifier(
                                    phenotype=phenotype_name,
                                    field_id=f,
                                    values=field_values,
                                    date_field_id=field_metadata["time_qualifier"][
                                        "field_id"
                                    ],
                                    insert=to_insert,
                                )
                            )

            # add to diagnosis df
            if not field_entries.empty:
                field_entries.columns = diag_columns
                diagnosis_entries = pd.concat(
                    [diagnosis_entries, field_entries], ignore_index=True
                )

        return diagnosis_entries

    def insert_from_df(self, df: pd.DataFrame, table_name: str):
        """
        Inserts entries from a pandas DataFrame `df` into a table `table_name`.
        `df` must have the same columns as the table.

        This is useful for ComplexPhenotypes which undergo processing in Python
        """

        if len(df) == 0:
            logging.error("Empty dataframe can't be loaded into table")
            return None
        sql = f"INSERT INTO {table_name} ({', '.join(df.columns)}) VALUES "
        for i in range(len(df)):
            if i != 0:
                sql += ", "
            sql += (
                "("
                + ", ".join([f"'{x}'" if x is not None else "NULL" for x in df.iloc[i]])
                + ")"
            )
        sql += ";"
        return self.query(sql).rowcount

    def get_baseline_cohort_eids(self):
        """
        The baseline_cohort table is the master source for participants that remain in the study,
        meaning that this function gives a list of participant ids in the study.
        """

        sql = """
        SELECT DISTINCT(eid) FROM baseline_cohort;
        """
        return set([x[0] for x in self.query(sql).fetchall()])
