import argparse
import json
from converter.grammar import convert

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("-m", "--mapping", required=True)
  args = parser.parse_args()

  mapping = dict()
  with open(args.mapping) as f:
    mapping = json.load(f)

  converted = convert(mapping["rules"])
  print(converted)