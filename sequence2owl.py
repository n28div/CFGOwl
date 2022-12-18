import argparse
import json
from converter.sequence import convert

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("-s", "--sequence", required=True)
  args = parser.parse_args()
  converted = convert(args.sequence)
  print(converted)