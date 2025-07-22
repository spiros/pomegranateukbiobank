# pomegranate-ukbiobank

The algorithms in this repository are described here: 
> Torralbo, A., Davitte, J.M., Croteau-Chonka, D.C. et al. A computational framework for defining and validating reproducible phenotyping algorithms of 313 diseases in the UK Biobank. Sci Rep 15, 24607 (2025). [DOI: 10.1038/s41598-025-05838-9](https://www.nature.com/articles/s41598-025-05838-9)

The [online portal](https://pomegranate.denaxaslab.org/) contains additional information. 


## Phenotype schema (YAML)

Current version: `1.2`

Version | Date | Notes
--- | --- | ---
1.0 | 2020-03-31 | First release
1.1 | 2020-07-01 | Added ontologies in metadata
1.2 | 2020-09-02 | Added priority flag to metadata

### Introduction

The purpose of this document is to provide the YAML specification of phenotype 
definition files.

Each phenotype is defined within a YAML file named using the phenotype variable/stem name i.e. `asthma.yaml`


### Structure

A phenotype YAML file composed by two main sections: 

* the `metadata` section which outlines basic metadata information about an algorithm
* the `definition` section which contains the definition implementation details. 

The `definition` section is structured as a list of key-value entries using UK Biobank field identifiers as keys. The hierarchy is reflected in the structure below:

- YAML file
  - metadata
      - ...
  - definitions
    - field_id
      - metadata
        - ...
      - values
        - ...
    - field_id
      - metadata
        - ...
      - values
        - ...
  
<hr>

### Metadata section

**Example**
```yaml
metadata:
  phenotype: Asthma
  group: Respiratory
  is_cancer: '0'
  is_adult: '1'
  variable_name: asthma
  gender:
  - male
  - female
  authors: Kuan, V; Denaxas, S; Gonzalez-Izquierdo, A; Direk, K; Bhatti, O; Husain,
    S; Sutaria, S; Hingorani, M; Nitsch, D; Parisinos, C; Lumbers, T; Mathur, R; Sofat,
    R; Casas, J; Wong, I; Hemingway, H; Hingorani, A;
  ontologies:
    DOID: DOID_2841
    GWAS: EFO_0000270
    MESH: D001249
    SNOMED-CT: 195967001
    FINNGEN: J10_ASTHMA
  uuid: 018142ee-ed30-416d-97f1-503f4be316c6
  priority: 1
```

The `metadata` section contains top level metadata related to the algorithm.

| Field | Definition |
|-------|------------|
| phenotype | Phenotype name for human consumption (unique) |
| variable_name | Phenotype name for computer consumption (unique) |
| group | Disease high-level group that phenotype belongs to |
| is_cancer | Binary flag, set to `1` if phenotype is a cancer phenotype |
| is_adult | Binary flag, set to `0` if phenotype is a neonatal condition |
| gender | Field outlining any gender restrictions on a phenotype using the [HL7 Administrative Gender coding scheme](https://www.hl7.org/fhir/codesystem-administrative-gender.html) |
| authors | Phenotype authors and lead clinical experts |
| uuid | RFC 4122-compliant UUID identifier (unique) |
| ontologies | Identifiers for DO, MeSH, SNOMECT-CT, and FinnGen |
| priority | Identifies the priority group of the trait. 1 = first batch (n=10), second batch (n=50) etc. This field can be ignored as its for internal consumption. |

### Definitions section

The `definitions` section is composed by a list of key-value entries using UK Biobank field identifiers as the `id` value.

The list of UK Biobank field identifiers has been drawn from the [UK Biobank Showcase](http://biobank.ctsu.ox.ac.uk/crystal/schema.cgi). 

A set of fields has been defined as the `core set` and is defined in all phenotype definitions, irrespective of if the phenotype definition sources information from that field:

| Source | field_id  | Description
|--------|-----------|------------|
| Baseline | 20001 |  cancer self report |
| Baseline | 20002 | non cancer self report |
| Hospital EHR | 41202  | Primary diagnoses |
| Hospital EHR | 41204  | Secondary diagnoses
| Hospital EHR | 41200  | Primary procedures |
| Hospital EHR | 41210  | Secondary procedures |
| Mortality | 40001 | primary mortality |
| Mortality | 40002 | secondary mortality |
| Primary care EHR | 42040 | diagnoses |
| Cancer EHR | 40006 | Cancer registration data |

Each YAML file also contains disease-specific fields which are appended to the ones above. For example, the `asthma` phenotype contains entries for fields related to doctor diagnosed asthma (_Blood clot, DVT, bronchitis, emphysema, asthma, rhinitis, eczema, allergy diagnosed by doctor_ and others).

Each definition entry is composed by two sections: 
  
  * the `metadata` section which outlines basic metadata information about an algorithm
  * the `values` section which contains one or more field values for cases

The `metadata` section contains top level metadata related to the field.

| Field | Definition |
|-------|------------|
| desc | Field description |
| time_qualifier | UK Biobank field id which contains the time qualifier for the given field and the type of the qualifier (can be any of 'year' or 'age') |

For example, for the non-cancer self reported illness codes, the `metadata` section contains:

```yaml
20002:
  metadata:
    desc: Non-cancer illness code, self-reported
    time_qualifier:
      field_id: 20008
      type: year
```

This indicates that the temporal information related to field `20002` are defined in field `20008` (_Interpolated Year when non-cancer illness first diagnosed_ and that this field contains the value which is formatted as a year (YYYY).

Each `value` entry is composed by three values:

* `code` which contains the absolute value the algorithm uses to identify (such as for example an ICD-10 code)
* `value` the lookup value or meaning for the `coded` (such as for example an ICD-10 term or 'Yes')
* `type` flag to indicate the type of event (incident or prevalent)

The hierarchy is reflected in the structure below:

* field_id
  * metadata
  * values
    * code
    * value
    * type
    * [...]

**Notes**

1. Definitions at the moment only include values for cases and not controles i.e. the prescence of one or more of the prespecified values indicates that a patient is a case.
2. Values with the `prevalent` flag set indicate diagnosis terms which refer to historical events or prevalent conditions. This information is recorded on a particular date, usually as part of a consultation, but should not be treated as an incident event.

**Example**
```yaml
42040:
  metadata:
    desc: GP clinical event records
  values:
  - code: 14B4.00
    value: 'H/O: asthma'
    type: prevalent
  - code: 173A.00
    value: Exercise induced asthma
    type: any
  - code: 173c.00
    value: Occupational asthma
    type: any
```

### Example of entire phenotype

```yaml
metadata:
  phenotype: Asthma
  group: Respiratory
  is_cancer: '0'
  is_adult: '1'
  variable_name: asthma
  gender:
  - male
  - female
  authors: Kuan, V; Denaxas, S; Gonzalez-Izquierdo, A; Direk, K; Bhatti, O; Husain,
    S; Sutaria, S; Hingorani, M; Nitsch, D; Parisinos, C; Lumbers, T; Mathur, R; Sofat,
    R; Casas, J; Wong, I; Hemingway, H; Hingorani, A;
  uuid: 018142ee-ed30-416d-97f1-503f4be316c6
definitions:
  20001:
    metadata:
      desc: Cancer code, self-reported
      time_qualifier:
        field_id: 20006
        type: year
    values: []
  20002:
    metadata:
      desc: Non-cancer illness code, self-reported
      time_qualifier:
        field_id: 20008
        type: year
    values:
    - code: '1111'
      value: asthma
      type: any
  20003:
    metadata:
      desc: Treatment/medication code
    values: []
  20004:
    metadata:
      desc: Operation code
    values: []
  41202:
    metadata:
      desc: Diagnoses - main ICD10
    values:
    - code: J45
      value: Asthma
      type: any
    - code: J46
      value: Status asthmaticus
      type: any
  41204:
    metadata:
      desc: Diagnoses - secondary ICD10
    values:
    - code: J45
      value: Asthma
      type: any
    - code: J46
      value: Status asthmaticus
      type: any
  41200:
    metadata:
      desc: Operative procedures - main OPCS4
    values: []
  41210:
    metadata:
      desc: Operative procedures - secondary OPCS4
    values: []
  40001:
    metadata:
      desc: 'Underlying (primary) cause of death: ICD10'
      time_qualifier:
        field_id: 40000
        type: date
    values:
    - code: J45
      value: Asthma
      type: any
    - code: J46
      value: Status asthmaticus
      type: any
  40002:
    metadata:
      desc: 'Contributory (secondary) causes of death: ICD10'
      time_qualifier:
        field_id: 40000
        type: date
    values:
    - code: J45
      value: Asthma
      type: any
    - code: J46
      value: Status asthmaticus
      type: any
  42040:
    metadata:
      desc: GP clinical event records
    values:
    - code: 14B4.00
      value: 'H/O: asthma'
      type: prevalent
    - code: 173A.00
      value: Exercise induced asthma
      type: any
    - code: 173c.00
      value: Occupational asthma
      type: any
    - code: 173d.00
      value: Work aggravated asthma
      type: any
    - code: '1780.00'
      value: Aspirin induced asthma
      type: any
    - code: 1O2..00
      value: Asthma confirmed
      type: any
    - code: '2126200.0'
      value: Asthma resolved
      type: any
    - code: 212G.00
      value: Asthma resolved
      type: any
    - code: H312000
      value: Chronic asthmatic bronchitis
      type: any
    - code: H330000
      value: Extrinsic asthma without status asthmaticus
      type: any
    - code: H330011
      value: Hay fever with asthma
      type: any
    - code: H330100
      value: Extrinsic asthma with status asthmaticus
      type: any
    - code: H330111
      value: Extrinsic asthma with asthma attack
      type: any
    - code: H330.00
      value: Extrinsic (atopic) asthma
      type: any
    - code: H330.11
      value: Allergic asthma
      type: any
    - code: H330.12
      value: Childhood asthma
      type: any
    - code: H330.13
      value: Hay fever with asthma
      type: any
    - code: H330.14
      value: Pollen asthma
      type: any
    - code: H330z00
      value: Extrinsic asthma NOS
      type: any
    - code: H331000
      value: Intrinsic asthma without status asthmaticus
      type: any
    - code: H331100
      value: Intrinsic asthma with status asthmaticus
      type: any
    - code: H331111
      value: Intrinsic asthma with asthma attack
      type: any
    - code: H331.00
      value: Intrinsic asthma
      type: any
    - code: H331.11
      value: Late onset asthma
      type: any
    - code: H331z00
      value: Intrinsic asthma NOS
      type: any
    - code: H332.00
      value: Mixed asthma
      type: any
    - code: H333.00
      value: Acute exacerbation of asthma
      type: any
    - code: H334.00
      value: Brittle asthma
      type: any
    - code: H335.00
      value: Chronic asthma with fixed airflow obstruction
      type: any
    - code: H33..00
      value: Asthma
      type: any
    - code: H33..11
      value: Bronchial asthma
      type: any
    - code: H33z000
      value: Status asthmaticus NOS
      type: any
    - code: H33z011
      value: Severe asthma attack
      type: any
    - code: H33z100
      value: Asthma attack
      type: any
    - code: H33z111
      value: Asthma attack NOS
      type: any
    - code: H33z200
      value: Late-onset asthma
      type: any
    - code: H33z.00
      value: Asthma unspecified
      type: any
    - code: H33z.11
      value: Hyperreactive airways disease
      type: any
    - code: H33zz00
      value: Asthma NOS
      type: any
    - code: H33zz11
      value: Exercise induced asthma
      type: any
    - code: H33zz12
      value: Allergic asthma NEC
      type: any
    - code: H33zz13
      value: Allergic bronchitis NEC
      type: any
  42039:
    metadata:
      desc: GP prescription records
    values: []
  40006:
    metadata:
      desc: 'Type of cancer: ICD10'
      time_qualifier:
        field_id: 40005
        type: date
    values: []
```
