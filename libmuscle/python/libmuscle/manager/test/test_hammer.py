from ymmsl import load
from ymmsl.v0_2 import Conduit, Model, Reference, resolve

from libmuscle.manager.hammer import flatten, Plate

import pytest


@pytest.fixture
def c1() -> Conduit:
    return Conduit('macro.out', 'micro.in')


@pytest.fixture
def c2() -> Conduit:
    return Conduit('micro.in', 'micro.program.in')


@pytest.fixture
def c3() -> Conduit:
    return Conduit('micro.program.out', 'micro.out')


@pytest.fixture
def c4() -> Conduit:
    return Conduit('micro.out', 'macro.in')


@pytest.fixture
def c5() -> Conduit:
    return Conduit('micro.in', 'micro.program2.in')


@pytest.fixture
def plate(c1: Conduit, c2: Conduit, c3: Conduit, c4: Conduit, c5: Conduit) -> Plate:
    plate = Plate()
    plate.add(c1, True, False)
    plate.add(c2, False, True)
    plate.add(c3, True, False)
    plate.add(c4, False, True)
    plate.add(c5, False, True)
    return plate


def has_conduit(model: Model, sender: str, receiver: str, filters: str = '') -> bool:
    """Helper function for checking whether a model has a given conduit.

    They're in a list, this makes it easier to search, although still inefficient.
    Filters are given in a single string, separated by single spaces, e.g. 'last pad'.
    """
    for conduit in model.conduits:
        if conduit.sender == sender and conduit.receiver == receiver:
            cfs = ' '.join([f.value for f in conduit.filters])
            if cfs == filters:
                return True
    return False


def test_plate(plate, c2, c5) -> None:
    macro_out_conduits = plate.pop_by_sender(Reference('micro.in'))
    assert macro_out_conduits == {
            Reference('micro.program.in'): (c2, True),
            Reference('micro.program2.in'): (c5, True)}

    # check that they were removed
    assert len(plate.pop_by_sender(Reference('micro.in'))) == 0


def test_plate2(plate, c1) -> None:
    micro2_in_conduits = plate.pop_by_receiver(Reference('micro.in'))
    assert micro2_in_conduits == {Reference('macro.out'): (c1, True)}

    # check that it was removed
    assert len(plate.pop_by_receiver(Reference('micro.in'))) == 0


def test_flatten_simple() -> None:
    nested_config_yaml = (
            'ymmsl_version: v0.2\n'
            'description: Simple nested test configuration\n'
            'models:\n'
            '  outer:\n'
            '    description: Model containing a submodel\n'
            '    components:\n'
            '      init:\n'
            '        ports:\n'
            '          o_f: init_out\n'
            '        description: Creates initial conditions\n'
            '        implementation: p1\n'
            '      sim:\n'
            '        ports:\n'
            '          f_init: init_in\n'
            '        description: Simulates stuff\n'
            '        implementation: inner\n'
            '    conduits:\n'
            '      init.init_out: sim.init_in\n'
            '  inner:\n'
            '    ports:\n'
            '      f_init: init_in\n'
            '    description: Nested simulation model\n'
            '    components:\n'
            '      simulate:\n'
            '        ports:\n'
            '          f_init: in\n'
            '        description: Simulation program\n'
            '        implementation: p2\n'
            '    conduits:\n'
            '      init_in: simulate.in\n'
            'programs:\n'
            '  p1:\n'
            '    description: Program that calculates initial conditions\n'
            '    executable: /home/user/codes/p1\n'
            '  p2:\n'
            '    description: Program that simulates stuff\n'
            '    executable: /home/user/codes/p2\n'
            )

    nested_config = load(nested_config_yaml)
    flat_config = flatten(nested_config)

    assert len(flat_config.models) == 1
    assert 'outer' in flat_config.models
    model = flat_config.root_model()
    assert model.name == 'outer'
    assert len(model.components) == 2
    assert 'init' in model.components
    assert 'sim.simulate' in model.components
    assert len(model.conduits) == 1
    assert has_conduit(model, 'init.init_out', 'sim.simulate.in')


