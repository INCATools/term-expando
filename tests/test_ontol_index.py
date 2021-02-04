# -*- coding: utf-8 -*-

"""Test the module can be imported."""

import unittest
from term_expando import Expander, OntolIndexer
from pathlib import Path
import os
from util import datafile

TBL = 'my'
class TestOntolIndex(unittest.TestCase):
    """A test case for import tests."""

    expander = Expander()

    def setUp(self):
        oi  = OntolIndexer()
        p = datafile("nucleus.json")

        oi.load_from_files([p])
        oi.gen_name2id()
        self.expander.load_pairs(oi.pairs, table=TBL)
        self.expander.default_table = TBL

    def test_expand(self):
        """Test basic expansion functionality."""

        x = self.expander
        for n,d in x.lookup_tables.items():
            print(f'T:{d} ==> {len(d.keys())}')
        for k in ['cell', 'nucleus', 'chromosome', 'unknown']:
            print(f'Exp({k}) == {x.expand_term(k)}')
        assert x.expand_term('cell') == 'GO:0005623'
        assert x.expand_term('u') == 'u'
        txt = "blah cell nucleus intracellular foo cell part intracellular organelle"
        txt2 = x.expand_text(txt, in_place=True, sep=' ')
        assert txt2 == "blah GO:0005623 GO:0005634 GO:0005622 foo GO:0005623 part GO:0005622 GO:0043226"
