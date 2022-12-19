import argparse
from utils.cfg import parse
from converter.cfg_classification import convert

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("-g", "--grammar", required=True)
  parser.add_argument("-s", "--sequence", required=True)
  args = parser.parse_args()

  mapping = dict()
  with open(args.grammar) as f:
    ebnf = f.read()

  print(convert(parse(ebnf, args.sequence.split(" "))))

