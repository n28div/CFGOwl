import nltk

def classify(tree, c, path=[]):
  for child in tree:
    if type(child) == str:
      c.append((child, path))
    else:
      newpath = path + [child.label()] if child.label() != "S" else path
      classify(child, c, path=newpath)

def parse(ebnf, sequence):
  grammar = nltk.CFG.fromstring(ebnf)
  starting_alone = [str(p.lhs()) for p in filter(lambda p: len(p.rhs()) == 2, grammar.productions())]
  starting_recursive = [f"{s} S" for s in starting_alone]
  starting_symbol = " | ".join(starting_alone) + " | " + " | ".join(starting_recursive)
  ebnf = "S -> " + starting_symbol + "\n" + ebnf
  grammar = nltk.CFG.fromstring(ebnf)

  parser = nltk.parse.EarleyChartParser(grammar)
  tree = next(parser.parse(sequence))
  
  c = []
  classify(tree, c)
  return c