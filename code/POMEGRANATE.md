# pomegranate-ukbiobank


Quick start

1. ### Introduction to the project
See README.md 

2. ### Complete steps to set up the pomegranate environment and the database 
See TECHSTACK.md

The script are_we_connected.py will tell you if the environment and the database connection have been succesfully setup: 


```
python ops/are_we_connected.py 

```

3. ### Executing phenotypes

The main ETL script used to extract execute phenotypes is extract_phenotype.py which extracts data from individual UK Biobank fields and populates the phenotypes database table.

The script can be used to define a phenotype entirely:

```
python extract_phenotype.py -p=asthma --testing

```


The --refresh flag will drop all existing data points for a given phenotype and re-execute and insert the data points in the phenotypes table:

```
python extract_phenotype.py -p=asthma --refresh

```


4. ### Defining first events

The script define_first_events.py is used to populate the table phenotype_first which contains the earliest event date for each phenotype called.


The script needs to be re-run when there's been a edit to a phenotype definition or some other change that could affect how earlier events are being defined.

