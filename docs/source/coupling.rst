Coupling your model
===================

Multicast
---------

With MUSCLE3 you can connect an output port to multiple input ports.
When a submodel sends a message on a port that is connected to
multiple input ports, the message is copied and sent to each connected port.

.. note::

    It is not allowed to connect multiple output ports to a single input port.

Example
```````

.. tabs::

    .. code-tab:: yaml Basic macro/micro model configuration

        ymmsl_version: v0.1
        model:
          name: multicast
          components:
            macro: macro
            micro: micro
          conduits:
            macro.state_out: micro.state_in
            micro.state_out: macro.state_in

    .. code-tab:: yaml Extended configuration with multicast

        ymmsl_version: v0.1
        model:
          name: multicast
          components:
            macro: macro
            micro: micro
            printer: printer
          conduits:
            macro.state_out: micro.state_in
            micro.state_out:
            - macro.state_in
            - printer.in

In the second tab, a new component `printer` is added and wired to the
``state_out`` port of the micro model. Whenever the micro model sends a message
on that port, one copy is sent to the macro model to continue the simulation.
Another copy is sent to the printer component, which (for example) prints a
summary of the state.