def test_flatten_deep() -> None:
    nested_config_yaml = (
            'ymmsl_version: v0.2\n'
            'description: Three-deep nested test configuration\n'
            'models:\n'
            '  top:\n'
            '    description: Model at the top\n'
            '    components:\n'
            '      c1:\n'
            '        ports:\n'
            '          o_i: out\n'
            '          s: in\n'
            '        description: Calls c2\n'
            '        implementation: p1\n'
            '      c2:\n'
            '        ports:\n'
            '          f_init: init_in\n'
            '          o_f: final_out\n'
            '        description: Submodel\n'
            '        implementation: middle\n'
            '    conduits:\n'
            '      c1.out: c2.init_in\n'
            '      c2.final_out: c1.in\n'
            '  middle:\n'
            '    ports:\n'
            '      f_init: init_in\n'
            '      o_f: final_out\n'
            '    description: Middle simulation model, empty shell really\n'
            '    components:\n'
            '      c3:\n'
            '        ports:\n'
            '          f_init: init_in\n'
            '          o_f: final_out\n'
            '        description: Forward again...\n'
            '        implementation: bottom\n'
            '    conduits:\n'
            '      init_in: c3.init_in\n'
            '      c3.final_out: final_out\n'
            '  bottom:\n'
            '    ports:\n'
            '      f_init: init_in\n'
            '      o_f: final_out\n'
            '    description: Bottom simulation model\n'
            '    components:\n'
            '      c4:\n'
            '        ports:\n'
            '          f_init: init_in\n'
            '          o_f: final_out\n'
            '        description: Actual simulation model\n'
            '        implementation: p2\n'
            '    conduits:\n'
            '      init_in: c4.init_in\n'
            '      c4.final_out: final_out\n'
            'programs:\n'
            '  p1:\n'
            '    description: Program that calculates initial conditions\n'
            '    executable: /home/user/codes/p1\n'
            '  p2:\n'
            '    description: Program that simulates stuff\n'
            '    executable: /home/user/codes/p2\n'
            )

    nested_config = load(nested_config_yaml)
    flat_config = flatten(nested_config)

    assert len(flat_config.models) == 1
    assert 'top' in flat_config.models
    model = flat_config.root_model()
    assert model.name == 'top'
    assert len(model.components) == 2
    assert 'c1' in model.components
    assert 'c2.c3.c4' in model.components
    assert len(model.conduits) == 2
    assert has_conduit(model, 'c1.out', 'c2.c3.c4.init_in')
    assert has_conduit(model, 'c2.c3.c4.final_out', 'c1.in')


def test_flatten_nested_ensemble() -> None:
    nested_config_yaml = (
            'ymmsl_version: v0.2\n'
            'description: Three-deep nested test configuration\n'
            'models:\n'
            '  top:\n'
            '    description: Model at the top\n'
            '    components:\n'
            '      c1:\n'
            '        ports:\n'
            '          o_i: out\n'
            '          s: in\n'
            '        description: Calls c2\n'
            '        implementation: p1\n'
            '      c2:\n'
            '        ports:\n'
            '          f_init: init_in\n'
            '          o_f: final_out\n'
            '        description: Submodel\n'
            '        implementation: middle\n'
            '        multiplicity: 10\n'
            '    conduits:\n'
            '      c1.out: c2.init_in\n'
            '      c2.final_out: c1.in\n'
            '  middle:\n'
            '    ports:\n'
            '      f_init: init_in\n'
            '      o_f: final_out\n'
            '    description: This should get replicated\n'
            '    components:\n'
            '      c3:\n'
            '        ports:\n'
            '          f_init: init_in\n'
            '          o_f: final_out\n'
            '        description: Another subcomponent\n'
            '        implementation: nested\n'
            '        multiplicity: 5\n'
            '    conduits:\n'
            '      init_in: c3.init_in\n'
            '      c3.final_out: final_out\n'
            '  nested:\n'
            '    ports:\n'
            '      f_init: init_in\n'
            '      o_f: final_out\n'
            '    description: This should get replicated, nested\n'
            '    components:\n'
            '      c4:\n'
            '        ports:\n'
            '          f_init: init_in\n'
            '          o_f: final_out\n'
            '        description: First component\n'
            '        implementation: p2\n'
            '      c5:\n'
            '        ports:\n'
            '          f_init: init_in\n'
            '          o_f: final_out\n'
            '        description: Second component\n'
            '        implementation: p2\n'
            '    conduits:\n'
            '      init_in: c4.init_in\n'
            '      c4.final_out: c5.init_in\n'
            '      c5.final_out: final_out\n'
            'programs:\n'
            '  p1:\n'
            '    description: Program that calculates initial conditions\n'
            '    executable: /home/user/codes/p1\n'
            '  p2:\n'
            '    description: Program that simulates stuff\n'
            '    executable: /home/user/codes/p2\n'
            )

    nested_config = load(nested_config_yaml)
    flat_config = flatten(nested_config)

    assert len(flat_config.models) == 1
    assert 'top' in flat_config.models
    model = flat_config.root_model()
    assert model.name == 'top'
    assert len(model.components) == 3
    assert 'c1' in model.components
    assert 'c2.c3.c4' in model.components
    assert model.components['c2.c3.c4'].multiplicity == [10, 5]
    assert 'c2.c3.c5' in model.components
    assert model.components['c2.c3.c5'].multiplicity == [10, 5]
    assert len(model.conduits) == 3
    assert has_conduit(model, 'c2.c3.c4.final_out', 'c2.c3.c5.init_in')
    assert has_conduit(model, 'c1.out', 'c2.c3.c4.init_in')
    assert has_conduit(model, 'c2.c3.c5.final_out', 'c1.in')


