# Pomegranate

This document outlines the three major components of the pomegranate project for UK Biobank data and how to set them up in a local MySql database:

* [instal and configure the the Python pipeline](#python)
* [the MySQL schema used to load and transform raw data](#database-schema)
* [the YAML file format for storing phenotyping algorithms](#yamlfile)

Please note that code is offered 'as-is'. 

## Setup MySQL testing env

Make sure you install MySQL (from binary or source). The pipeline has been developed using version 8.0.4.


## Setup Python development pipeline 
<a id="python"></a>

### Environment variables

Some configuration parameters are stored in environment variables which need to be set. Specifically, a set of variables contain the **production** database configuration details:

| Variable | Description | 
|----------|-------------|
| POMEGRANATE_DB_HOST | IP address of MySQL database server |
| POMEGRANATE_DB_PORT| Database port |
| POMEGRANATE_DB_USERNAME | Database user name |
| POMEGRANATE_DB_PASSWD | Password | 
| POMEGRANATE_DB_DB | Database name | 


You can verify that the variables have been set by using the `env` command:

```console
(da) ➜ pomegranate (master) ✗ env | grep POM 
POMEGRANATE_DB_HOST=xxx.x.x.x
POMEGRANATE_DB_PORT=xxxx
POMEGRANATE_DB_USERNAME=xxxx
POMEGRANATE_DB_PASSWD=xxxx
POMEGRANATE_DB_DB=xxxx
```

### Step-by-step instructions using Anaconda 

The following steps are executed in a bash shell in the root folder of the pomegranate repository.

1. You need to create a project virtual environment using Anaconda (see below for instructions without using Anaconda - miniconda will also work). A virtual environment is basically a project-specific copy of the python executables plus any specific libraries you install:

```console
user@host$ conda env create -f conda.yml
```

and then confirm using:

```console
user@host$ conda env list
```

The anaconda site has a good [tutorial](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-from-an-environment-yml-file) This  and [cheatsheet](https://docs.conda.io/projects/conda/en/4.6.0/_downloads/52a95608c49671267e40c689e0bc00ca/conda-cheatsheet.pdf)

2. Activate your environment (example below assumes yoy have called it 'pom'):

```console
user@host$ conda activate pom
```

You can check if its active using: 

```console
user@host$ conda info
```

2. Install the Python libraries that pomegranate uses. 
You can use the `pip` command and the `requirements.txt` file to do this:

```console
user@host$ pip install -r requirements.txt
```

3. Set your PYTHONPATH environment variable to include the pomegranate library path. 

For example, on my computer, I have cloned the repository in `/Users/user/pomegranate`. 

The following command appends the PYTHONPATH env:

```console
user@host$ export PYTHONPATH=$PYTHONPATH:/Users/user/pomegranate
```

You can verify it's working by running:

```console
user@host$ env | grep PYTHONPATH
```

It's strongly recommended to include this command in the `.bash_profile` or `.bashrc` file
in your home directory so you dont need to type it in manually all the time.

4. Run the pytest suite to verify things are working:

```console
user@host$ pytest -s tests
```

### Step-by-step instructions for Mac using venv
If you prefer to install and manage environments using pip and venv, you can use these instructions instead of those above. These instructions are intended for developers of pomegranate or users who want to create the database and run the code to extract the phenotypes and assume you already have the [venv](https://docs.python.org/3/library/venv.html) library installed. Instructions are given assuming you are in the root of the pomegranate repo.

Set up and activate a virtual environment.
```console
python -m venv venv/
source venv/bin/activate
```

Ensure you have installed MySQL locally:
```console
brew install mysql
```

Install the required modules:
```console
pip install -r requirements.txt
```

Install pomegranate (editable, so it will update as you're working on it)
```console
pip install -e .
```

Check it all worked by running tests:
```console
python -m pytest
```

### If things go wrong.

The MySQL python package requires MySQL to be installed locally.

Additionally, the following error message might indicate that the 
shared library between Python and the MySQL client library `_mysql.so`
is not setup.

```
Traceback (most recent call last):
  File "export_tables.py", line 7, in <module>
    import MySQLdb
  File "/Users/ana/opt/anaconda3/envs/pom/lib/python3.7/site-packages/MySQLdb/__init__.py", line 18, in <module>
    from . import _mysql
ImportError: dlopen(/Users/ana/opt/anaconda3/envs/pom/lib/python3.7/site-packages/MySQLdb/_mysql.cpython-37m-darwin.so, 2): Library not loaded: @rpath/libmysqlclient.21.dylib
  Referenced from: /Users/ana/opt/anaconda3/envs/pom/lib/python3.7/site-packages/MySQLdb/_mysql.cpython-37m-darwin.so
  Reason: image not found
```

To fix this, set the library path:

```console
user@host$ export DYLD_LIBRARY_PATH=/usr/local/mysql/lib:$DYLD_LIBRARY_PATH
```

On OSX, you might need to install `pkg-config` as well:

```console
brew install pkg-config
```

This [SO post](https://stackoverflow.com/questions/4559699/python-mysqldb-and-library-not-loaded-libmysqlclient-16-dylib) contains some useful details and the [installation details](https://github.com/PyMySQL/mysqlclient/blob/main/README.md) for mysqlclient have some pointers (e.g. maybe you also need to install `mysql-client` using homebrew)

p.s. set this in your `.bash_profile` so you dont need to execute it every time.

The [`rpy2`](https://rpy2.github.io/) package, a python connector for R, naturally requires R to be installed locally. See instructions at [R Project](https://www.r-project.org/).  


## Database schema
 <a id="database-schema"></a>



### Introduction

The purpose of this document is to provide a description of how raw UK Biobank data are loaded and stored within a relational datababase management system (MySQL v. 5.7.21). 

We outline below the key tables required and their schema:

| Table | Contents |
|-------|----------|
| baseline | Baseline assessment information (long format) | 
| hesin | Hospital EHR hospitalization metadata | 
| hesin_diag | Hospital EHR diagnoses | 
| hesin_oper | Hospital EHR procedures and interventions | 
| gp_registrations | Primary care EHR registrations  | 
| gp_prescriptions | Primary care EHR medication prescriptions | 
| gp_clinical | Primary care EHR diagnoses, laboratory measurements and lifestyle risk factor information | 
| phenotypes | Raw phenotype data stratified by UK Biobank field, populated by ETL |
| phenotype_first | First diagnoses, by field, by phenotype |


<!-- ![Overall schema](schema.png) -->

### Raw data tables

### Baseline 

We store a transposed and decomposed version of the baseline by converting the baseline data file from a wide format:
    
```
eid, fieldid1-i-n, fieldid2-i-n, fieldid3-i-n, fieldid4-i-n... fieldidn-i-n
```


to a long format:
```
eid, fieldid1, i, n, value1
eid, fieldid2, i, n, value2
eid, fieldid3, i, n, value3
eid, fieldid4, i, n, value4
```

```sql
DROP TABLE IF EXISTS baseline;
CREATE TABLE IF NOT EXISTS baseline(
    eid INT,
    field INT(5),
    i INT(2),
    n INT(2),
    value TEXT
);

CREATE INDEX b ON baseline(eid,field,i,n);
```

The entire process covering ~500,000 patients and ~9000 fields takes ~5 hours to run on a i7/4.2Ghz OS X box with 32GB RAM. Records where the value is missing or is empty are not stored in order to preserve space.

The following Python script (`load_baseline_to_mysql.py`) will read, transpose and load a baseline CSV file to the database.

```python
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
db_host = os.getenv('POMEGRANATE_DB_HOST')
db_port = int(os.getenv('POMEGRANATE_DB_PORT'))
db_dbname = os.getenv('POMEGRANATE_DB_DB')
db_username = os.getenv('POMEGRANATE_DB_USERNAME')
db_password = os.getenv('POMEGRANATE_DB_PASSWD')

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
```
#### Death data

Death data are recorded in two locations: the baseline data file and as stand-alone files which are available directly to download in the Showcase. The following tables accomodate the latter format and enable the loading
of death data that are released for download directly from the UK Biobank.

* UK Biobank [documentation on death data linkage](https://biobank.ctsu.ox.ac.uk/crystal/crystal/docs/DeathLinkage.pdf)

##### Dates of death

```sql
DROP TABLE IF EXISTS death;
CREATE TABLE IF NOT EXISTS death(
  eid INT(7) unsigned,
  ins_index INT(1) UNSIGNED,
  dsource VARCHAR(5),
  source INT(1) UNSIGNED,
  date_of_death DATE
);

LOAD DATA INFILE 'death.txt'
INTO TABLE death
FIELDS TERMINATED BY '\t' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(
  eid,
  ins_index,
  dsource,
  source,
  @date_of_death
)
SET
  date_of_death     = IF(@date_of_death = '', NULL, str_to_date(@date_of_death, '%d/%m/%Y'));

CREATE INDEX e ON death(eid);
```

##### Cause of death

```sql
DROP TABLE IF EXISTS death_cause;
CREATE TABLE IF NOT EXISTS death_cause(
  eid INT(7) UNSIGNED,
  ins_index INT(1) UNSIGNED,
  arr_index INT(1) UNSIGNED,
  `level` INT(1) UNSIGNED,
  cause_icd10 VARCHAR(5)
);

LOAD DATA INFILE 'death_cause.txt'
INTO TABLE death_cause
FIELDS TERMINATED BY '\t' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES;

CREATE INDEX e ON death_cause(eid,level,cause_icd10);
```

#### Hospital EHR

* Official [HES data dictionary](http://biobank.ctsu.ox.ac.uk/crystal/label.cgi?id=2000)

##### Hospitalizations

* `classpat`, `admisorc`, `disdest` and `admimeth` are columns defined as integer in the documentation but very rarely can contain characters (e.g. 'A')

```sql
DROP TABLE IF EXISTS hesin;
CREATE TABLE IF NOT EXISTS hesin(
    eid INT(7) UNSIGNED,
    ins_index INT(5) UNSIGNED,
    dsource CHAR(5),
    source INT(5) UNSIGNED,
    epistart DATE,
    epiend DATE,
    epidur INT(5) UNSIGNED,
    bedyear INT(5) UNSIGNED,
    epistat INT(5) UNSIGNED,
    epitype INT(5) UNSIGNED,
    epiorder INT(5) UNSIGNED,
    spell_index INT(5) UNSIGNED,
    spell_seq INT(5) UNSIGNED,
    spelbgin INT(5) UNSIGNED,
    spelend  CHAR(5),
    speldur INT(5) UNSIGNED,
    pctcode CHAR(5),
    gpprpct CHAR(5),
    category INT(5) UNSIGNED,
    elecdate DATE,
    elecdur INT(5) UNSIGNED,
    admidate DATE,
    admimeth_uni INT(5) UNSIGNED,
    admimeth CHAR(5),
    admisorc_uni INT(5) UNSIGNED,
    admisorc CHAR(5),
    firstreg INT(5) UNSIGNED,
    classpat_uni INT(5) UNSIGNED,
    classpat CHAR(5),
    intmanag_uni INT(5) UNSIGNED,
    intmanag INT(5) UNSIGNED,
    mainspef_uni INT(5) UNSIGNED,
    mainspef CHAR(5),
    tretspef_uni INT(5) UNSIGNED,
    tretspef CHAR(5),
    operstat INT(5) UNSIGNED,
    disdate DATE,
    dismeth_uni INT(5) UNSIGNED,
    dismeth INT(5) UNSIGNED,
    disdest_uni INT(5) UNSIGNED,
    disdest CHAR(5),
    carersi INT(5) UNSIGNED  
);

LOAD DATA INFILE 'hesin.txt'
INTO TABLE hesin
FIELDS TERMINATED BY '\t' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(
    @eid,
    @ins_index,
    @dsource,
    @source,
    @epistart,
    @epiend,
    @epidur,
    @bedyear,
    @epistat,
    @epitype,
    @epiorder,
    @spell_index,
    @spell_seq,
    @spelbgin,
    @spelend,
    @speldur,
    @pctcode,
    @gpprpct,
    @category,
    @elecdate,
    @elecdur,
    @admidate,
    @admimeth_uni,
    @admimeth,
    @admisorc_uni,
    @admisorc,
    @firstreg,
    @classpat_uni,
    @classpat,
    @intmanag_uni,
    @intmanag,
    @mainspef_uni,
    @mainspef,
    @tretspef_uni,
    @tretspef,
    @operstat,
    @disdate,
    @dismeth_uni,
    @dismeth,
    @disdest_uni,
    @disdest,
    @carersi
)
SET
    eid          = NULLIF(@eid, ''),
    ins_index    = NULLIF(@ins_index, ''),
    dsource      = NULLIF(@dsource, ''),
    source       = NULLIF(@source, ''),
    epistart     = IF(@epistart = '', NULL, str_to_date(@epistart, '%d/%m/%Y')),
    epiend       = IF(@epiend = '', NULL, str_to_date(@epiend, '%d/%m/%Y')),
    epidur       = NULLIF(@epidur, ''),
    bedyear      = NULLIF(@bedyear, ''),
    epistat      = NULLIF(@epistat, ''),
    epitype      = NULLIF(@epitype, ''),
    epiorder     = NULLIF(@epiorder, ''),
    spell_index  = NULLIF(@spell_index, ''),
    spell_seq    = NULLIF(@spell_seq, ''),
    spelbgin     = NULLIF(@spelbgin, ''),
    spelend      = NULLIF(@spelend, ''),
    speldur      = NULLIF(@speldur, ''),
    pctcode      = NULLIF(@pctcode, ''),
    gpprpct      = NULLIF(@gpprpct, ''),
    category     = NULLIF(@category, ''),
    elecdate     = IF(@elecdate = '', NULL, str_to_date(@elecdate, '%d/%m/%Y')),
    elecdur      = NULLIF(@elecdur, ''),
    admidate     = IF(@admidate = '', NULL, str_to_date(@admidate, '%d/%m/%Y')),
    admimeth_uni = NULLIF(@admimeth_uni, ''),
    admimeth     = NULLIF(@admimeth, ''),
    admisorc_uni = NULLIF(@admisorc_uni, ''),
    admisorc     = NULLIF(@admisorc, ''),
    firstreg     = NULLIF(@firstreg, ''),
    classpat_uni = NULLIF(@classpat_uni, ''),
    classpat     = NULLIF(@classpat, ''),
    intmanag_uni = NULLIF(@intmanag_uni, ''),
    intmanag     = NULLIF(@intmanag, ''),
    mainspef_uni = NULLIF(@mainspef_uni, ''),
    mainspef     = NULLIF(@mainspef, ''),
    tretspef_uni = NULLIF(@tretspef_uni, ''),
    tretspef     = NULLIF(@tretspef, ''),
    operstat     = NULLIF(@operstat, ''),
    disdate      = IF(@disdate = '', NULL, str_to_date(@disdate, '%d/%m/%Y')),
    dismeth_uni  = NULLIF(@dismeth_uni, ''),
    dismeth      = NULLIF(@dismeth, ''),
    disdest_uni  = NULLIF(@disdest_uni, ''),
    disdest      = NULLIF(@disdest, ''),
    carersi      = NULLIF(@carersi, '')
;

CREATE INDEX h ON hesin(eid, ins_index);
```

##### Diagnoses

```sql
DROP TABLE IF EXISTS hesin_diag;
CREATE TABLE IF NOT EXISTS hesin_diag(
    eid INT(7) UNSIGNED,
    ins_index INT(5) UNSIGNED,    
    arr_index INT(5) UNSIGNED,
    level INT(1) UNSIGNED,    
    diag_icd9 CHAR(7),
    diag_icd9_nb CHAR(7),
    diag_icd10 CHAR(7),
    diag_icd10_nb CHAR(7)
);

LOAD DATA INFILE 'hesin_diag.txt'
INTO TABLE hesin_diag
FIELDS TERMINATED BY '\t' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(
    eid,
    @ins_index,
    @arr_index,
    @level,
    @diag_icd9,
    @diag_icd9_nb,
    @diag_icd10,
    @diag_icd10_nb
)
SET 
    ins_index     = IF(@ins_index = '', NULL, @ins_index),
    arr_index     = IF(@arr_index = '', NULL, @arr_index),
    level         = IF(@level = '', NULL, @level),
    diag_icd9     = IF(@diag_icd9 = '', NULL, @diag_icd9),
    diag_icd9_nb  = IF(@diag_icd9_nb = '', NULL, @diag_icd9_nb),
    diag_icd10    = IF(@diag_icd10 = '', NULL, @diag_icd10),
    diag_icd10_nb = IF(@diag_icd10_nb = '', NULL, @diag_icd10_nb)
;

CREATE INDEX hesr ON hesin_diag(eid, ins_index, level, diag_icd10);
```

##### Procedures

* The operation date column `opdate` is stored as `'%d/%m/%Y'` (in contrast with how dates are stored in the `hesin` table which is `'%Y%m%d'`)

```sql
DROP TABLE IF EXISTS hesin_oper;
CREATE TABLE IF NOT EXISTS hesin_oper(
    eid INT(7) UNSIGNED,
    ins_index INT(5) UNSIGNED,    
    arr_index INT(5) UNSIGNED,
    level INT(1) UNSIGNED,    
    opdate DATE DEFAULT NULL,
    oper3 CHAR(5),
    oper3_nb CHAR(5),
    oper4 CHAR(5),
    oper4_nb CHAR(5),
    posopdur INT(5) UNSIGNED,
    preopdur INT(5) UNSIGNED
);

LOAD DATA INFILE 'hesin_oper.txt'
INTO TABLE hesin_oper
FIELDS TERMINATED BY '\t' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(
    eid,
    @ins_index,
    @arr_index,
    @level,
    @opdate,
    @oper3,
    @oper3_nb,
    @oper4,
    @oper4_nb,
    @posopdur,
    @preopdur
)
SET
    ins_index = IF(@ins_index = '', NULL, @ins_index),
    arr_index = IF(@arr_index = '', NULL, @arr_index),
    level     = IF(@level = '', NULL, @level),
    opdate    = IF(@opdate = '', NULL, str_to_date(@opdate, '%d/%m/%Y')),
    oper3     = IF(@oper3 = '', NULL, @oper3),
    oper3_nb  = IF(@oper3_nb = '', NULL, @oper3_nb),
    oper4     = IF(@oper4 = '', NULL, @oper4),
    oper4_nb  = IF(@oper4_nb = '', NULL, @oper4_nb),
    posopdur  = IF(@posopdur = '', NULL, @posopdur),
    preopdur  = IF(@preopdur = '', NULL, @preopdur)
;

CREATE INDEX hesr ON hesin_oper(eid, ins_index, level, oper4);
```

#### Primary care EHR

* Official [GP EHR data dictionary](http://biobank.ctsu.ox.ac.uk/crystal/label.cgi?id=3000)

##### Registrations

```sql
DROP TABLE IF EXISTS gp_registrations;
CREATE TABLE IF NOT EXISTS gp_registrations (
    eid INT(7) UNSIGNED,
    data_provider INT(1),
    reg_date DATE,
    deduct_date DATE
);

LOAD DATA INFILE 'gp_registrations.txt'
INTO TABLE gp_registrations
FIELDS TERMINATED BY '\t' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(
    @eid,
    @data_provider,
    @reg_date,
    @deduct_date
)
SET
    eid           = NULLIF(@eid, ''),
    data_provider = NULLIF(@data_provider, ''),
    reg_date      = IF( @reg_date = '', NULL, str_to_date(@reg_date, '%d/%m/%Y')),
    deduct_date   = IF( @deduct_date = '', NULL, str_to_date(@deduct_date, '%d/%m/%Y'));

CREATE INDEX gpreg ON gp_registrations(eid, data_provider);
```

##### Prescriptions

```sql
DROP TABLE IF EXISTS gp_prescriptions;
CREATE TABLE IF NOT EXISTS gp_prescriptions (
    eid INT(7) UNSIGNED,
    data_provider INT(1),
    issue_date DATE,
    read_2 VARCHAR(15),
    bnf_code VARCHAR(155),
    dmd_code VARCHAR(155),
    drug_name VARCHAR(255),
    quantity VARCHAR(255)
);

LOAD DATA INFILE 'gp_scripts.txt'
INTO TABLE gp_prescriptions
FIELDS TERMINATED BY '\t' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(
    @eid,
    @data_provider,
    @issue_date,
    @read_2,
    @bnf_code,
    @dmd_code,
    @drug_name,
    @quantity
)
SET
    eid           = NULLIF(@eid, ''),
    data_provider = NULLIF(@data_provider, ''),
    issue_date    = IF( @issue_date = '', NULL, str_to_date(@issue_date, '%d/%m/%Y')),
    read_2    = NULLIF(@read_2, ''),
    bnf_code  = NULLIF(@bnf_code, ''),
    dmd_code  = NULLIF(@dmd_code, ''),
    drug_name = NULLIF(@drug_name, ''),
    quantity  = NULLIF(@quantity, '');

CREATE INDEX gprx ON gp_prescriptions(eid, data_provider,read_2,bnf_code,dmd_code);
```


##### Diagnoses

```sql
DROP TABLE IF EXISTS gp_clinical;
CREATE TABLE IF NOT EXISTS gp_clinical (
    eid INT(7) UNSIGNED,
    data_provider INT(1),
    event_dt DATE,
    read_2 VARCHAR(15),
    read_3 VARCHAR(15),
    value1 VARCHAR(255),
    value2 VARCHAR(255),
    value3 VARCHAR(255)
);

LOAD DATA INFILE 'gp_clinical.txt'
INTO TABLE gp_clinical
FIELDS TERMINATED BY '\t' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(
    @eid,
    @data_provider,
    @event_dt,
    @read_2,
    @read_3,
    @value1,
    @value2,
    @value3
)
SET
    eid           = NULLIF(@eid, ''),
    data_provider = NULLIF(@data_provider, ''),
    event_dt      = IF( @event_dt = '', NULL, str_to_date(@event_dt, '%d/%m/%Y')),
    read_2 = NULLIF(@read_2, ''),
    read_3 = NULLIF(@read_3, ''),
    value1 = NULLIF(@value1, ''),
    value2 = NULLIF(@value2, ''),
    value3 = NULLIF(@value3, '');
```

###### Post-processing

Once the clinical data are loaded in the `gp_clinical` table, create a new
column `read_code` which will store the unified Read V2 and CTV3 information.

```sql
ALTER TABLE gp_clinical ADD COLUMN read_code VARCHAR(15);

UPDATE
    gp_clinical
SET
    read_code = read_2
WHERE
    read_2 IS NOT NULL
AND
    read_3 IS NULL;

UPDATE
    gp_clinical
SET
    read_code = read_3
WHERE
    read_2 IS NULL
AND
    read_3 IS NOT NULL;

CREATE INDEX gpca ON gp_clinical(eid,read_code);
```

The default collation is `latin1_swedish_ci` which is case insensitive - this means that Read code '44f..' and '44F..' are considered identical despite the fact that the first one is serum glucose and the latter is serum ALP. The following statement sets the table collation to `utf8` in order to enable case-sensitive comparisons. More information can be found on the MySQL Reference Manual [section on character sets](https://dev.mysql.com/doc/refman/8.0/en/charset.html).

```sql
ALTER TABLE gp_clinical CONVERT TO CHARACTER SET utf8 COLLATE utf8_bin;
```

UK Biobank uses placeholder dates for GP events where the date matches the participants
date of birth. Specifically, 

* Where the date matches participant date of birth it has been changed to 02/02/1902.
* Where the date follows participant date of birth but is in the year of their birth it has been changed to 03/03/1903

We create a unified `eventdate` column and set the values according to the `baseline` table information:

```sql
ALTER TABLE gp_clinical ADD COLUMN eventdate DATE;
UPDATE gp_clinical SET eventdate = event_dt;

UPDATE 
    gp_clinical g,
    baseline b
SET
    g.eventdate = STR_TO_DATE(CONCAT(b.value, '-07-01'), '%Y-%m-%d')
WHERE
    YEAR(g.eventdate) IN (1902, 1903)
AND
    g.eid = b.eid
AND
    b.field = 34
AND
    b.i = 0
AND
    b.i = 0;
```

Similarly, we set the `reg_date` in the `gp_registrations` table:


```sql
UPDATE
    gp_registrations g,
    baseline b
SET
    g.reg_date = STR_TO_DATE(CONCAT(b.value, '-07-01'), '%Y-%m-%d')
WHERE
    YEAR(g.reg_date) IN (1902, 1903)
AND
    g.eid = b.eid
AND
    b.field = 34
AND
    b.i = 0
AND
    b.i = 0;
```

Similarly, we update the `deduct_date` column in the `gp_registrations` table:

```sql
UPDATE
    gp_registrations g,
    baseline b
SET
    g.deduct_date = STR_TO_DATE(CONCAT(b.value, '-07-01'), '%Y-%m-%d')
WHERE
    YEAR(g.deduct_date) IN (1902, 1903)
AND
    g.eid = b.eid
AND
    b.field = 34
AND
    b.i = 0
AND
    b.i = 0;
```

### Project specific tables

#### Phenotypes 

The `phenotypes` table stores the raw data for phenotypes stratified by UK Biobank field.

```sql
DROP TABLE IF EXISTS phenotypes;
CREATE TABLE IF NOT EXISTS phenotypes(
    eid INT(15),
    phenotype VARCHAR(128),
    field_id INT(10),
    field_value VARCHAR(155),
    eventdate DATE
);

CREATE INDEX psf ON phenotypes(phenotype, field_id, eventdate);
```

#### First event

The `phenotype_first` table stores the first date of diagnoses (incident or prevalent)
by phenotype and data field. The `field_id` column denotes the UK Biobank field
identifier that the phenotype data were derived from i.e. a value of `20002` would denote
a diagnoses based on data from the non-cancer self reported [field](http://biobank.ctsu.ox.ac.uk/crystal/field.cgi?id=20002). 

```sql
DROP TABLE IF EXISTS phenotype_first;
CREATE TABLE phenotype_first AS
SELECT
    eid,
    phenotype,
    field_id,
    MIN(eventdate) AS eventdate
FROM
    phenotypes
GROUP BY eid, phenotype, field_id;

CREATE INDEX r ON phenotype_first(eid, phenotype, field_id);
```

We set the `eventdate` to participant DOB for events where the participant
has supplied an age of diagnosis of 0.

```sql
UPDATE 
  baseline_cohort b,
  phenotype_first p 
SET
  p.eventdate = b.dob
WHERE b.eid = p.eid
AND p.eventdate <= b.dob 
AND p.eventdate NOT IN ('1900-01-01', '1901-01-01');
```


#### Baseline cohort

The `baseline_cohort` table stores baseline characteristics for all patients for quick lookup
and contains any exclude flags.


| UK Biobank field id | Table column | Desciption | 
|---------------------|------------|--------------|
| 31 | f31 | Sex  | 
| 34 | f34 | Year of birth  | 
| 52 | f52 | Month of birth  | 
| 53 | f53 | Date attending assessment center |
| 54 | f54 | Assessment centre identifier |  
| 21003 | f21003 | Age at assessment centre | 
| 189 | f189 | Deprivation at recruitment | 
| 21001 | f21001 | BMI | 
| 50 | f50 | Height | 
| 21002 | f21002 | Weight | 
| 95 | f95 | Systolic blood pressure | 
| 94 | f94 | Diastolic blood pressure | 
| 20116 | f20116 | Smoking status | 
| 20117 | f20117 | Alcohol status  | 
| 21000 | f21000 | Ethnic status | 
| 40000 | f40000 | Date of death |
| | country | Country of assessment center, based on assessment center identifier: (E)ngland, (S)cotland (Glasgow, Edinburgh) or (W)ales. | 
| dob | dob | Date of birth (from fields 34 and 52) |
| gp_ehr | gp_ehr | Binary flag if patient has primary care EHR data (populated by checking if the patient exists in the `gp_registrations` table. |
| gp_ehr_data_provider | gp_ehr_data_provider | Primary care data provider code: 1 England Vision, 2 Scotland, 3 England TPP and 4 Wales. Field is NULL when `gp_ehr` is 0. More information on the providers in the [UK Biobank documentation.](http://biobank.ctsu.ox.ac.uk/crystal/crystal/docs/primary_care_data.pdf) | 


```sql
DROP TABLE IF EXISTS baseline_cohort;
CREATE TABLE baseline_cohort AS
    SELECT
        DISTINCT(eid)
    FROM
        baseline;

CREATE INDEX e ON baseline_cohort(eid);

ALTER TABLE baseline_cohort
    ADD COLUMN f31 VARCHAR(50),
    ADD COLUMN f34 VARCHAR(50),
    ADD COLUMN f52 VARCHAR(50),
    ADD COLUMN f53 VARCHAR(50),
    ADD COLUMN f54 VARCHAR(50),
    ADD COLUMN country CHAR(1),
    ADD COLUMN dob DATE,
    ADD COLUMN f21003 VARCHAR(50),    
    ADD COLUMN f189 VARCHAR(50),
    ADD COLUMN f21001 VARCHAR(50),
    ADD COLUMN f50 VARCHAR(50),
    ADD COLUMN f21002 VARCHAR(50),
    ADD COLUMN f95 VARCHAR(50),
    ADD COLUMN f94 VARCHAR(50),
    ADD COLUMN f20116 VARCHAR(50),
    ADD COLUMN f20117 VARCHAR(50),
    ADD COLUMN f21000 VARCHAR(50),
    ADD COLUMN f40000 DATE,
    ADD COLUMN gp_ehr INT(1),
    ADD COLUMN gp_ehr_data_provider INT(1);

UPDATE baseline_cohort c, baseline b
SET c.f31 = b.value
WHERE b.field = 31
AND b.eid = c.eid
AND b.i = 0 
AND b.n = 0;

UPDATE baseline_cohort c, baseline b
SET c.f34 = b.value
WHERE b.field = 34
AND b.eid = c.eid
AND b.i = 0 
AND b.n = 0;

UPDATE baseline_cohort c, baseline b
SET c.f52 = b.value
WHERE b.field = 52
AND b.eid = c.eid
AND b.i = 0 
AND b.n = 0;

UPDATE baseline_cohort c, baseline b
SET c.f53 = b.value
WHERE b.field = 53
AND b.eid = c.eid
AND b.i = 0 
AND b.n = 0;

UPDATE baseline_cohort c, baseline b
SET c.f21003 = b.value
WHERE b.field = 21003
AND b.eid = c.eid
AND b.i = 0 
AND b.n = 0;

UPDATE baseline_cohort c, baseline b
SET c.f189 = b.value
WHERE b.field = 189
AND b.eid = c.eid
AND b.i = 0 
AND b.n = 0;

UPDATE baseline_cohort c, baseline b
SET c.f21001 = b.value
WHERE b.field = 21001
AND b.eid = c.eid
AND b.i = 0 
AND b.n = 0;

UPDATE baseline_cohort c, baseline b
SET c.f50 = b.value
WHERE b.field = 50
AND b.eid = c.eid
AND b.i = 0 
AND b.n = 0;

UPDATE baseline_cohort c, baseline b
SET c.f21002 = b.value
WHERE b.field = 21002
AND b.eid = c.eid
AND b.i = 0 
AND b.n = 0;

UPDATE  baseline_cohort c, baseline b
SET c.f94 = b.value
WHERE b.field = 94
AND b.eid = c.eid
AND b.i = 0 
AND b.n = 0;

UPDATE baseline_cohort c, baseline b
SET c.f95 = b.value
WHERE b.field = 95
AND b.eid = c.eid
AND b.i = 0 
AND b.n = 0;

UPDATE baseline_cohort c, baseline b
SET c.f20116 = b.value
WHERE b.field = 20116
AND b.eid = c.eid
AND b.i = 0 
AND b.n = 0;

UPDATE baseline_cohort c, baseline b
SET c.f20117 = b.value
WHERE b.field = 20117
AND b.eid = c.eid
AND b.i = 0 
AND b.n = 0;

UPDATE baseline_cohort c, baseline b
SET c.f21000 = b.value
WHERE b.field = 21000
AND b.eid = c.eid
AND b.i = 0 
AND b.n = 0;

UPDATE baseline_cohort c, baseline b
SET c.f54 = b.value
WHERE b.field = 54
AND b.eid = c.eid
AND b.i = 0 
AND b.n = 0;

UPDATE baseline_cohort c
SET c.country = IF( -- Glasgow, Edinburgh
                    c.f54 IN (11005, 11004), 'S', 
                   -- Cardiff, Swansea, Wrexham
                   IF(c.f54 IN (11003, 11022, 11023), 'W', 
                   'E'));

UPDATE baseline_cohort c, baseline b
SET c.f40000 = b.value
WHERE b.field = 40000
AND b.eid = c.eid
AND b.i = 0 
AND b.n = 0;

UPDATE baseline_cohort c
SET c.dob = STR_TO_DATE(
    CONCAT(f34, '-', f52, '-', 15),
    '%Y-%m-%d'
);

UPDATE baseline_cohort c, gp_registrations g
SET c.gp_ehr = 1 WHERE c.eid = g.eid;

UPDATE baseline_cohort c
SET c.gp_ehr = 0 WHERE c.gp_ehr IS NULL;

UPDATE baseline_cohort c, gp_registrations g
SET c.gp_ehr_data_provider = g.data_provider
WHERE c.eid = g.eid;
```



