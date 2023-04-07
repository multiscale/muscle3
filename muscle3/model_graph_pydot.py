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


def port_shape(port: Reference, component: Union[Component, None]):
    """Given a port reference, find the component referred to,
    look up the port type matching this name
    and look up the shape corresponding to the port type."""

    # I think it is quite easy to misinterpret the direction of a MMSL diagram
    # given that the 'weight' of the edge is towards the filled shape.
    # I would consider making the sending_port smaller, but cannot find the setting
    # in graphviz
    return OPERATOR_SHAPES[component.ports.operator(port)] if component else "normal"


def find_component(name: Reference, components: List[Component]):
    """Find a component by reference"""
    return next(
        (component for component in components if component.name == str(name)), None
    )


def set_style(graph):
    """set default properties to make for a more readable DOT file"""
    graph.add_node(
        pydot.Node(
            "node",
            shape="box",
            style="rounded",
            fixedsize="false",
            width=2,
            height=1,
            labelloc="c",
        )
    )

    # set default edge properties
    graph.add_node(
        pydot.Node(
            "edge",
            dir="both",
            labelfontsize=8,
            fontsize=8,
            len=2,
        )
    )


def trim_sending_port(identifier: str):
    """Strip _out suffix from identifier"""
    return identifier[:-4] if identifier.endswith("_out") else identifier


def trim_receiving_port(identifier: str):
    """Strip _in, _init suffix from identifier"""
    if identifier.endswith("_in"):
        return identifier[:-3]
    if identifier.endswith("_init"):
        return identifier[:-5]
    return identifier


def plot_model_graph(config: PartialConfiguration, simplify_edge_labels: bool) -> None:
    """Convert a PartialConfiguration into DOT format."""
    graph = pydot.Dot(
        config.model.name,
        graph_type="digraph",
        layout="dot",
        pad=1,
        # splines="ortho",
        nodesep=0.6,
        ranksep=0.75,
        fontname="Sans-Serif",
    )
    # be very careful with ortho splines, I have seen it put edges
    # upside down and eating labels
    set_style(graph)

    for component in config.model.components:
        graph.add_node(
            pydot.Node(
                str(component.name),
            )
        )

    for conduit in config.model.conduits:
        # can we do this more elegantly?
        sender = find_component(conduit.sending_component(), config.model.components)
        receiver = find_component(
            conduit.receiving_component(), config.model.components
        )

        edge = pydot.Edge(
            str(conduit.sending_component()),
            str(conduit.receiving_component()),
            arrowtail=port_shape(
                conduit.sending_port(),
                sender,
            ),
            tailport=str(conduit.sending_port()),
            arrowhead=port_shape(
                conduit.receiving_port(),
                receiver,
            ),
            headport=str(conduit.receiving_port()),
        )

        # if port names match exactly (optionally when removing an _in or _out suffix)
        # we show the name on the conduit instead of on the port
        if simplify_edge_labels and trim_sending_port(
            str(conduit.sending_port())
        ) == trim_receiving_port(str(conduit.receiving_port())):
            edge.set_label(trim_sending_port(str(conduit.sending_port())))
        else:
            edge.set_taillabel(str(conduit.sending_port()))
            edge.set_headlabel(str(conduit.receiving_port()))

        # we could consider setting a minlen based on the text length and font size
        graph.add_edge(edge)

    return graph
