""" Tests for phenotype module wrapper. """

import pytest
from pomegranate.phenotype import Phenotype
from pomegranate.exceptions import GenericException


def test_create_ok():
    phenotype = Phenotype('asthma')
    assert phenotype


def test_fields_stuff():
    phenotype = Phenotype('asthma')
    m = [22167, 22127, 6152, 20002, 41202, 41204, 40001, 40002, 42040]
    assert phenotype.get_definition_fields() == m

    assert phenotype.get_values_for_field(20002) == ['1111']

    phenotype = Phenotype('av_block_1')
    assert phenotype.get_values_for_field(41204) == ['I440']

    phenotype = Phenotype('AKI')
    assert phenotype.get_field_definition(42040) is None


def test_create_bad():

    with pytest.raises(GenericException):
        phenotype = Phenotype('NOPE')


def test_incident_prevalent():
    phenotype = Phenotype('asthma')
    assert phenotype.get_values_for_field(42040, type='prevalent') == ['14B4.']
    assert '14B4.' not in phenotype.get_values_for_field(42040, type='any')

    # Ptosis does not have any prevalent primary care diagnosis terms.
    phenotype = Phenotype('ptosis')
    assert phenotype.get_values_for_field(42040, type='prevalent') == []
