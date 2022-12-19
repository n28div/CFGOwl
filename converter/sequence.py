from typing import Dict, Union
import rdflib
from rdflib.extras.infixowl import Class, Restriction, Ontology
from rdflib import OWL, RDF, RDFS
import re
from more_itertools import pairwise
import urllib

NS = rdflib.Namespace("http://example.org/")


def convert(sequence: str) -> str:
  """
  Convert a sequence in OWL.

  Args:
      sequence (str): Input sequence.

  Returns:
      str: Sequence in Turtle syntax.
  """
  graph = rdflib.Graph()
  
  next_property = NS["next"]
  graph.add((next_property, RDF.type, OWL.FunctionalProperty))
  
  sequence = sequence.split(" ")
  created_classes = list()
  for i, (s_i, s_n) in enumerate(pairwise(sequence)):
    s_i_class = NS[urllib.parse.quote(s_i)]
    uri_s_i = NS[urllib.parse.quote_plus(f"element_{i}")]
    s_n_class = NS[urllib.parse.quote(s_n)]
    uri_s_n = NS[urllib.parse.quote_plus(f"element_{i + 1}")]

    if s_i not in created_classes:
      graph.add((s_i_class, RDF.type, OWL.Class))
      created_classes.append(s_i)
    if s_n not in created_classes:
      graph.add((s_n_class, RDF.type, OWL.Class))
      created_classes.append(s_n)

    graph.add((uri_s_i, RDF.type, s_i_class))
    graph.add((uri_s_n, RDF.type, s_n_class))
    graph.add((uri_s_i, next_property, uri_s_n))

  return graph.serialize(format="turtle")