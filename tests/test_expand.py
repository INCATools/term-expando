# -*- coding: utf-8 -*-

"""Test the module can be imported."""

import unittest
from term_expando import Expander

expected = {
    'a': 'a1|a2|a3'
}

class TestExpand(unittest.TestCase):
    """A test case for import tests."""

    def test_expand(self):
        """Test basic expansion functionality."""
        x = Expander()
        t = 'my'
        x.load_table("data/basic.tsv", t)
        for k in ['a', 'b', 'c', 'unknown']:
            print(f'Exp({k}) == {x.expand_term(k,t)}')

        for k,v in expected.items():
            assert x.expand_term(k,t) == v

    def test_expand_arr(self):
        """Test basic expansion functionality."""
        x = Expander()
        print(f'Expander = {x}')
        t = 'my'
        x.load_table("data/basic.tsv", t, valsep='|')
        for k in ['a', 'b', 'c', 'unknown']:
            print(f'Exp({k}) == {x.expand_term(k,t)}')

        for k,v in expected.items():
            assert x.expand_term(k,t) == v.split('|')

    def test_expand_text(self):
        """Test basic expansion functionality."""
        x = Expander()
        x.load_table("data/basic.tsv")
        for k in ['a', 'b', 'c', 'unknown']:
            print(f'Exp({k}) == {x.expand_term(k)}')
        txt = x.expand_text("foo a bar b boz c biz")
        print(f'Repl={txt}')
        assert txt == 'foo a1|a2|a3 bar b1|b2|b3 boz c biz'

    def test_expand_tsv(self):
        """Test basic expansion functionality."""
        x = Expander()
        x.load_table("data/basic.tsv", "basic")
        x.expand_tsv("data/src.tsv", column_map={'c1': 'basic'}, in_place=True)
