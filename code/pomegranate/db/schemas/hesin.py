""" SQL schema for the 'hesin' table. """

SCHEMA_HESIN = """
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

CREATE INDEX h ON hesin(eid, ins_index);
"""