def test_flatten_conduit_filters() -> None:
    nested_config_yaml = (
            'ymmsl_version: v0.2\n'
            'description: Macro-micro to macro-micro dispatch, nested\n'
            'models:\n'
            '  macro_micro:\n'
            '    ports:\n'
            '      f_init: macro_state_in micro_state_in\n'
            '      o_f: macro_state_out micro_state_out\n'
            '    description: Macro-micro model\n'
            '    components:\n'
            '      macro:\n'
            '        ports:\n'
            '          f_init: state_in\n'
            '          o_i: boundary_out\n'
            '          s: boundary_in\n'
            '          o_f: state_out\n'
            '        description: |\n'
            '          Macro model that communicates its boundary conditions\n'
            '          while running, and outputs its state at the end.\n'
            '        implementation: p1\n'
            '      micro:\n'
            '        ports:\n'
            '          f_init: state_in boundary_in\n'
            '          o_f: state_out boundary_out\n'
            '        description: |\n'
            '          Stateful micro model that takes new boundary conditions and\n'
            '          optionally a new state on each run. If a new state is received\n'
            '          then it re-initialises, otherwise the current state is kept.\n'
            '          Re-equilibrates to the new boundary conditions, then outputs\n'
            '          boundary and state at the end of each run.\n'
            '        implementation: p2\n'
            '    conduits:\n'
            '      macro_state_in: macro.state_in\n'
            '      micro_state_in: pad micro.state_in\n'
            '      macro.boundary_out: micro.boundary_in\n'
            '      micro.boundary_out: macro.boundary_in\n'
            '      macro.state_out: macro_state_out\n'
            '      micro.state_out: last micro_state_out\n'
            '  init:\n'
            '    ports:\n'
            '      o_f: macro_state_out micro_state_out\n'
            '    description: Creates initial states\n'
            '    components:\n'
            '      init_macro:\n'
            '        ports:\n'
            '          o_f: state_out\n'
            '        description: Creates initial conditions for macro\n'
            '        implementation: p3\n'
            '      init_micro:\n'
            '        ports:\n'
            '          o_f: state_out\n'
            '        description: Creates initial conditions for micro\n'
            '        implementation: p4\n'
            '    conduits:\n'
            '      init_macro.state_out: macro_state_out\n'
            '      init_micro.state_out: micro_state_out\n'
            '  macro_micro_dispatch:\n'
            '    description: |\n'
            '      Creates initial conditions, the runs a model until conditions\n'
            '      change and that model doesn\'t apply anymore, after which we\n'
            '      pass the state to a second model to finish the calculation.\n'
            '      Actually uses the same model twice, but maybe with different\n'
            '      settings. Note that the model here is a closed box, we cannot\n'
            '      tell that there is a macro-micro inside, other than from the name\n'
            '      of the model and its ports.\n'
            '    components:\n'
            '      init:\n'
            '        ports:\n'
            '          o_f: macro_state_out micro_state_out\n'
            '        description: Calculates initial conditions\n'
            '        implementation: init\n'
            '      first:\n'
            '        ports:\n'
            '          f_init: macro_state_in micro_state_in\n'
            '          o_f: macro_state_out micro_state_out\n'
            '        description: First macro-micro model\n'
            '        implementation: macro_micro\n'
            '      second:\n'
            '        ports:\n'
            '          f_init: macro_state_in micro_state_in\n'
            '        description: First macro-micro model\n'
            '        implementation: macro_micro\n'
            '    conduits:\n'
            '      init.macro_state_out: first.macro_state_in\n'
            '      init.micro_state_out: first.micro_state_in\n'
            '      first.macro_state_out: second.macro_state_in\n'
            '      first.micro_state_out: second.micro_state_in\n'
            'programs:\n'
            '  p1:\n'
            '    description: Implements macro model\n'
            '    executable: /home/user/codes/macro\n'
            '  p2:\n'
            '    description: Implements micro model\n'
            '    executable: /home/user/codes/micro\n'
            '  p3:\n'
            '    description: Program that calculates initial conditions for macro\n'
            '    executable: /home/user/codes/macro_ic\n'
            '  p4:\n'
            '    description: Program that calculates initial conditions for micro\n'
            '    executable: /home/user/codes/micro_ic\n'
            )

    nested_config = load(nested_config_yaml)
    flat_config = flatten(nested_config)

    assert len(flat_config.models) == 1
    assert 'macro_micro_dispatch' in flat_config.models
    model = flat_config.root_model()
    assert model.name == 'macro_micro_dispatch'
    assert len(model.components) == 6
    assert 'init.init_macro' in model.components
    assert 'init.init_micro' in model.components
    assert 'first.macro' in model.components
    assert 'first.micro' in model.components
    assert 'second.macro' in model.components
    assert 'second.micro' in model.components

    assert len(model.conduits) == 8

    assert has_conduit(model, 'init.init_macro.state_out', 'first.macro.state_in')
    assert has_conduit(
            model, 'init.init_micro.state_out', 'first.micro.state_in', 'pad')

    assert has_conduit(model, 'first.macro.boundary_out', 'first.micro.boundary_in')
    assert has_conduit(model, 'first.micro.boundary_out', 'first.macro.boundary_in')

    assert has_conduit(model, 'first.macro.state_out', 'second.macro.state_in')
    assert has_conduit(
            model, 'first.micro.state_out', 'second.micro.state_in', 'last pad')

    assert has_conduit(model, 'second.macro.boundary_out', 'second.micro.boundary_in')
    assert has_conduit(model, 'second.micro.boundary_out', 'second.macro.boundary_in')


