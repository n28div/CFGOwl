import argparse
import json
from utils.perturbate_grammar import perturbate
from converter.grammar import convert as g_convert
from converter.sequence import convert as s_convert
from converter.cfg_classification import convert as cfg_convert
import rdflib
from rdflib.extras.infixowl import Ontology
import tempfile
import subprocess
import re
import datetime
import matplotlib.pyplot as plt
import pandas as pd
from tqdm.auto import tqdm
from utils.cfg import parse
from time import time

NS = rdflib.Namespace("http://example.org/")
CLASSIFICATION_TIME = re.compile(r"(main\s+\|\s+)(\d+)")
AXIOMS = re.compile(r"(?<=\nAxioms = )(.*)\n")

def test_cfgdl(rules, seq, pellet):
  g_converted = g_convert(rules)
  s_converted = s_convert(seq)

  graph = rdflib.Graph()
  Ontology(graph=graph)
  graph.parse(data=g_converted)
  graph.parse(data=s_converted)
  tf = tempfile.NamedTemporaryFile()  
  graph.serialize(tf.name)
  
  out = subprocess.run(f"{pellet} extract -v -s \"AllStatements\" {tf.name}", stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
  time_taken = int(CLASSIFICATION_TIME.search(out.stderr.decode()).groups()[1]) / 1000
  
  out = subprocess.run(f"{pellet} info {tf.name}", stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
  axioms = int(AXIOMS.search(out.stdout.decode()).groups()[0])
  return time_taken, axioms

def test_cfgdl_hybrid(rules, seq, pellet, cfg_c):
  g_converted = g_convert(rules)
  s_converted = s_convert(seq)
  cfg_c_converted = cfg_convert(cfg_c, all_classes=list(rules.keys()))

  graph = rdflib.Graph()
  Ontology(graph=graph)
  graph.parse(data=g_converted)
  graph.parse(data=s_converted)
  graph.parse(data=cfg_c_converted)
  tf = tempfile.NamedTemporaryFile()  
  graph.serialize(tf.name)
  
  out = subprocess.run(f"{pellet} extract -v -s \"AllStatements\" {tf.name}", stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
  time_taken = int(CLASSIFICATION_TIME.search(out.stderr.decode()).groups()[1]) / 1000
  
  out = subprocess.run(f"{pellet} info {tf.name}", stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
  axioms = int(AXIOMS.search(out.stdout.decode()).groups()[0])
  return time_taken, axioms

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("-g", "--grammar", required=True)
  parser.add_argument("-e", "--ebnf", required=True)
  parser.add_argument("-s", "--sequence", required=True)
  parser.add_argument("-p", "--pellet", default="./openllet/bin/openllet")
  parser.add_argument("--add-productions", default=10, type=int)
  parser.add_argument("--add-productions-step", default=1, type=int)
  args = parser.parse_args()

  mapping = dict()
  with open(args.grammar) as f:
    mapping = json.load(f)
  with open(args.ebnf) as f:
    ebnf = f.read()

  stats = {
    "added_productions": [0],
    "total_productions": [],
    "cfg_time_taken": [],
    "cfgdl_time_taken": [],
    "cfgdl_total_axioms": [],
    #"h_cfgdl_time_taken": [],
    #"h_cfgdl_total_axioms": []
  }

  # compute without perturbation
  original_rules = mapping["rules"]
  stats["total_productions"].append(sum(map(len, original_rules.values())))
  taken, axioms = test_cfgdl(original_rules, args.sequence, args.pellet)
  stats["cfgdl_time_taken"].append(taken)
  stats["cfgdl_total_axioms"].append(axioms)
  
  # time cfg
  start_s = time()
  cfg_parsed = parse(ebnf, args.sequence.split(" "))
  end_s = time()
  stats["cfg_time_taken"].append(end_s - start_s)

  # time hybrid
  #taken, axioms = test_cfgdl_hybrid(original_rules, args.sequence, args.pellet, cfg_parsed)
  #stats["h_cfgdl_time_taken"].append(taken)
  #stats["h_cfgdl_total_axioms"].append(axioms)
  
  for additional_rules in tqdm(range(1, args.add_productions + 1, args.add_productions_step)):
    # perturbate
    noisy_rules, added = perturbate(original_rules, additional_rules=additional_rules, n_rhss=10)
    stats["added_productions"].append(additional_rules)
    
    # compute for cfg-dl
    stats["total_productions"].append(sum(map(len, noisy_rules.values())))
    taken, axioms = test_cfgdl(noisy_rules, args.sequence, args.pellet)
    stats["cfgdl_time_taken"].append(taken)
    stats["cfgdl_total_axioms"].append(axioms)
    
    # compute for cfg
    new_ebnf = ebnf + "\n" + "\n".join([f"{a} -> " + " | ".join(noisy_rules[a]) for a in added])
    start_s = time()
    cfg_parsed = parse(new_ebnf, args.sequence.split(" "))
    end_s = time()
    stats["cfg_time_taken"].append(end_s - start_s)

    # compute for hybrid cfg-dl
    #taken, axioms = test_cfgdl_hybrid(noisy_rules, args.sequence, args.pellet, cfg_parsed)
    #stats["h_cfgdl_time_taken"].append(taken)
    #stats["h_cfgdl_total_axioms"].append(axioms)
    
  df = pd.DataFrame(data=stats)
  
  df.plot(x="added_productions", 
          y=["cfgdl_time_taken", "cfg_time_taken"], 
          xlabel="Number of added productions in $G$", 
          ylabel="Time taken (s)",
          label=["CFG-DL", "CFG"],
          legend=True).get_figure().savefig("time_complexity_productions.png")
  df.plot(x="added_productions", 
          y="cfgdl_total_axioms", 
          xlabel="Number of added productions in $G$", 
          ylabel="Total axioms in the resulting ontology", 
          legend=False).get_figure().savefig("total_axioms.png")
