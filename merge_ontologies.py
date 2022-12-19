import argparse
import rdflib
from rdflib.extras.infixowl import Ontology

NS = rdflib.Namespace("http://example.org/")

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("-i", "--input", nargs="+", required=True)
  args = parser.parse_args()
  
  graph = rdflib.Graph()
  Ontology(graph=graph)
  for i in args.input:
    graph.parse(i)

  print(graph.serialize(format="turtle"))