def test_flatten_multicast() -> None:
    nested_config_yaml = (
            'ymmsl_version: v0.2\n'
            'description: Testing wiring of multicast conduits\n'
            'models:\n'
            '  outer:\n'
            '    description: Model containing a submodel\n'
            '    components:\n'
            '      c1:\n'
            '        ports:\n'
            '          o_f: out\n'
            '        description: Sends some data\n'
            '        implementation: p1\n'
            '      c2:\n'
            '        ports:\n'
            '          f_init: in\n'
            '          o_f: out1 out2\n'
            '        description: Submodel\n'
            '        implementation: inner\n'
            '      c3:\n'
            '        ports:\n'
            '          f_init: in1 in2 in3\n'
            '        description: Receives some data\n'
            '        implementation: p3\n'
            '      c4:\n'
            '        ports:\n'
            '          f_init: in1 in2\n'
            '        description: Receives some data\n'
            '        implementation: p3\n'
            '    conduits:\n'
            '      c1.out:\n'
            '      - c2.in\n'
            '      - c3.in1\n'
            '      c2.out1:\n'
            '      - c3.in2\n'
            '      - c4.in1\n'
            '      c2.out2:\n'
            '      - c3.in3\n'
            '      - c4.in2\n'
            '  inner:\n'
            '    ports:\n'
            '      f_init: in\n'
            '      o_f: out1 out2\n'
            '    description: Nested simulation model\n'
            '    components:\n'
            '      c1:\n'
            '        ports:\n'
            '          f_init: in\n'
            '          o_f: out\n'
            '        description: Simulation program\n'
            '        implementation: p2\n'
            '      c2:\n'
            '        ports:\n'
            '          f_init: in\n'
            '          o_f: out\n'
            '        description: Simulation program\n'
            '        implementation: p2\n'
            '    conduits:\n'
            '      in:\n'
            '      - c1.in\n'
            '      - c2.in\n'
            '      c1.out:\n'
            '      - out1\n'
            '      - out2\n'
            'programs:\n'
            '  p1:\n'
            '    description: Program that sends something\n'
            '    executable: /home/user/codes/p1\n'
            '  p2:\n'
            '    description: Program that simulates stuff\n'
            '    executable: /home/user/codes/p2\n'
            '  p3:\n'
            '    description: Program that receives some things\n'
            '    executable: /home/user/codes/p2\n'
            )

    nested_config = load(nested_config_yaml)
    flat_config = flatten(nested_config)

    assert len(flat_config.models) == 1
    assert 'outer' in flat_config.models
    model = flat_config.root_model()
    assert model.name == 'outer'

    assert len(model.components) == 5
    assert 'c1' in model.components
    assert 'c2.c1' in model.components
    assert 'c2.c2' in model.components
    assert 'c3' in model.components
    assert 'c4' in model.components

    assert len(model.conduits) == 7
    assert has_conduit(model, 'c1.out', 'c3.in1')
    assert has_conduit(model, 'c1.out', 'c2.c1.in')
    assert has_conduit(model, 'c1.out', 'c2.c2.in')
    assert has_conduit(model, 'c2.c1.out', 'c3.in2')
    assert has_conduit(model, 'c2.c1.out', 'c4.in1')
    assert has_conduit(model, 'c2.c1.out', 'c3.in3')
    assert has_conduit(model, 'c2.c1.out', 'c4.in2')


