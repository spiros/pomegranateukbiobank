"""A module for connection and administrative functions."""

import os

import pymysql
from pomegranate.exceptions import GenericException
from pomegranate.error_codes import ErrorCode
from sqlalchemy import create_engine


class MySQLDatabase:
    """
    Manages connecting to MySQL databases and executing queries.
    """

    def __init__(self, **kwargs) -> None:
        """
        Creates a new instance of the class.
        Information on what arguments are available in PyMySQL:
        https://pymysql.readthedocs.io/en/latest/modules/connections.html#pymysql.connections.Connection


        Parameters
        ----------
        host : hostname
        port : port
        db : database name
        user : MySQL username
        passwd : MySQL password
        autocommit : autocommit flag (default: True)
        cursorclass : cursor class (default pymysql.cursors.Cursor)

        Note:
        ------

        Replace the xxx below for host, port, db, user, passdw as appropriate in your set up 

        """

        self.config = kwargs
        self.config["host"] = kwargs.get(
            "host", os.getenv("POMEGRANATE_DB_HOST", "xxx.x.x.x")
        )
        self.config["port"] = kwargs.get(
            "port", int(os.getenv("POMEGRANATE_DB_PORT", xxxx))
        )
        self.config["db"] = kwargs.get("db", os.getenv("POMEGRANATE_DB_DB", "xxx"))
        self.config["user"] = kwargs.get(
            "username", os.getenv("POMEGRANATE_DB_USERNAME", "xxx")
        )
        self.config["passwd"] = kwargs.get(
            "passwd", os.getenv("POMEGRANATE_DB_PASSWD", "xxx")
        )
        self.config["autocommit"] = kwargs.get("autocommit", True)
        self.config["cursorclass"] = kwargs.get("cursorclass", pymysql.cursors.Cursor)
        self.connect()

    def connect(self):
        """
        Connect to the database.
        """

        try:

            self.connection = pymysql.connect(
                host=self.config["host"],
                user=self.config["user"],
                passwd=self.config["passwd"],
                port=self.config["port"],
                db=self.config["db"],
                cursorclass=self.config["cursorclass"],
                client_flag=pymysql.constants.CLIENT.MULTI_STATEMENTS,
            )

            self.cursor = self.connection.cursor()
            self.connection.autocommit(self.config["autocommit"])

        except Exception as e:

            db_connection_not_working = GenericException(
                ErrorCode.DB_CONNECTION_FAILED, e
            )

            raise db_connection_not_working

    def commit(self):
        """
        Commit all pending transaction queries
        in case autocommit is off.
        """

        return self.connection.commit()

    def disconnect(self):
        """
        Terminate connection to database.
        """

        self.cursor.close()
        self.connection.close()

    def is_connected(self):
        """
        Check if we are still connected to the database.
        """

        return self.connection.open

    def get_connection(self):
        """
        Return connection object.
        """

        return self.connection

    def count_rows(self, table: str) -> int:
        """
        Count the rows in a table.
        """

        data = self.query("SELECT COUNT(*) AS num_rows FROM %s" % table).fetchall()
        return data[0]["num_rows"]

    def drop_table_if_exists(self, table: str):
        """
        DROP table.

        Parameters
        ----------
        table : table name to drop

        """

        # NOTE: parametrization of table names or column names is not possible
        # so we need to escape the parameter using backquotes.

        return self.query("DROP TABLE IF EXISTS %s" % table)

    def query(self, sql: str, sql_params: list = None):
        """
        Execute a query.

        Parameters
        ----------
            sql = sql statement (str)
            sql_params = sql statement params (list)

        Output
        ------
            cursor object (pymysql.cursors.Cursor)

        """

        try:
            # Convert dict_values to list for PyMySQL compatibility
            if (
                sql_params is not None
                and hasattr(sql_params, "__iter__")
                and not isinstance(sql_params, (str, bytes, dict))
            ):
                sql_params = list(sql_params)
            self.cursor.execute(sql, sql_params)
        except Exception as e:
            print("Query failed: ", sql, "params: ", sql_params, " exception: ", e)
            raise

        return self.cursor

    def execute_multiple(self, sql: str, sql_params: list = None):
        """
        Execute multiple SQL statements separated by semicolons.

        Parameters
        ----------
            sql = sql statements separated by semicolons (str)
            sql_params = sql statement params (list)

        Returns
        -------
            list of results from each statement
        """
        try:
            # Execute all statements
            self.cursor.execute(sql, sql_params)

            # Collect results from all statements
            results = []
            results.append(self.cursor.fetchall())

            # Process any additional result sets
            while self.cursor.nextset():
                results.append(self.cursor.fetchall())

            return results

        except Exception as e:
            print(
                "Multiple query failed: ",
                sql,
                "params: ",
                sql_params,
                " exception: ",
                e,
            )
            raise

    def get_column_names(self, database: str, table: str) -> list:
        """
        Returns the column names for a given schema / table
        combination.

        Arguments
        ---------

        database (str) : database name
        table (str) : table name

        Returns
        -------

        list [of str] with table names.

        """

        sql = f"""
        SELECT COLUMN_NAME
        from INFORMATION_SCHEMA.COLUMNS
        where TABLE_NAME = '{table}'
        and TABLE_SCHEMA= '{database}'
        """

        return [x[0] for x in self.query(sql).fetchall()]

    def _get_sqlite_engine(self):
        """
        This is an internal function - only used
        for pandas to save a dataframe in the database
        by creating an sqlalcemy engine.
        """

        engstr = f"mysql+pymysql://{self.config['user']}:{self.config['passwd']}@{self.config['host']}:{int(self.config['port'])}/{self.config['db']}"
        engine = create_engine(engstr, echo=False)
        return engine

    def __enter__(self):
        """Magic method"""

        return self

    def __exit__(self, type, value, traceback):
        """Magic method"""

        self.disconnect()
