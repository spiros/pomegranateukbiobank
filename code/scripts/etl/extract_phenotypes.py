from pomegranate.cli.etl.extract_phenotype import extract_phenotypes
from pomegranate.db.ukbdb import UKBDatabase

db = UKBDatabase()

phenotypes = ['sec_brain' 'sec_LN' 'av_block_1' 'av_block_2']
n = extract_phenotypes(phenotypes, db, refresh=False)