def test_flatten_passthrough_overload() -> None:
    nested_config_yaml = (
            'ymmsl_version: v0.2\n'
            'description: Testing model passthroughs and custom implementations\n'
            'models:\n'
            '  framework:\n'
            '    description: Model with a passthrough\n'
            '    components:\n'
            '      c1:\n'
            '        ports:\n'
            '          o_f: out\n'
            '        description: Sends some data\n'
            '        implementation: p1\n'
            '      c2:\n'
            '        ports:\n'
            '          f_init: in\n'
            '          o_f: out\n'
            '        description: Extension point\n'
            '        implementation: passthrough\n'
            '      c3:\n'
            '        ports:\n'
            '          f_init: in\n'
            '        description: Receives some data\n'
            '        implementation: p3\n'
            '    conduits:\n'
            '      c1.out: c2.in\n'
            '      c2.out: c3.in\n'
            '  passthrough:\n'
            '    ports:\n'
            '      f_init: in\n'
            '      o_f: out\n'
            '    description: Passes through the message\n'
            '    conduits:\n'
            '      in: out\n'
            'programs:\n'
            '  p1:\n'
            '    description: Program that sends something\n'
            '    executable: /home/user/codes/p1\n'
            '  p2:\n'
            '    description: Program that simulates stuff\n'
            '    executable: /home/user/codes/p2\n'
            '  p3:\n'
            '    description: Program that receives some things\n'
            '    executable: /home/user/codes/p2\n'
            )

    nested_config = load(nested_config_yaml)
    flat_config = flatten(nested_config)

    assert len(flat_config.models) == 1
    assert 'framework' in flat_config.models
    model = flat_config.root_model()
    assert model.name == 'framework'

    assert len(model.components) == 2
    assert 'c1' in model.components
    assert 'c3' in model.components

    assert len(model.conduits) == 1
    assert has_conduit(model, 'c1.out', 'c3.in')

    nested_config = load(nested_config_yaml)
    nested_config.custom_implementations[Reference('framework.c2')] = Reference('p2')
    resolve(Reference([]), nested_config)      # apply custom_implementations
    flat_config = flatten(nested_config)

    assert len(flat_config.models) == 1
    assert 'framework' in flat_config.models
    model = flat_config.root_model()
    assert model.name == 'framework'

    assert len(model.components) == 3
    assert 'c1' in model.components
    assert 'c2' in model.components
    assert 'c3' in model.components

    assert len(model.conduits) == 2
    assert has_conduit(model, 'c1.out', 'c2.in')
    assert has_conduit(model, 'c2.out', 'c3.in')

    assert len(flat_config.custom_implementations) == 0
    assert model.components['c2'].implementation == 'p2'


