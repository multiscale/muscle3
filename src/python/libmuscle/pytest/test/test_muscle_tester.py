from pathlib import Path

import pytest
from ymmsl.v0_2 import (
    Conduit,
    Configuration,
    ExecutionModel,
    Identifier,
    Model,
    Operator,
    Port,
    Ports,
    Program,
    Reference,
    Timeline,
    resolve_timelines,
)

from libmuscle.pytest.implementation_tester import (
    PARENT_TESTER_NAME,
    SIBLING_TESTER_NAME,
)
from libmuscle.pytest.muscle_tester import MuscleTester


@pytest.fixture
def tmp_run_dir(tmp_path: Path) -> Path:
    run_dir = tmp_path / "run_dir"
    run_dir.mkdir()
    return run_dir


@pytest.fixture
def program_config() -> Configuration:
    """Configuration whose implementation-under-test is a Program."""
    prog = Program(
        name="micro_model_program",
        ports=Ports(f_init=["init_in"], o_f=["final_out"]),
        execution_model=ExecutionModel.MANUAL,
    )
    return Configuration(programs=[prog])


@pytest.fixture
def model_config() -> Configuration:
    """Configuration whose implementation-under-test is a Model."""
    sub_model = Model(
        name="macro_model",
        ports=Ports(o_i=["state_out"], s=["update_in"]),
    )
    return Configuration(models=[sub_model])


@pytest.fixture
def meso_program_config() -> Configuration:
    """Configuration whose implementation-under-test is a Program with all
    operators, with its O_I and S ports on two different timelines."""
    prog = Program(
        name="meso_model_program",
        ports=Ports(
            [
                Port(Identifier("init_in"), Operator.F_INIT),
                Port(Identifier("state_out"), Operator.O_I, Timeline("sub1")),
                Port(Identifier("update_in"), Operator.S, Timeline("sub2")),
                Port(Identifier("final_out"), Operator.O_F),
            ]
        ),
        execution_model=ExecutionModel.MANUAL,
    )
    return Configuration(programs=[prog])


@pytest.fixture
def meso_model_config() -> Configuration:
    """Configuration whose implementation-under-test is a Model with all operators,
    with its O_I and S ports on two different timelines."""
    sub_model = Model(
        name="meso_model",
        ports=Ports(
            [
                Port(Identifier("init_in"), Operator.F_INIT),
                Port(Identifier("state_out"), Operator.O_I, Timeline("sub1")),
                Port(Identifier("update_in"), Operator.S, Timeline("sub2")),
                Port(Identifier("final_out"), Operator.O_F),
            ]
        ),
    )
    return Configuration(models=[sub_model])


def test_add_test_model_to_config(
    tmp_run_dir: Path, meso_model_config: Configuration
) -> None:
    tester = MuscleTester(tmp_run_dir)
    tester._add_test_model(meso_model_config, "meso_model")

    test_model = meso_model_config.models[Reference("muscle3_test_model")]
    assert set(test_model.components) == {
        Reference(PARENT_TESTER_NAME),
        Reference(SIBLING_TESTER_NAME),
        Reference("meso_model"),
    }


def test_add_tester_program_to_config(
    tmp_run_dir: Path, meso_program_config: Configuration
) -> None:
    tester = MuscleTester(tmp_run_dir)
    tester._add_test_model(meso_program_config, "meso_model_program")

    for name in (
        PARENT_TESTER_NAME,
        SIBLING_TESTER_NAME,
    ):
        tester_prog = meso_program_config.programs[Reference(name)]
        assert tester_prog.execution_model == ExecutionModel.MANUAL


def test_add_test_ports_to_config(
    tmp_run_dir: Path, meso_program_config: Configuration
) -> None:
    tester = MuscleTester(tmp_run_dir)
    tester._add_test_model(meso_program_config, "meso_model_program")
    test_model = meso_program_config.models[Reference("muscle3_test_model")]

    def ports(tester_name: str) -> dict[str, tuple[Operator, Timeline]]:
        component = test_model.components[Reference(tester_name)]
        return {
            str(name): (port.operator, port.timeline)
            for name, port in component.ports.items()
        }

    # The parent mirrors the F_INIT and O_F ports, and nests the sibling
    assert ports(PARENT_TESTER_NAME) == {
        "init_in": (Operator.O_I, Timeline([])),
        "final_out": (Operator.S, Timeline([])),
        "__sibling_settings_out__": (Operator.O_I, Timeline([])),
    }

    # The sibling mirrors the O_I and S ports, on the same timelines
    assert ports(SIBLING_TESTER_NAME) == {
        "state_out": (Operator.S, Timeline("sub1")),
        "update_in": (Operator.O_I, Timeline("sub2")),
    }


