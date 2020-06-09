"""
expando
"""

import click
import enum
from dataclasses import dataclass, field
from typing import Optional, Set, List, Tuple, Dict, Any
import csv

DEFAULT = 'default'


class DuplicateHandling(enum.Enum):
    STRICT = 1
    MERGE = 2
    OVERWRITE = 3


@dataclass
class Expander():

    lookup_tables : Dict[str, Dict[str,str]] = field(default_factory=dict)
    default_table : str = DEFAULT

    def expand_term(self, term : str, table : Optional[str] = None) -> str:
        """
        :param term: term to expand
        :param table: name of table
        :return: string representation of list
        """
        if table is None:
            table = self.default_table
        d = self.lookup_tables[table]
        if term in d:
            return d[term]
        else:
            return term


    def expand_text(self, text: str, table: Optional[str] = None, sep=' ', in_place = True) -> str:
        """
        tokenize text into terms, expand tokens, concatenate

        :param text: text to be expanded
        :param table: expansion table to use
        :param sep: token separator
        :return:
        """
        if in_place:
            toks = [self.expand_term(x, table) for x in text.split(sep)]
        else:
            toks = []
            for x in text.split(sep):
                toks.append(x)
                x2 = self.expand_term(x, table)
                if not x2 == x:
                    toks.append(x2)
        return sep.join(toks)

    def expand_file(self, file: str, table: Optional[str] = None, sep=' ', in_place = True) -> str:
        """
        as expand_text(), on a file

        :param file:
        :param table:
        :param sep:
        :return:
        """
        with open(file, "r") as s:
            for line in s.readlines():
                x = self.expand_text(line.rstrip(), table, sep=sep, in_place=in_place)
                print(x)

    def expand_tsv(self, file: str, table: Optional[str] = None,
                   column_map: Dict[str,Optional[str]] = None,
                   auto_header=False,
                   in_place = True,
                   sep='\t') -> str:
        """
        Expands columns in a TSV

        :param file:
        :param table:
        :param column_map: map between column names and index names
        :param in_place:
        :param sep:
        :return:
        """
        hdr = None
        hdr_ix = []
        with open(file) as fd:
            rd = csv.reader(fd, delimiter=sep)
            for row in rd:
                in_hdr = False
                if hdr is None:
                    hdr = {row[i]:i for i in range(len(row))}
                    hdr_index = {i:row[i] for i in range(len(row))}
                    in_hdr = True
                vs = []
                for i in range(len(row)):
                    v = row[i]
                    v_orig = v
                    if i in hdr_index:
                        c = hdr_index[i]
                    else:
                        c = ''
                    if column_map is not None:
                        if c in column_map:
                            tbl = column_map[c]

                            if in_hdr:
                                v = f'{v}_{tbl}'
                            else:
                                v = self.expand_term(v, tbl)
                    else:
                        # expand all
                        if in_hdr:
                            v = f'{v}_expanded'
                        else:
                            v = self.expand_term(v)
                    if in_place:
                        if column_map is None:
                            if v != v_orig:
                                v = f'{v_orig} ! {v}'
                        else:
                            vs.append(v_orig)
                    vs.append(v)
                print(sep.join(vs))

    def load_table(self, file: str, table: str = DEFAULT, sep='\t', valsep=None, duplicate_mode=DuplicateHandling.STRICT) -> None:
        """
        loads a lookup table from a 2-column TSV

        :param file: tab-separated file
        :param table: name of table
        :param sep: column separator
        :return: None
        """
        d={}
        with open(file) as fd:
            rd = csv.reader(fd, delimiter=sep)
            for row in rd:
                self.insert_pair(row[0], row[1], d, valsep=valsep)
        self.lookup_tables[table] = d

    def load_pairs(self, pairs: List[Tuple[str,str]], table: str = DEFAULT, sep='\t', valsep=None,
                   duplicate_mode=DuplicateHandling.STRICT) -> None:
        if table in self.lookup_tables:
            d = self.lookup_tables[table]
        else:
            d = {}
        for (k,v) in pairs:
            self.insert_pair(k, v, d, valsep=valsep)
        self.lookup_tables[table] = d

    def insert_pair(self, k: str, v: str, d: Dict[str,str], valsep:str = None,
                    duplicate_mode=DuplicateHandling.STRICT) -> None:
        if valsep is not None:
            v = v.split(valsep)

        if k in d:
            if duplicate_mode == DuplicateHandling.STRICT:
                raise Exception(f'Duplicate key {k}')
            elif duplicate_mode == DuplicateHandling.MERGE:
                d[k] = f'{d[k]}|{k}'
            else:
                d[k] = v
        else:
            d[k] = v

@click.group()
def cli():
    pass


@cli.command()
@click.option("-t", "--table",
              help="lookup table")
@click.option("-s", "--separator", default=' ',
              help="token separator")
@click.argument('files', nargs=-1)
def text(table, files, separator):
    """ expando """
    x = Expander()
    x.load_table(table)
    for file in files:
        x.expand_file(file, sep=separator)

@cli.command()
@click.option("-t", "--table",
              help="lookup table")
@click.option("-T", "--named-table", multiple=True,
              help="lookup table")
@click.option("-C", "--column_map", multiple=True,
              help="lookup table")
@click.option("-s", "--separator", default='\t',
              help="token separator")
@click.option("-x", "--in-place/--no-in-place", default=False,
              help="token separator")
@click.argument('files', nargs=-1)
def tsv(table, named_table,column_map, in_place, separator, files):
    """ expando """
    x = Expander()
    if table is not None:
        x.load_table(table)
    for t in named_table:
        [n, f] = t.split(':')
        x.load_table(f, table=n)
    cmap = None
    if column_map:
        cmap = {}
        for c_arg in column_map:
            [c,t] = c_arg.split(':')
            cmap[c] = t
    for file in files:
        x.expand_tsv(file, column_map=cmap, in_place=in_place, sep=separator)


if __name__ == '__main__':
    cli()
