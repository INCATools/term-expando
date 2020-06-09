"""
Creates an index from an ontology

A number of different indexes can be created: IDs to ancestors, names to IDs...

All indexes are from a string to a list of strings
"""

import click
from dataclasses import dataclass, field
from typing import Optional, Set, List, Tuple, Union, Dict, Any, IO
from term_expando import Expander
import sys

from ontobio import Ontology, OntologyFactory

@dataclass
class OntolIndexer():

    ontology: Optional[Ontology] = None
    relations: Optional[List[str]] = None
    out: IO = sys.stdout
    pairs: List[Tuple[str,str]] = field(default_factory=list)

    def save(self):
        """saves the index as a tsv"""
        for (src, tgts) in self.pairs:
            self.out.write(f'{src}\t{tgts}\n')

    def gen(self, src, tgts):
        self.pairs.append((src,"|".join(tgts)))

    def gen_closure(self) -> None:
        """
        generates a closure (ancestor) index
        """
        ont = self.ontology
        if len(self.relations) > 0:
            ont = ont.subontology(relations=self.relations)
        for n in ont.nodes():
            if ont.get_node_type(n) == "CLASS":
                ancs = ont.ancestors(n)
                self.gen(n, ancs)

    def gen_id2name(self):
        """
        generates an index mapping IDs to names (labels)
        """
        ont = self.ontology
        for n in ont.nodes():
            if ont.get_node_type(n) == "CLASS":
                lbl = ont.label(n)
                if lbl is not None:
                    self.gen(n, [lbl])

    def gen_id2alias(self):
        """
        generates an index mapping IDs to names + synonyms
        """
        ont = self.ontology
        for n in ont.nodes():
            if ont.get_node_type(n) == "CLASS":
                xs = [x.val for x in ont.synonyms(n)]
                lbl = ont.label(n)
                if lbl is not None:
                    xs.append(lbl)
                self.gen(n, xs)

    def gen_name2id(self):
        """
        generates an index mapping names to IDs
        """
        ont = self.ontology
        for n in ont.nodes():
            if ont.get_node_type(n) == "CLASS":
                lbl = ont.label(n)
                if lbl is not None:
                    self.gen(lbl, [n])

    def load_from_files(self, files: List[str]) -> None:
        """
        loads an ontology from an obojson file
        :param files: list of fils in obojson format
        :return:
        """
        factory = OntologyFactory()
        ont = None
        for file in files:
            if ont == None:
                ont = factory.create(file)
            else:
                ont.merge(factory.create(file))
        self.ontology = ont

@click.group()
def cli():
    pass

@cli.command()
@click.option("-r", "--relation", multiple=True)
@click.argument('files', nargs=-1)
def closure(files, relation):
    """ generate index from ontology """
    x = OntolIndexer(relations=list(relation))
    x.load_from_files(files)
    x.gen_closure()
    x.save()

@cli.command()
@click.argument('files', nargs=-1)
def id2name(files):
    """ generate index from ontology """
    x = OntolIndexer()
    x.load_from_files(files)
    x.gen_id2name()
    x.save()

@cli.command()
@click.argument('files', nargs=-1)
def id2alias(files):
    """ generate index from ontology """
    x = OntolIndexer()
    x.load_from_files(files)
    x.gen_id2alias()
    x.save()


@cli.command()
@click.argument('files', nargs=-1)
def name2id(files):
    """ generate index from ontology """
    x = OntolIndexer()
    x.load_from_files(files)
    x.gen_name2id()
    x.save()

if __name__ == '__main__':
    cli()