def test_add_test_conduits_to_config(
    tmp_run_dir: Path, meso_program_config: Configuration
) -> None:
    tester = MuscleTester(tmp_run_dir)
    tester._add_test_model(meso_program_config, "meso_model_program")
    test_model = meso_program_config.models[Reference("muscle3_test_model")]

    expected = [
        # The parent sends on F_INIT and receives from O_F
        Conduit(f"{PARENT_TESTER_NAME}.init_in", "meso_model_program.init_in"),
        Conduit("meso_model_program.final_out", f"{PARENT_TESTER_NAME}.final_out"),
        # The sibling receives from O_I and sends on S
        Conduit("meso_model_program.state_out", f"{SIBLING_TESTER_NAME}.state_out"),
        Conduit(f"{SIBLING_TESTER_NAME}.update_in", "meso_model_program.update_in"),
        # The parent nests the sibling in its timeline
        Conduit(
            f"{PARENT_TESTER_NAME}.__sibling_settings_out__",
            f"{SIBLING_TESTER_NAME}.muscle_settings_in",
        ),
    ]
    assert len(test_model.conduits) == len(expected)
    for conduit in expected:
        assert conduit in test_model.conduits

    # Via F_INIT, the parent nests the implementation next to the sibling.
    resolve_timelines(test_model)
    assert {
        str(name): component.timeline
        for name, component in test_model.components.items()
    } == {
        PARENT_TESTER_NAME: Timeline(PARENT_TESTER_NAME),
        "meso_model_program": Timeline(f"{PARENT_TESTER_NAME}:meso_model_program"),
        SIBLING_TESTER_NAME: Timeline(f"{PARENT_TESTER_NAME}:{SIBLING_TESTER_NAME}"),
    }


def test_original_config_unchanged(
    tmp_run_dir: Path, program_config: Configuration
) -> None:
    """_add_test_model should not remove the original model/program."""
    tester = MuscleTester(tmp_run_dir)
    tester._add_test_model(program_config, "micro_model_program")
    assert Reference("micro_model_program") in program_config.programs


def test_error_for_unknown_implementation(tmp_run_dir: Path) -> None:
    config = Configuration(models=[], programs=[])
    tester = MuscleTester(tmp_run_dir)
    with pytest.raises(ValueError, match="No implementation 'nonexistent'"):
        tester._add_test_model(config, "nonexistent")


def test_add_settings_conduit_without_f_init(
    tmp_run_dir: Path, model_config: Configuration
) -> None:
    tester = MuscleTester(tmp_run_dir)
    tester._add_test_model(model_config, "macro_model")
    test_model = model_config.models[Reference("muscle3_test_model")]

    # Without F_INIT ports, the parent nests the implementation via muscle_settings_in
    assert (
        Conduit(
            f"{PARENT_TESTER_NAME}.__settings_in__", "macro_model.muscle_settings_in"
        )
        in test_model.conduits
    )

    # This raises if the timelines are not consistent
    resolve_timelines(test_model)
    implementation = test_model.components[Reference("macro_model")]
    assert implementation.timeline == Timeline(f"{PARENT_TESTER_NAME}:macro_model")


def test_add_matching_timelines(
    tmp_run_dir: Path, meso_program_config: Configuration
) -> None:
    tester = MuscleTester(tmp_run_dir)
    tester._add_test_model(meso_program_config, "meso_model_program")
    test_model = meso_program_config.models[Reference("muscle3_test_model")]

    # Each timeline of the implementation matches the same one of the sibling
    assert test_model.matching_timelines is not None
    assert [match.matches for match in test_model.matching_timelines] == [
        {
            Timeline(f"{PARENT_TESTER_NAME}:meso_model_program.sub1"),
            Timeline(f"{PARENT_TESTER_NAME}:{SIBLING_TESTER_NAME}.sub1"),
        },
        {
            Timeline(f"{PARENT_TESTER_NAME}:meso_model_program.sub2"),
            Timeline(f"{PARENT_TESTER_NAME}:{SIBLING_TESTER_NAME}.sub2"),
        },
    ]


def test_no_sibling_without_o_i_and_s_ports(
    tmp_run_dir: Path, program_config: Configuration
) -> None:
    tester = MuscleTester(tmp_run_dir)
    tester._add_test_model(program_config, "micro_model_program")

    test_model = program_config.models[Reference("muscle3_test_model")]
    assert set(test_model.components) == {
        Reference(PARENT_TESTER_NAME),
        Reference("micro_model_program"),
    }
    assert Reference(SIBLING_TESTER_NAME) not in program_config.programs
