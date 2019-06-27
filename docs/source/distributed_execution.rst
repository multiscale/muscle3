Distributed execution
=====================

In the previous section, we created a simple macro-micro multiscale model with
MUSCLE 3, and ran it as a single Python script. This section briefly explains
how to go from there to a distributed simulation, possibly on multiple machines.

Note that distributed simulations are still somewhat experimental. They need a
bit more testing, and more development (in particular integration with a
launcher) to make them easier to use. All the necessary pieces are in place
however.

Making separate instances
-------------------------

Previously, we started a simulation by starting a single Python script that
contained all of the implementations and also the model configuration. For
distributed running, we want to start the instances one by one, so our script
needs to be split up. Doing that is very simple: just copy the model function
(and anything it depends on) to a new file, and add a main clause that runs it.
For the reaction model of the previous example, that looks like this:

.. literalinclude:: examples/reaction.py
  :caption: ``docs/source/examples/reaction.py``
  :language: python


Note that the code is exactly the same, we've just removed everything related to
the diffusion model and to the coupling between them. We can do the same to the
diffusion model:

.. literalinclude:: examples/diffusion.py
  :caption: ``docs/source/examples/diffusion.py``
  :language: python


Again, it's exactly the same code as before, just split off into a separate
file.

yMMSL files
-----------

In a distributed set-up, the manager and each instance run as separate programs,
communicating via the network. To make this work, the manager is started first,
with a yMMSL file that describes the simulation. The yMMSL file corresponding to
our previous example looks like this:

.. literalinclude:: examples/reaction_diffusion.ymmsl
  :caption: ``docs/source/examples/reaction_diffusion.ymmsl``
  :language: yaml


As you can see, this looks very much like the object representation. You can
load a yMMSL file to objects using `ymmsl.load` and save it back using
`ymmsl.save`.

Starting the manager
--------------------

Every MUSCLE 3 simulation needs a manager. The manager helps the instances find
each other, and distributes settings to them. To start the manager, run

.. code-block:: bash

  (venv)$ muscle_manager reaction_diffusion.ymmsl


in an environment in which you've installed MUSCLE 3. The manager will start,
and will print its location on standard out. This is the network address on
which it listens for connections from instances.

Starting instances
------------------

Starting an instance works just like starting any other Python script:

.. code-block:: bash

  (venv)$ python ./reaction.py --muscle-instance=micro


In the original script, we made a dictionary that mapped compute element names
to Python functions, which MUSCLE 3 used to start the submodel instances. Here,
we need to pass the same information. Instead of a function name, we start a
particular script, and we pass the instance name using the `--muscle-instance=`
argument. Note that the argument parser is not very flexible, so it needs to be
written exactly like that, and of course the instance name needs to match the
compute element name in the yMMSL file passed to the manager.

When the instance starts, it will register with the manager. Since we didn't
pass a location using the `--muscle-manager=<host:port>` option, MUSCLE 3 tried
to connect to the default location (localhost:9000), which the manager was
conveniently listening on. The `micro` instance registered, and if you have a
look at the `muscle3_manager.log` file produced by the manager (in the directory
in which you started it), you should find a record of this there.

Now, we need to start the second submodel in the same way:

.. code-block:: bash

  (venv)$ python ./diffusion.py --muscle-instance=macro


and then the simulation will run. Once it's done, the instances disconnect and
the manager shuts itself down automatically.