# optional component without implementation
def test_remove_no_implementation() -> None:
    nested_config_yaml = (
            'ymmsl_version: v0.2\n'
            'description: Testing a component without implementation\n'
            'models:\n'
            '  optional_micro:\n'
            '    description: Macro-micro with optional micro\n'
            '    components:\n'
            '      macro:\n'
            '        ports:\n'
            '          o_i: out\n'
            '          s: in\n'
            '        description: |\n'
            '          Macro model that can run with and without a micro.\n'
            '        implementation: p1\n'
            '      micro:\n'
            '        ports:\n'
            '          f_init: init\n'
            '          o_f: final\n'
            '        description: Optional micro model, not implemented\n'
            '    conduits:\n'
            '      macro.out: micro.init\n'
            '      micro.final: macro.in\n'
            'programs:\n'
            '  p1:\n'
            '    description: Macro model implementation\n'
            '    executable: /home/user/codes/p1\n'
            '  p2:\n'
            '    description: Micro model implementation\n'
            '    executable: /home/user/codes/p2\n'
            )

    nested_config = load(nested_config_yaml)
    flat_config = flatten(nested_config)

    assert len(flat_config.models) == 1
    assert 'optional_micro' in flat_config.models
    model = flat_config.root_model()
    assert model.name == 'optional_micro'

    assert len(model.components) == 1
    assert 'macro' in model.components

    assert len(model.conduits) == 0

    nested_config.custom_implementations[Reference('optional_micro.micro')] = \
        Reference('p2')
    resolve(Reference([]), nested_config)
    flat_config = flatten(nested_config)

    assert len(flat_config.models) == 1
    assert 'optional_micro' in flat_config.models
    model = flat_config.root_model()
    assert model.name == 'optional_micro'

    assert len(model.components) == 2
    assert 'macro' in model.components
    assert 'micro' in model.components

    assert len(model.conduits) == 2
    assert has_conduit(model, 'macro.out', 'micro.init')
    assert has_conduit(model, 'micro.final', 'macro.in')

    assert len(flat_config.custom_implementations) == 0
    assert model.components['micro'].implementation == 'p2'

    nested_config = load(nested_config_yaml)
    nested_config.models['optional_micro'].components['micro'].implementation = \
        Reference('p2')
    nested_config.custom_implementations[Reference('optional_micro.micro')] = None
    resolve(Reference([]), nested_config)
    flat_config = flatten(nested_config)

    assert len(flat_config.models) == 1
    assert 'optional_micro' in flat_config.models
    model = flat_config.root_model()
    assert model.name == 'optional_micro'

    assert len(model.components) == 1
    assert 'macro' in model.components

    assert len(model.conduits) == 0


def test_nested_custom_implementations() -> None:
    nested_config_yaml = (
            'ymmsl_version: v0.2\n'
            'description: Testing nested custom implementations\n'
            'models:\n'
            '  outer:\n'
            '    description: Outer model\n'
            '    components:\n'
            '      c1:\n'
            '        ports:\n'
            '          o_f: out\n'
            '        description: Component c1\n'
            '        implementation: p1\n'
            '      c2:\n'
            '        ports:\n'
            '          f_init: in\n'
            '        description: Component c1\n'
            '        implementation: p1\n'
            '    conduits:\n'
            '      c1.out: c2.in\n'
            '  middle:\n'
            '    ports:\n'
            '      o_f: out\n'
            '    description: Middle model\n'
            '    components:\n'
            '      c1:\n'
            '        ports:\n'
            '          o_f: out\n'
            '        description: Another component c1\n'
            '      c2:\n'
            '        ports:\n'
            '          o_f: out\n'
            '        description: Component c2\n'
            '    conduits:\n'
            '      c2.out: out\n'
            '  inner:\n'
            '    ports:\n'
            '      o_f: out\n'
            '    description: Inner model\n'
            '    components:\n'
            '      c1:\n'
            '        ports:\n'
            '          o_f: out\n'
            '        description: Yet another c1, it could happen...\n'
            '        implementation: p1\n'
            '    conduits:\n'
            '      c1.out: out\n'
            'programs:\n'
            '  p1:\n'
            '    description: Program 1\n'
            '    executable: /home/user/codes/p1\n'
            '  p2:\n'
            '    description: Program 2\n'
            '    executable: /home/user/codes/p2\n'
            'custom_implementations:\n'
            '  outer.c1: middle\n'
            '  outer.c1.c1: inner\n'
            '  outer.c1.c2: inner\n'
            '  outer.c1.c2.c1: p2\n'
            )
    nested_config = load(nested_config_yaml)
    resolve(Reference([]), nested_config)
    flat_config = flatten(nested_config)

    flat_model = flat_config.models['outer']
    assert len(flat_model.components) == 3
    assert flat_model.components['c1.c1.c1'].implementation == 'p1'
    assert flat_model.components['c1.c2.c1'].implementation == 'p2'
    assert len(flat_model.conduits) == 1
    assert flat_model.conduits[0].sender == 'c1.c2.c1.out'
    assert flat_model.conduits[0].receiver == 'c2.in'
