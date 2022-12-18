import argparse
import rdflib

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("-i", "--input", nargs="+", required=True)
  args = parser.parse_args()
  
  graph = rdflib.Graph()
  for i in args.input:
    graph.parse(i)

  print(graph.serialize(format="turtle"))