from typing import List, Union

from ymmsl.configuration import PartialConfiguration
from ymmsl.identity import Reference
from ymmsl.component import Operator, Component

import pydot

COLORS = {
    Operator.F_INIT: "#2998ba",
    Operator.O_I: "#eddea1",
    Operator.S: "#f1c40f",
    Operator.O_F: "#e67e22",
}


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
        Operator.F_INIT: "normal",
        Operator.O_I: "none",
        Operator.S: "normal",
        Operator.O_F: "none",
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
    return "".join([s[0] for s in identifier.split("_")]).upper()


def legend_html_label():
    return f"""<<TABLE CELLSPACING="0" CELLBORDER="0" >
  <TR>
    <TD BGCOLOR='{COLORS[Operator.F_INIT]}'>F_INIT</TD>
    <TD BGCOLOR='{COLORS[Operator.S]}'>S</TD>
  </TR>
  <TR>
    <TD COLSPAN="2"><B>legend</B></TD>
  </TR>
  <TR>
    <TD BGCOLOR='{COLORS[Operator.O_F]}'>O_F</TD>
    <TD BGCOLOR='{COLORS[Operator.O_I]}'>O_I</TD>
  </TR>
</TABLE>>"""
    pass


def component_html_label(component: Component):
    """Construct a HTML-like label (https://graphviz.org/doc/info/shapes.html#html)"""
    # TODO: make a helper function or clean this up

    # To layout the (single) table allowed, while getting evenly divided input and
    # output ports, we can use colspan

    # remap variables here to enable experimenting with layout
    # very ugly, should refactor
    top_left = component.ports.f_init
    top_left_color = COLORS[Operator.F_INIT]
    top_right = component.ports.s
    top_right_color = COLORS[Operator.S]
    bottom_left = component.ports.o_f
    bottom_left_color = COLORS[Operator.O_F]
    bottom_right = component.ports.o_i
    bottom_right_color = COLORS[Operator.O_I]
    c_top = len(bottom_left) + len(bottom_right)
    c_bottom = len(top_left) + len(top_right)

    label = "<<TABLE CELLSPACING='0' CELLBORDER='0' >\n"

    top_ports = ""
    for port in top_left:
        top_ports += f"    <TD PORT='{port}' COLSPAN='{c_top}' BGCOLOR='{top_left_color}'>{port_shortname(port)}</TD>\n"
    # spacer port
    # top_ports += f"    <TD COLSPAN='{c_top}'></TD>\n"
    for port in top_right:
        top_ports += f"    <TD PORT='{port}' COLSPAN='{c_top}' BGCOLOR='{top_right_color}'>{port_shortname(port)}</TD>\n"

    if top_ports != "":
        label += f"  <TR>\n{top_ports}  </TR>\n"

    label += f"  <TR>\n    <TD COLSPAN='{c_top*c_bottom}'><B>{component.name}</B></TD>\n  </TR>\n"

    bottom_ports = ""
    for port in bottom_left:
        bottom_ports += f"    <TD PORT='{port}' COLSPAN='{c_bottom}' BGCOLOR='{bottom_left_color}'>{port_shortname(port)}</TD>\n"
    # spacer port
    # bottom_ports += f"    <TD COLSPAN='{c_bottom}'></TD>\n"
    for port in bottom_right:
        bottom_ports += f"    <TD PORT='{port}' COLSPAN='{c_bottom}' BGCOLOR='{bottom_right_color}'>{port_shortname(port)}</TD>\n"

    if bottom_ports != "":
        label += f"  <TR>\n{bottom_ports}  </TR>\n"

    return label.replace("'", '"') + "</TABLE>>"


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

    # Start with a legend node
    graph.add_node(pydot.Node("legend", label=legend_html_label()))

    for component in config.model.components:
        graph.add_node(
            pydot.Node(str(component.name), label=component_html_label(component))
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
                    sender,
                )
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
