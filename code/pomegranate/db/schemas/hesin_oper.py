""" SQL schema for the 'hesin_oper' table. """

SCHEMA_HESIN_OPER = """
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

CREATE INDEX hesr ON hesin_oper(eid, ins_index, level, oper4);
"""
