""" Script to load UK Biobank baseline to MySQL. """

import argparse
import MySQLdb
import csv
from tqdm import tqdm
import os

# Parse arguments
argparser = argparse.ArgumentParser()
argparser.add_argument('-input', type=str, required=True)
args = argparser.parse_args()

# Setup DB connection
db_host = os.getenv('POMEGRANATE_DEVEL_DB_HOST')
db_port = int(os.getenv('POMEGRANATE_DEVEL_DB_PORT'))
db_dbname = os.getenv('POMEGRANATE_DEVEL_DB_DB')
db_username = os.getenv('POMEGRANATE_DEVEL_DB_USERNAME')
db_password = os.getenv('POMEGRANATE_DEVEL_DB_PASSWD')

if None in (db_host, db_port, db_dbname, db_username, db_password):
    raise Exception("Missing configuration for DB.")


def infer_field_info(field_name):
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


if __name__ == "__main__":

    # Connect to database
    db_connection = MySQLdb.connect(
        host=db_host,
        user=db_username,
        passwd=db_password,
        port=db_port,
        db=db_dbname)

    with db_connection.cursor() as c:

        # Load data
        with open(args.input, mode='r') as f:
            reader = csv.reader(f)

            n = 0
            file_columns = []
            rows_to_insert = []

            for row in tqdm(reader):

                # First row of file, store
                # column names and skip.
                if row[0] == 'eid':
                    file_columns = row
                    continue

                for y, column_value in enumerate(row[1:]):

                    # Skip column if value is empty or is missing
                    if column_value == '' or column_value is None:
                        continue

                    # Process column
                    column_name = file_columns[y + 1]
                    field_id, field_instance, field_n = infer_field_info(column_name)

                    # Insert records
                    row_to_insert = (int(row[0]), field_id, field_instance, field_n, column_value)
                    rows_to_insert.append(row_to_insert)

                    if len(rows_to_insert) == 1000:
                        c.executemany('INSERT INTO baseline VALUES (%s, %s, %s, %s, %s)', rows_to_insert)
                        rows_to_insert = []
                        continue

            # Flush remaining records
            c.executemany('INSERT INTO baseline VALUES (%s, %s, %s, %s, %s)', rows_to_insert)

        db_connection.commit()

    db_connection.close()
