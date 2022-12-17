from typing import Dict
import rdflib
from rdflib.extras.infixowl import Class, Restriction, Ontology
from rdflib import OWL, RDF, RDFS
import nltk
import re
from more_itertools import pairwise

NS = rdflib.Namespace("http://example.org/")

def convert(tree_str: str, mapping: Dict[str, str], brackets: str = "[]") -> str:
  """
  Convert a parse tree in OWL.

  Args:
      tree_str (str): Parse tree.
      mapping (Dict[str, str]): Mapping between parse tree variables and concepts.

  Returns:
      str: Parse tree in Turtle syntax.
  """
  graph = rdflib.Graph()
  tree = nltk.tree.Tree.fromstring(tree_str, brackets=brackets)
  tree.chomsky_normal_form()
  
  next_property = NS["next"]
  graph.add((next_property, RDF.type, OWL.FunctionalProperty))
  
  created_concepts = list()
  
  # VariableOne
  variable_one = NS["VariableOne"]
  graph.add((variable_one, RDF.type, OWL.Class))
  variable_one_rolified = NS["R_VariableOne"]
  restriction = Restriction(variable_one_rolified, someValuesFrom=OWL.Thing, graph=graph)
  graph.add((variable_one, OWL.equivalentClass, restriction.identifier))
  # VariableTwo
  variable_two = NS["VariableTwo"]
  graph.add((variable_two, RDF.type, OWL.Class))
  variable_two_rolified = NS["R_VariableTwo"]
  restriction = Restriction(variable_two_rolified, someValuesFrom=OWL.Thing, graph=graph)
  graph.add((variable_two, OWL.equivalentClass, restriction.identifier))
  
  # extract the productions from the tree
  productions = tree.productions()
  print(productions)

  for production in productions:
    lhs = production.lhs()
    rhs = production.rhs()
  
    # handle lhs
    if lhs.symbol() in mapping:
      lhs_class = mapping[lhs.symbol()]
    else:
      lhs_class = f"C_{lhs.symbol()}"
    lhs_rolified = f"R_{lhs_class}"
  
    # rolify lhs_class
    graph.add((NS[lhs_class], RDF.type, OWL.Class))
    graph.add((NS[lhs_rolified], RDF.type, OWL.ObjectProperty))
    created_concepts.append(lhs_class)
    
    # infixOwl doesn't support hasSelf -> instantiate by hand  
    bnode = rdflib.BNode()
    graph.add((bnode, RDF.type, OWL.Restriction))
    graph.add((bnode, OWL.onProperty, NS[lhs_rolified]))
    graph.add((bnode, OWL.hasSelf, rdflib.Literal(True)))
    graph.add((NS[lhs_class], OWL.equivalentClass, bnode))
    
    # handle rhs
    if len(rhs) == 1:
      terminal = rhs[0]
      graph.add((NS[terminal], RDF.type, NS[lhs_class]))
    elif len(rhs) == 2: 
      rhs_class = map(lambda v: mapping[v.symbol()] if v.symbol() in mapping else f"C_{v.symbol()}", rhs)
      rhs_1, rhs_2 = tuple(rhs_class)
      rhs_1_rolified, rhs_2_rolified = f"R_{rhs_1}", f"R_{rhs_2}"
  
      # create the property chain to enforce order between two elements
      chain_IRI = rdflib.BNode()
      chain = rdflib.collection.Collection(graph, chain_IRI, [
        NS[rhs_1_rolified],
        next_property, 
        NS[rhs_2_rolified],
      ])
      graph.add((variable_one_rolified, OWL.propertyChainAxiom, chain_IRI))

      inverse_next = rdflib.BNode()
      graph.add((inverse_next, OWL.inverseOf, next_property))
      inverse_chain_IRI = rdflib.BNode()
      inverse_chain = rdflib.collection.Collection(graph, inverse_chain_IRI, [
        NS[rhs_2_rolified],
        inverse_next, 
        NS[rhs_1_rolified],
      ])
      graph.add((variable_two_rolified, OWL.propertyChainAxiom, inverse_chain_IRI))
  
      # general axiom
      axiom_v1 = Class(NS[rhs_1], graph=graph) & Class(variable_one, graph=graph)
      axiom_v2 = Class(NS[rhs_2], graph=graph) & Class(variable_two, graph=graph)
      collection_IRI = rdflib.BNode()
      collection = rdflib.collection.Collection(graph, collection_IRI, [axiom_v1.identifier, axiom_v2.identifier])
      union_IRI = rdflib.BNode()
      graph.add((union_IRI, OWL.unionOf, collection_IRI))
      graph.add((union_IRI, RDFS.subClassOf, NS[lhs_class]))

  for a, b in pairwise(tree.leaves()):
    graph.add((NS[a], next_property, NS[b]))

  return graph.serialize(format="turtle")