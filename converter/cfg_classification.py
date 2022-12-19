from typing import Dict, Union
import rdflib
from rdflib.extras.infixowl import Class, Restriction, Ontology
from rdflib import OWL, RDF, RDFS
import re
from more_itertools import pairwise
import urllib

NS = rdflib.Namespace("http://example.org/")


def convert(classification, all_classes = []) -> str:
  graph = rdflib.Graph()
  
  next_property = NS["next"]
  graph.add((next_property, RDF.type, OWL.FunctionalProperty))
  
  created_classes = list()
  for i, (s_i, s_n) in enumerate(pairwise(classification)):
    s_i, s_i_classes = s_i
    uri_s_i = NS[urllib.parse.quote_plus(f"element_{i}")]
    s_i_class = NS[urllib.parse.quote_plus(s_i)]
    s_i_classes = [NS[urllib.parse.quote_plus(x)] for x in s_i_classes]
    if s_i not in created_classes:
      graph.add((s_i_class, RDF.type, OWL.Class))
      created_classes.append(s_i)
    graph.add((uri_s_i, RDF.type, s_i_class))
    for s_i_c in s_i_classes:
      if s_i_c not in created_classes:
        graph.add((s_i_c, RDF.type, OWL.Class))
        created_classes.append(s_i_c)
      graph.add((uri_s_i, RDF.type, s_i_c))
        
    s_n, s_n_classes = s_n
    uri_s_n = NS[urllib.parse.quote_plus(f"element_{i + 1}")]
    s_n_class = NS[urllib.parse.quote_plus(s_n)]
    s_n_classes = [NS[urllib.parse.quote_plus(x)] for x in s_n_classes]
    if s_n not in created_classes:
      graph.add((s_n_class, RDF.type, OWL.Class))
      created_classes.append(s_n)
    graph.add((uri_s_n, RDF.type, s_n_class))
    for s_n_c in s_i_classes:
      if s_n_c not in created_classes:
        graph.add((s_n_c, RDF.type, OWL.Class))
        created_classes.append(s_n_c)
      graph.add((uri_s_i, RDF.type, s_n_c))

    graph.add((uri_s_i, next_property, uri_s_n))

  return graph.serialize(format="turtle")