from typing import List, Union

from ymmsl.configuration import PartialConfiguration
from ymmsl.identity import Reference
from ymmsl.component import Operator, Component

import pydot

# https://www.graphviz.org/docs/attr-types/arrowType/
OPERATOR_SHAPES = {
    Operator.NONE: "normal",
    Operator.F_INIT: "odiamond",
    Operator.O_I: "dot",
    Operator.S: "odot",
    Operator.O_F: "diamond",
}


def endpoint_to_key(endpoint: Reference):
    """Replace an endpoint name like component.port with
    a graphviz node:port display.

    See https://graphviz.readthedocs.io/en/stable/manual.html#node-ports-compass

    Not sure how to handle vector ports yet.
    """
    return str(endpoint).replace(".", ":")


def port_shape(port: Reference, component: Union[Component, None]):
    """Given a port reference, find the component referred to
    and look up the shape corresponding to the port type."""
    return OPERATOR_SHAPES[component.ports.operator(port)] if component else "normal"


def find_component(name: Reference, components: List[Component]):
    """Find a component by reference"""
    return next(
        (component for component in components if component.name == str(name)), None
    )


def plot_model_graph(config: PartialConfiguration) -> None:
    """Convert a PartialConfiguration into DOT format."""
    graph = pydot.Dot(
        config.model.name,
        graph_type="digraph",
        layout="sfdp",
        pad=1,
        splines="ortho",
        nodesep=0.6,
        ranksep=0.75,
        fontname="Sans-Serif",
    )

    for component in config.model.components:
        graph.add_node(
            pydot.Node(
                str(component.name),
                shape="box",
                style="rounded",
                fixedsize="false",
                width=2,
                height=1,
                labelloc="c",
            )
        )

    for conduit in config.model.conduits:
        # The ':' acts as a port, on a node, so we ensure that edges
        # coming from the same name get mapped to the same port
        sender = find_component(conduit.sending_component(), config.model.components)
        receiver = find_component(
            conduit.receiving_component(), config.model.components
        )

        # Could save space in generated dot graph by setting default values
        # (see https://graphviz.org/docs/edges/ edge [name0=val0])
        edge = pydot.Edge(
            endpoint_to_key(conduit.sender),
            endpoint_to_key(conduit.receiver),
            arrowtail=port_shape(
                conduit.sending_port(),
                sender,
            ),
            arrowhead=port_shape(
                conduit.receiving_port(),
                receiver,
            ),
            dir="both",
            labelfontsize=8,
            fontsize=8,
            len=2,
        )

        # if port names match exactly (optionally when removing an _in or _out suffix)
        # we show the name on the conduit instead of on the port
        sending_port = str(conduit.sending_port())
        receiving_port = str(conduit.receiving_port())

        # special casing for ports having names matching almost exactly
        sending_port = (
            sending_port[:-4] if sending_port.endswith("_out") else sending_port
        )
        receiving_port = (
            receiving_port[:-3] if receiving_port.endswith("_in") else receiving_port
        )

        if sending_port == receiving_port:
            edge.set_label(sending_port)
        else:
            edge.set_taillabel(str(conduit.sending_port()))
            edge.set_headlabel(str(conduit.receiving_port()))

        # we could consider setting a minlen based on the text length and font size

        graph.add_edge(edge)

    print(graph)
    return graph
