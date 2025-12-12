""" Config file for phenotypes definition files and other stuff. """

ONTOLOGIES_FIELDS = {
    'DOID': 'Disease Ontology Identifier',
    'GWAS': 'Genome-Wide Association Study (GWAS) catalog identifier',
    'MESH': 'MEdical Subject Headings identifier',
    'SNOMED-CT': 'Systematized Medical Nomenclature for Medicine–Clinical Terminology (SNOMED-CT) identifier',
    'FINNGEN': 'FinnGen project (Finnish Genetics) identifier',
}

METADATA_FIELDS = {
    'phenotype': 'Name of phenotype',
    'group': 'Top-level disease group',
    'is_cancer': 'Flag to denote if phenotype is cancer-related',
    'is_adult': 'Flag to denote if phenotype applies only to adults',
    'variable_name': 'Phenotype short name',
    'gender': 'Valid sex',
    'authors': 'List of phenotype authors',
    'uuid': 'Unique identifier',
    'priority': 'Priority',
    'ontologies': 'Mapping for ontologies',
    'short_desc': 'Short description',
    'long_desc': 'Long description',
}

METADATA_OPTIONAL_FIELDS = {
    'complex_logic': 'Dict containing description of complex logic and name of Implementation function',
    'created_by': 'Script and settings used to create phenotype file',
    'date_created': 'Date phenotype file was created.',
}

CODE_FIELDS = {
    'code': 'Code (could be from any ontology)',
    'value': 'Code description',
    'ontology': 'Ontology code belongs to, e.g. read, snomed, bnf, dmd, etc',
    'type': 'Prevalence status: does this represent an incident or prevalent event',
    'group': 'Group that the code belongs to (for complex phenotypes only)',
}
