import argparse
import json
from utils.perturbate_grammar import perturbate
from converter.grammar import convert
import rdflib
from rdflib.extras.infixowl import Ontology
import tempfile
import subprocess
import re
import datetime
import matplotlib.pyplot as plt
import pandas as pd
from tqdm.auto import tqdm

NS = rdflib.Namespace("http://example.org/")
CLASSIFICATION_TIME = re.compile(r"(?<=Classifying finished in )(.*)\n")
AXIOMS = re.compile(r"(?<=\nAxioms = )(.*)\n")

def test(rules, seq, pellet):
  converted = convert(rules)
  graph = rdflib.Graph()
  Ontology(graph=graph)
  graph.parse(data=converted)
  graph.parse(seq)
  tf = tempfile.NamedTemporaryFile()  
  graph.serialize(tf.name)
  
  out = subprocess.run(f"{pellet} realize {tf.name}", stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
  time_taken = datetime.datetime.strptime(CLASSIFICATION_TIME.search(out.stderr.decode()).groups()[0], "%M:%S")
  
  out = subprocess.run(f"{pellet} info {tf.name}", stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
  axioms = AXIOMS.search(out.stdout.decode()).groups()[0]
  return time_taken.second, axioms


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("-g", "--grammar", required=True)
  parser.add_argument("-s", "--sequence", required=True)
  parser.add_argument("-p", "--pellet", default="./openllet/openlletcli/bin/openllet")
  parser.add_argument("--add-productions", default=10, type=int)
  parser.add_argument("--add-productions-step", default=1, type=int)
  args = parser.parse_args()

  mapping = dict()
  with open(args.grammar) as f:
    mapping = json.load(f)

  added_productions = [0]
  total_productions = list()
  time_taken = list()
  total_axioms = list()

  original_rules = mapping["rules"]
  total_productions.append(sum(map(len, original_rules.values())))
  taken, axioms = test(original_rules, args.sequence, args.pellet)
  time_taken.append(taken)
  total_axioms.append(axioms)
  
  for additional_rules in tqdm(range(1, args.add_productions, args.add_productions_step)):
    noisy_rules = perturbate(original_rules, additional_rules=additional_rules, n_rhss=10)
    total_productions.append(sum(map(len, noisy_rules.values())))
    taken, axioms = test(noisy_rules, args.sequence, args.pellet)

    added_productions.append(additional_rules)
    time_taken.append(taken)
    total_axioms.append(axioms)

  print(added_productions)
  df = pd.DataFrame(data={
    "added_productions": added_productions,
    "total_productions": total_productions,
    "time_take": time_taken,
    "total_axioms": total_axioms
  })
  df.to_csv("stress_results.csv")
