# -*- coding: utf-8 -*-

"""Command line interface for term-expando.


.. seealso:: http://click.pocoo.org/5/setuptools/#setuptools-integration
"""

import logging
import os
import sys
import time
from io import StringIO
from typing import List, Optional
from term_expando import Expander, OntolIndexer

import click

logger = logging.getLogger(__name__)


indexer = OntolIndexer()
expander = Expander()
@click.group(help="term-expando CLI on {}".format(sys.executable))
@click.version_option()
@click.option('-l', '--load', multiple=True)
@click.option('-e', '--operation', multiple=True)
@click.option("-t", "--table",
              help="lookup table")
@click.option("-T", "--named-table", multiple=True,
              help="lookup table")
def main(table, named_table, operation, load):
    """Command line interface for term-expando."""
    if table is not None:
        expander.load_table(table)
    for t in named_table:
        [n, f] = t.split(':')
        expander.load_table(f, table=n)
    if len(load) > 0:
        indexer.load_from_files(load)
        if len(operation) == 0:
            logging.warning("no --operation supplied, assuming id2name")
            operation = ['id2name']
    for op in operation:
        func = getattr(indexer, f'gen_{op}')
        func()
    expander.load_pairs(indexer.pairs)
    for k in expander.lookup_tables:
        print(f'Index: {k} Size: {len(expander.lookup_tables[k])}')

@main.command()
@click.option("-C", "--column_map", multiple=True,
              help="lookup table")
@click.option("-s", "--separator", default='\t',
              help="token separator")
@click.option("-x", "--in-place/--no-in-place", default=False,
              help="token separator")
@click.option("-A", "--auto-header/--no-no-auto-header", default=False,
              help="token separator")
@click.argument('files', nargs=-1)
def tsv(column_map, in_place, auto_header, separator, files):
    """ expand terms in a TSV """
    cmap = None
    if column_map:
        cmap = {}
        for c_arg in column_map:
            [c,t] = c_arg.split(':')
            cmap[c] = t
    for file in files:
        expander.expand_tsv(file, column_map=cmap, in_place=in_place,
                            auto_header=auto_header, sep=separator)

@main.command()
@click.option("-s", "--separator", default=' ',
              help="token separator")
@click.option("-x", "--in-place/--no-in-place", default=False,
              help="token separator")
@click.argument('files', nargs=-1)
def text(in_place, separator, files):
    """ expand terms in a text file """
    for file in files:
        expander.expand_file(file, in_place=in_place, sep=separator)


if __name__ == '__main__':
    main()
