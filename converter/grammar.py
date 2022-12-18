from typing import Dict, Union
import rdflib
from rdflib.extras.infixowl import Class, Restriction, Ontology
from rdflib import OWL, RDF, RDFS
import nltk
import re
from more_itertools import pairwise
import urllib

NS = rdflib.Namespace("http://example.org/")

def create_class(name: str, graph: rdflib.Graph, rolify: bool = True, rolified_name: Union[str, None] = None):
  """
  Create a class in the provided graph. Optionally rolify the class.

  Args:
      name (str): Class name
      graph (rdflib.Graph): Ontology Graph
      rolify (bool, optional): Rolify the class or not. Defaults to True.
      rolified_name (Union[str, NoneType], optional): Name of the rolified property. If None the rolification property is named R_<name>. Defaults to None.
  """
  rolified_name = f"R_{name}" if rolified_name is None else rolified_name

  graph.add((NS[name], RDF.type, OWL.Class))
  graph.add((NS[rolified_name], RDF.type, OWL.ObjectProperty))

  # infixOwl doesn't support hasSelf -> instantiate by hand  
  bnode = rdflib.BNode()
  graph.add((bnode, RDF.type, OWL.Restriction))
  graph.add((bnode, OWL.onProperty, NS[rolified_name]))
  graph.add((bnode, OWL.hasSelf, rdflib.Literal(True)))
  graph.add((NS[name], OWL.equivalentClass, bnode))


def convert(grammar_mapping: Dict[str, str]) -> str:
  """
  Convert a parse tree in OWL.

  Args:
      tree_str (str): Parse tree.
      mapping (Dict[str, str]): Mapping between parse tree variables and concepts.

  Returns:
      str: Parse tree in Turtle syntax.
  """
  graph = rdflib.Graph()
  
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
  
  created_classes = list()
  for lhs_class, rhss in grammar_mapping.items():
    lhs_class = urllib.parse.quote(lhs_class)
    lhs_rolified = f"R_{lhs_class}"

    if lhs_class not in created_classes:
      # rolify lhs_class
      create_class(lhs_class, graph)
      created_classes.append(lhs_class)
          
    for rhs in rhss:
      # handle rhs
      rhs = tuple(map(urllib.parse.quote, rhs.split(" ")))
      if len(rhs) == 1:
        terminal = rhs[0]
        if terminal not in created_classes:
          create_class(terminal, graph)
        graph.add((NS[terminal], RDFS.subClassOf, NS[lhs_class]))
      elif len(rhs) == 2: 
        rhs_1, rhs_2 = rhs
        rhs_1_rolified, rhs_2_rolified = f"R_{rhs_1}", f"R_{rhs_2}"

        if rhs_1 not in created_classes: 
          create_class(rhs_1, graph)
          created_classes.append(rhs_1)
        if rhs_2 not in created_classes: 
          create_class(rhs_2, graph)
          created_classes.append(rhs_2)
  
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

  return graph.serialize(format="turtle")