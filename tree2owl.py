import argparse
import yaml
from converter.convert import convert

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("-i", "--input", required=True)
  parser.add_argument("-m", "--mapping", required=True)
  args = parser.parse_args()

  with open(args.input) as f:
    tree_str = f.read()

  with open(args.mapping) as f:
    mapping = yaml.safe_load(f)

  # extract concepts mapping
  #concepts_mapping = {k:v for m in mapping["concepts"] for k,v in m.items()}
  
  converted = convert(tree_str, {})
  print(converted)