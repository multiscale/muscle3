from typing import List, Union

from ymmsl.configuration import PartialConfiguration
from ymmsl.identity import Reference
from ymmsl.component import Operator, Component

import pydot


def port_operator(port: Reference, component: Union[Component, None]):
    """Look up the operator corresponding to a specific port"""
    return component.ports.operator(port) if component else "normal"

def port_shape(operator: str):
    """Given a port reference, find the component referred to,
    look up the port type matching this name
    and look up the shape corresponding to the port type."""

    # I think it is quite easy to misinterpret the direction of a MMSL diagram
    # given that the 'weight' of the edge is towards the filled shape.
    # I would consider making the sending_port smaller, but cannot find the setting
    # in graphviz
    # https://www.graphviz.org/docs/attr-types/arrowType/
    OPERATOR_SHAPES = {
        Operator.NONE: "normal",
        Operator.F_INIT: "odiamond",
        Operator.O_I: "dot",
        Operator.S: "odot",
        Operator.O_F: "diamond",
    }
    return OPERATOR_SHAPES[operator]


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
            shape="plain",
            style="rounded",
            fixedsize="false",
            width=2,
            penwidth=2,
            height=1,
            labelloc="c",
        )
    )

    # set default edge properties
    graph.add_node(
        pydot.Node(
            "edge",
            dir="both",
            labelfontsize=10,
            fontsize=10,
            penwidth=2,
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

def headport(identifier: Reference, component: Union[Component, None]):
    """Given a reference, return the portPos.
    https://www.graphviz.org/docs/attr-types/portPos/
    """
    return str(identifier)

def tailport(identifier: Reference, component: Union[Component, None]):
    """Given a reference, return the portPos.
    https://www.graphviz.org/docs/attr-types/portPos/
    """
    return str(identifier)

def port_shortname(identifier: Reference):
    """Strip suffixes and summarize names to only a few characters"""
    identifier = trim_sending_port(trim_receiving_port(str(identifier)))
    return "".join([s[0] for s in identifier.split('_')]).upper()

def component_html_label(component: Component):
    """Construct a HTML-like label (https://graphviz.org/doc/info/shapes.html#html)"""

    # To layout the (single) table allowed, while getting evenly divided input and
    # output ports, we can use colspan

    n_inputs = len(component.ports.f_init) + len(component.ports.s)
    if n_inputs == 0:
        n_inputs = 1
    n_outputs = len(component.ports.o_f) + len(component.ports.o_i)
    if n_outputs == 0:
        n_outputs = 1

    label = "<<TABLE CELLSPACING='0'>\n"

    # First draw a row with the input ports if there are any
    input_ports = ""
    for port in component.ports.f_init:
        input_ports += f"    <TD PORT='{port}' COLSPAN='{n_outputs}'>{port_shortname(port)}</TD>\n"
    for port in component.ports.s:
        input_ports += f"    <TD PORT='{port}' COLSPAN='{n_outputs}'>{port_shortname(port)}</TD>\n"
    
    if input_ports != "":
        label += f"  <TR>\n{input_ports}  </TR>\n"

    label += f"  <TR>\n    <TD COLSPAN='{n_outputs*n_inputs}'><B>{component.name}</B></TD>\n  </TR>\n"

    # Finally draw the output ports
    output_ports = ""
    for port in component.ports.o_f:
        output_ports += f"    <TD PORT='{port}' COLSPAN='{n_inputs}'>{port_shortname(port)}</TD>\n"
    for port in component.ports.o_i:
        output_ports += f"    <TD PORT='{port}' COLSPAN='{n_inputs}'>{port_shortname(port)}</TD>\n"

    if output_ports != "":
        label += f"  <TR>\n{output_ports}  </TR>\n"

    return label.replace("'", '"') + '</TABLE>>'

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
                label=component_html_label(component)
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
                port_operator(
                conduit.sending_port(),
                sender,)
            ),
            tailport=tailport(conduit.sending_port(), sender),
            arrowhead=port_shape(
                port_operator(
                conduit.receiving_port(),
                receiver,
                )
            ),
            headport=headport(conduit.receiving_port(), receiver),
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
