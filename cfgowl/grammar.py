from typing import Dict, Union, List, Tuple

from lark import Lark, Visitor, Token, Tree
from lark.parsers.cyk import to_cnf, Grammar as CYKGrammar
from lark.load_grammar import Grammar


def dfs(node: Union[Tree, Token], 
        partial: List[Union[Tree, Token]], 
        paths: List[List[Token]]):
  """
  Extract all the paths from the root to a leaf and add 
  it to the `paths`

  Args:
      node (Union[Tree, Token]): Root node
      partial (List[Union[Tree, Token]]): List to accumulate nodes
      paths (List[Union[Tree, Token]]): Set of paths from root to leaves.
  """
  if hasattr(node, "children"):
    for child in node.children:
      dfs(child, partial + [node.data], paths)
  else:
    paths.append(partial + [node])


class Grammar(object):
  def __init__(self, grammar: str):
    """
    Initialise a grammar that will then be converted into OWL.

    Args:
        grammar (str): Grammar in Lark format.
    """
    cyk = Lark(grammar, parser="cyk")
    cyk_cnf = to_cnf(cyk.parser.parser.parser.grammar)
    self._cnf = [(r.lhs.name if type(r.lhs.name) is str else r.lhs.name.value, tuple(rhs.name for rhs in r.rhs)) 
                 for r in cyk_cnf.rules]

  @property
  def parser(self) -> Lark:
    raise NotImplementedError

  @property
  def cnf(self) -> Grammar:
    """
    Returns:
        Grammar: Returns the grammar in Chomsky Normal Form
    """
    return self._cnf

  def parse(self, seq: str) -> List[Tuple[str, List[str]]]:
    """
    Parse the sequence using the grammar.

    Args:
        seq (str): Input sequence.

    Returns:
        List[Tuple[str, List[str]]]: Class of each element in the sequence.
    """
    tree = self.parser.parse(seq)
    # extract all ancestors of each leaf
    paths = []
    dfs(tree, [], paths)

    # convert paths to tuple of the form
    # (element, [list of classes])
    return [ (str(p[-1]), list(map(str, p[:-1]))) for p in paths ]


class CFG(Grammar):
  def __init__(self, grammar: str):
    """
    Initialise a Context Free Grammar using Earley parser.

    Args:
        grammar (str): Context free grammar in Lark syntax.
    """
    super().__init__(grammar)
    self._parser = Lark(
      grammar,
      parser="earley",
      keep_all_tokens=True,
      propagate_positions=False,
      maybe_placeholders=False,
    )

  @property
  def parser(self) -> Lark:
    """
    Returns:
        Lark: Return the CFG parser
    """
    return self._parser

