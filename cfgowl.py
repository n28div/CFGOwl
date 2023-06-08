"""
Utility to convert a CFG into OWL and classify a sequence
"""
import argparse
import pathlib

import rdflib

from cfgowl.grammar import CFG
from cfgowl.converter import grammar_to_owl, parsing_result_to_owl

parser = argparse.ArgumentParser(description="CFGOwl utility: convert an ontology and eventually classify a sequence using the same grammar.",)

parser.add_argument("--grammar", "-g", 
                    required=True, 
                    type=argparse.FileType("r", encoding="utf-8"),
                    help="Path to the Lark grammar.")

parser.add_argument("--format", "-f", 
                    required=False, 
                    choices=["json-ld", "n3", "nquads", "nt", "hext", "xml", "turtle", "trig", "trix"],
                    default="xml",
                    help="Format to which the ontology is serialised to. Defaults to xml.")

parser.add_argument("--sequence", "-s",
                    required=False,
                    type=str,
                    help="Sequence to be classified by the grammar and converted in OWL.")

parser.add_argument("--namespace", "-ns",
                    required=False,
                    type=str,
                    default="http://w3id.org/cfgowl/",
                    help="Namespace for the created ontology. Defaults to http://w3id.org/cfgowl/.")

parser.add_argument("--next-iri",
                    required=False,
                    type=str,
                    default="http://www.ontologydesignpatterns.org/cp/owl/sequence.owl#directlyFollows",
                    help="IRI of the predicate used for the next element in a sequence. Defaults to http://www.ontologydesignpatterns.org/cp/owl/sequence.owl#directlyFollows")

parser.add_argument("--previous-iri",
                    required=False,
                    type=str,
                    default="http://www.ontologydesignpatterns.org/cp/owl/sequence.owl#directlyPrecedes",
                    help="IRI of the predicate used for the previous element in a sequence. Defaults to http://www.ontologydesignpatterns.org/cp/owl/sequence.owl#directlyPrecedes")

parser.add_argument("--disable-cfg-axioms",
                    required=False,
                    default=False,
                    action="store_true",
                    help="Disable the formalisation of axioms that allow parsing the sequence using the reasoner.")



if __name__ == "__main__":
  args = parser.parse_args()

  grammar_text = args.grammar.read()
  grammar =  CFG(grammar_text)

  ontology = rdflib.Graph()

  if not args.disable_cfg_axioms:
    ontology += grammar_to_owl(grammar, 
                              namespace=args.namespace, 
                              next_predicate_iri=args.next_iri, 
                              previous_predicate_iri=args.previous_iri)

  if args.sequence:
    parsed = grammar.parse(args.sequence)
    ontology += parsing_result_to_owl(parsed, 
                                      namespace=args.namespace,
                                      next_predicate_iri=args.next_iri)

  print(ontology.serialize(format=args.format))


  
