from typing import List, Dict, Union
from cfgowl.grammar import Grammar
import rdflib
from rdflib.extras.infixowl import Class, Restriction, Ontology
from rdflib import OWL, RDF, RDFS
from more_itertools import pairwise
import urllib


def create_grammar_class(name: str, graph: rdflib.Graph, namespace: rdflib.Namespace, rolify: bool = True, rolified_name: Union[str, None] = None):
  """
  Create a class in the provided graph. Optionally rolify the class.

  Args:
      name (str): Class name
      graph (rdflib.Graph): Ontology Graph
      namespace (rdflib.Namespace): Namespace used to create the class
      rolify (bool, optional): Rolify the class or not. Defaults to True.
      rolified_name (Union[str, None], optional): Name of the rolified property. If None the rolification property is named R_<name>. Defaults to None.
  """
  rolified_name = f"R_{name}" if rolified_name is None else rolified_name

  graph.add((namespace[name], RDF.type, OWL.Class))
  graph.add((namespace[rolified_name], RDF.type, OWL.ObjectProperty))

  # infixOwl doesn't support hasSelf -> instantiate manually
  bnode = rdflib.BNode()
  graph.add((bnode, RDF.type, OWL.Restriction))
  graph.add((bnode, OWL.onProperty, namespace[rolified_name]))
  graph.add((bnode, OWL.hasSelf, rdflib.Literal(True)))
  graph.add((namespace[name], OWL.equivalentClass, bnode))


def grammar_to_owl(grammar: Grammar, 
                   namespace: str = "http://w3id.org/cfgowl/",
                   next_predicate_iri: str = "http://www.ontologydesignpatterns.org/cp/owl/sequence.owl#directlyFollows",
                   previous_predicate_iri: str = "http://www.ontologydesignpatterns.org/cp/owl/sequence.owl#directlyPrecedes") -> rdflib.Graph:
  """
  Converts a grammar object into an OWL ontology, using
  the algorithm described in [1].

  [1] https://link.springer.com/chapter/10.1007/978-3-031-33455-9_10

  Args:
      grammar (Grammar): Input grammar.
      namespace (str, optional): Namespace used to create the classes. 
        Defaults to "http://w3id.org/cfgowl/".
      next_predicate_iri (str, optional): IRI of the predicate that has semantic "next element in the sequence". 
        Defaults to "http://www.ontologydesignpatterns.org/cp/owl/sequence.owl#directlyFollows".
      previous_predicate_iri (str, optional): IRI of the predicate that has semantic "previous element in the sequence".
        Defaults to "http://www.ontologydesignpatterns.org/cp/owl/sequence.owl#directlyPrecedes".

  Returns:
      rdflib.Graph: OWL ontology
  """
  graph = rdflib.Graph()
  NS = rdflib.Namespace(namespace)

  cnf_grammar = grammar.cnf

  # next property must be functional
  next_property = rdflib.URIRef(next_predicate_iri)
  graph.add((next_property, RDF.type, OWL.FunctionalProperty))
  inverse_next = rdflib.URIRef(previous_predicate_iri)
  graph.add((inverse_next, OWL.inverseOf, next_property))      
  
  created_concepts = list()
  
  # create the class for variable one
  variable_one = NS["VariableOne"]
  graph.add((variable_one, RDF.type, OWL.Class))
  variable_one_rolified = NS["R_VariableOne"]
  restriction = Restriction(variable_one_rolified, someValuesFrom=OWL.Thing, graph=graph)
  graph.add((variable_one, OWL.equivalentClass, restriction.identifier))
  
  # create the class for variable two
  variable_two = NS["VariableTwo"]
  graph.add((variable_two, RDF.type, OWL.Class))
  variable_two_rolified = NS["R_VariableTwo"]
  restriction = Restriction(variable_two_rolified, someValuesFrom=OWL.Thing, graph=graph)
  graph.add((variable_two, OWL.equivalentClass, restriction.identifier))
  
  created_classes = list()
  for lhs_class, rhss in cnf_grammar:
    lhs_class = urllib.parse.quote_plus(lhs_class)
    lhs_rolified = f"R_{lhs_class}"

    if lhs_class not in created_classes:
      # rolify lhs_class
      create_grammar_class(lhs_class, graph, NS)
      created_classes.append(lhs_class)
          
    for rhs in rhss:
      rhs = tuple(map(urllib.parse.quote_plus, rhs.split(" ")))
      
      if len(rhs) == 1:
        terminal = rhs[0]
        if terminal not in created_classes:
          create_grammar_class(terminal, graph, NS)
        graph.add((NS[terminal], RDFS.subClassOf, NS[lhs_class]))
      elif len(rhs) == 2: 
        rhs_1, rhs_2 = rhs
        rhs_1_rolified, rhs_2_rolified = f"R_{rhs_1}", f"R_{rhs_2}"

        if rhs_1 not in created_classes: 
          create_grammar_class(rhs_1, graph, NS)
          created_classes.append(rhs_1)
        if rhs_2 not in created_classes: 
          create_grammar_class(rhs_2, graph, NS)
          created_classes.append(rhs_2)
  
        # create the property chain to enforce order between two elements
        chain_IRI = rdflib.BNode()
        chain = rdflib.collection.Collection(graph, chain_IRI, [
          NS[rhs_1_rolified],
          next_property, 
          NS[rhs_2_rolified],
        ])
        graph.add((variable_one_rolified, OWL.propertyChainAxiom, chain_IRI))

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

  return graph


def parsing_result_to_owl(
  paths: List,
  namespace: str = "http://w3id.org/cfgowl/",
  next_predicate_iri: str = "http://www.ontologydesignpatterns.org/cp/owl/sequence.owl#directlyFollows") -> rdflib.Graph:
  """
  Converts the parsed ancestors of a  grammar object into an OWL ontology, using the algorithm described in [1].

  [1] https://link.springer.com/chapter/10.1007/978-3-031-33455-9_10

  Args:
      grammar (Grammar): Input grammar.
      namespace (str, optional): Namespace used to create the classes. 
        Defaults to "http://w3id.org/cfgowl/".
      next_predicate_iri (str, optional): IRI of the predicate that has semantic "next element in the sequence". 
        Defaults to "http://www.ontologydesignpatterns.org/cp/owl/sequence.owl#directlyFollows".

  Returns:
      rdflib.Graph: OWL ontology
  """
  graph = rdflib.Graph()
  NS = rdflib.Namespace(namespace)
  
  # next property must be functional
  next_property = rdflib.URIRef(next_predicate_iri)
  graph.add((next_property, RDF.type, OWL.FunctionalProperty))
  
  for (a, a_classes), (b, b_classes) in pairwise(paths):
    # add the sequence in the ontology
    a = urllib.parse.quote_plus(a)
    a_type = urllib.parse.quote_plus(a_classes[-1])
    b_type = urllib.parse.quote_plus(b_classes[-1])

    graph.add((NS[a], next_property, NS[b]))
    graph.add((NS[a], RDF.type, NS[a_type]))
    graph.add((NS[b], RDF.type, NS[b_type]))
    
    for c in a_classes[:-1]:
      c = urllib.parse.quote_plus(c)
      graph.add((NS[a], RDF.type, NS[c]))
      graph.add((NS[a_type], RDFS.subClassOf, NS[c]))

    for c in b_classes:
      c = urllib.parse.quote_plus(c)
      graph.add((NS[b], RDF.type, NS[c]))
      graph.add((NS[b_type], RDFS.subClassOf, NS[c]))
  
  return graph