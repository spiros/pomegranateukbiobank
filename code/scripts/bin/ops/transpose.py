"""
Transpose the UK Biobank baseline file from wide to long format.

Note: in order to save space, this script will not output
rows where the value is missing.

"""

import csv
import argparse
from tqdm import tqdm
import gzip

argparser = argparse.ArgumentParser()
argparser.add_argument('-input', type=str)
argparser.add_argument('-output', type=str)
args = argparser.parse_args()

finput = args.input
foutput = args.output + ".gz"

with open(finput, errors='ignore', encoding="utf-8") as csv_input:
    csv_reader = csv.reader(csv_input, delimiter=",")
    line = 0

    with gzip.open(foutput, 'wt', encoding="utf-8") as csv_output:
        csv_writer = csv.writer(csv_output, delimiter=",")

        for row in tqdm(csv_reader, total=5000000):
            if line == 0:
                cols = row
                csv_writer.writerow(['eid', 'field', 'i', 'n', 'value'])
            else:
                eid = row[0]
                # Skip fields where the value is missing to save space
                for i, col_value in enumerate(row[1:]):
                    if col_value == '' or col_value is None:
                        continue
                    col_name = cols[i+1]
                    try:
                        field_id, instance = col_name.split('.')[0].split('-')
                    except ValueError:
                        field_id = col_name.split('-')[0]
                        instance = 0
                        n = 0

                    n = col_name.split('.')[1]
                    csv_writer.writerow([eid, field_id, instance, n, col_value])

            line += 1
