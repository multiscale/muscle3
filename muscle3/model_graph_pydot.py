from typing import List, Union

from ymmsl.configuration import PartialConfiguration
from ymmsl.identity import Reference
from ymmsl.component import Operator, Component

import pydot

# https://www.graphviz.org/docs/attr-types/arrowType/
OPERATOR_SHAPES = {
    Operator.NONE: 'normal',
    Operator.F_INIT: 'odiamond',
    Operator.O_I: 'dot',
    Operator.S: 'odot',
    Operator.O_F: 'diamond'
}


def endpoint_to_key(endpoint: Reference):
    """Replace an endpoint name like component.port with
    a graphviz node:port display.

    See https://graphviz.readthedocs.io/en/stable/manual.html#node-ports-compass

    Not sure how to handle vector ports yet.
    """
    return str(endpoint).replace('.', ':')


def port_shape(port: Reference, component: Union[Component, None]):
    """Given a port reference, find the component referred to
    and look up the shape corresponding to the port type."""
    print(component.ports.operator(port))
    return OPERATOR_SHAPES[component.ports.operator(port)] if component else 'normal'


def find_component(name: Reference, components: List[Component]):
    """Find a component by reference"""
    return next((component for component in components if component.name == str(name)), None)


def plot_model_graph(config: PartialConfiguration) -> None:
    """Convert a PartialConfiguration into DOT format.

    """
    graph = pydot.Dot(config.model.name, graph_type='digraph')

    for component in config.model.components:
        graph.add_node(pydot.Node(str(component.name), shape='box'))

    for conduit in config.model.conduits:
        # The ':' acts as a port, on a node, so we ensure that edges
        # coming from the same name get mapped to the same port

        receiver = next((component for component in config.model.components
                        if component.name == str(conduit.receiving_component)), None)
        receiving_operator = OPERATOR_SHAPES[receiver.ports.operator(conduit.receiving_port)] if receiver else 'normal'

        graph.add_edge(pydot.Edge(endpoint_to_key(conduit.sender),
                                  endpoint_to_key(conduit.receiver),
                                  arrowtail=port_shape(conduit.sending_port(),
                                                       find_component(conduit.sending_component(),
                                                                      config.model.components)),
                                  arrowhead=port_shape(conduit.receiving_port(),
                                                       find_component(conduit.receiving_component(),
                                                                      config.model.components)),
                                  dir='both',
                      ))

    print(graph)
    return graph
