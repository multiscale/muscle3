"""Tests for MuscleTester and ImplementationTester."""
import pytest
from pathlib import Path

from ymmsl.v0_2 import (
    Configuration,
    ExecutionModel,
    Model,
    Ports,
    Program,
    Reference,
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


def test_add_tester_model_to_config(tmp_run_dir: Path, program_config: Configuration,
                                    model_config: Configuration) -> None:
    tester = MuscleTester(tmp_run_dir)
    result_program = tester._add_tester_component(program_config, "micro_model_program")
    result_model = tester._add_tester_component(model_config, "macro_model")
    assert Reference("muscle3_implementation_tester") in result_program.models
    assert Reference("muscle3_implementation_tester") in result_model.models

    tester_model = result_program.models[Reference("muscle3_implementation_tester")]
    assert Reference("muscle3_implementation_tester") in tester_model.components


def test_add_tester_program_to_config(tmp_run_dir: Path, program_config: Configuration
                                      ) -> None:
    tester = MuscleTester(tmp_run_dir)
    result = tester._add_tester_component(program_config, "micro_model_program")
    assert Reference("muscle3_implementation_tester") in result.programs

    tester_prog = result.programs[Reference("muscle3_implementation_tester")]
    assert tester_prog.execution_model == ExecutionModel.MANUAL


def test_add_test_ports_to_config(tmp_run_dir: Path, program_config: Configuration
                                  ) -> None:
    tester = MuscleTester(tmp_run_dir)
    result = tester._add_tester_component(program_config, "micro_model_program")
    tester_model = result.models[Reference("muscle3_implementation_tester")]
    tester_comp = tester_model.components[Reference("muscle3_implementation_tester")]
    # init_in is a receiving port of micro_model_program → tester sends on it (O_I)
    assert "init_in" in [str(p) for p in tester_comp.ports.sending_port_names()]

    # final_out is a sending port of micro_model_program → tester receives on it (S)
    assert "final_out" in [str(p) for p in tester_comp.ports.receiving_port_names()]


def test_add_test_conduits_to_config(tmp_run_dir: Path, program_config: Configuration
                                     ) -> None:
    tester = MuscleTester(tmp_run_dir)
    result = tester._add_tester_component(program_config, "micro_model_program")
    tester_model = result.models[Reference("muscle3_implementation_tester")]
    conduit_pairs = {
        (str(c.sender), str(c.receiver)) for c in tester_model.conduits
    }
    # Tester sends init_in → implementation receives init_in
    assert (
        "muscle3_implementation_tester.init_in",
        "micro_model_program.init_in",
    ) in conduit_pairs
    # Implementation sends final_out → tester receives final_out
    assert (
        "micro_model_program.final_out",
        "muscle3_implementation_tester.final_out",
    ) in conduit_pairs


def test_original_config_unchanged(tmp_run_dir: Path, program_config: Configuration
                                   ) -> None:
    """add_tester_component should not remove the original model/program."""
    tester = MuscleTester(tmp_run_dir)
    result = tester._add_tester_component(program_config, "micro_model_program")
    assert Reference("micro_model_program") in result.programs


def test_error_for_unknown_implementation(tmp_run_dir: Path) -> None:
    config = Configuration(models=[], programs=[])
    tester = MuscleTester(tmp_run_dir)
    with pytest.raises(ValueError, match="No implementation 'nonexistent'"):
        tester._add_tester_component(config, "nonexistent")
