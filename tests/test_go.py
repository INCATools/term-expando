# -*- coding: utf-8 -*-

"""Test the module can be imported."""

import unittest
import os
from term_expando import Expander
from util import datafile

expected = {
    'a': 'a1|a2|a3'
}

class TestExpandGAF(unittest.TestCase):
    """A test case for import tests."""

    def test_expand_gaf(self):
        """Test basic expansion functionality."""
        x = Expander()
        x.load_table(datafile("go-small-id2name.tsv"))
        x.expand_tsv(datafile("pombase-small.gaf"), in_place=True)
