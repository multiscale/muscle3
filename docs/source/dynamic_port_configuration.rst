Dynamic port configuration
==========================

In the tutorial we have seen that, when creating an ``Instance``, you need to indicate
the ports that the instance has. For, example, the `reaction` component defined two
ports:

.. tabs::

    .. group-tab:: Python

        .. code-block:: python

            instance = Instance({
                Operator.F_INIT: ['initial_state'],     # 1D Grid
                Operator.O_F: ['final_state']})         # 1D Grid

    .. group-tab:: C++

        .. code-block:: C++

            Instance instance(argc, argv, {
                {Operator::F_INIT, {"initial_state"}},  // 1D Grid
                {Operator::O_F, {"final_state"}}});     // 1D Grid


Some components in your simulation can be generic, for example merging multiple inputs
into a single container. For these generic component, MUSCLE3 allows the component to
have a `dynamic` ports configuration: the ports will be created based on the yMMSL
configuration instead of statically configured when creating the Instance.

.. versionchanged:: 0.10.0 Added support for dynamic ``O_I`` and ``S`` ports.


Example: generic combiner component
-----------------------------------

The generic combiner component from this example receives inputs on multiple ``F_INIT``
ports, combines them into a list and finally sends it on its output port(s). In the code
listings below, you see how the component:

1. Indicates it wants a dynamic port configuration, by not providing a port description
   when creating the Instance.
2. Requests which ports are available, and checks that it only has ``F_INIT`` and
   ``O_F`` ports.
3. Receives on all connected ``F_INIT`` ports.
4. Combines the message data from all inputs and sends it on all connected ``O_F``
   ports.


.. tabs::

    .. group-tab:: Python

        .. literalinclude:: examples/python/combiner.py
            :caption: ``docs/source/examples/python/combiner.py``
            :language: python

    .. group-tab:: C++

        .. literalinclude:: examples/cpp/combiner.cpp
            :caption: ``docs/source/examples/cpp/combiner.cpp``
            :language: c++
