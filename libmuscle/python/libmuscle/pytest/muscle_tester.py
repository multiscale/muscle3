from types import TracebackType
from pathlib import Path
import subprocess
from typing import Optional

import ymmsl.v0_2
from ymmsl.v0_2 import (
    Component,
    Conduit,
    Ports,
    Configuration,
    Reference,
    Program,
    Model,
    ExecutionModel,
)

from libmuscle.pytest.implementation_tester import ImplementationTester


class MuscleTester:
    """Helper class to test an implementation."""

    def __init__(self, run_dir: Path) -> None:
        self.run_dir = run_dir
        self._manager_process: Optional[subprocess.Popen] = None

    def __enter__(self) -> "MuscleTester":
        """Allows usage in a with-statement"""
        return self

    def __exit__(
        self,
        typ: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        """Allows usage in a with-statement"""
        self.cleanup()

    def add_tester_component(
        self, config: Configuration, implementation: str
    ) -> Configuration:
        """
        Add a 'muscle3_implementation_tester' as a tester component
        - add the s and o_i ports for the component.
        - add the conduits which connect to the implementation which is connected to
        a specific component.
        - set it to manual: class ExecutionModel(*values), describes how to start a model
        component: MANUAL=5, Let the user start it by hand.
        """
        target_model: Optional[Model] = None
        target_name: Optional[Reference] = None
        target_comp: Optional[Component] = None

        for model in config.models.values():
            for comp_name, comp in model.components.items():
                if comp.implementation == implementation:
                    if target_comp is not None:
                        raise ValueError(
                            f"Found multiple components using implementation "
                            f"'{implementation}': '{target_name}' and '{comp_name}'. "
                            f"Expected exactly one component."
                        )
                    target_model = model
                    target_name = comp_name
                    target_comp = comp

        if target_model is None or target_comp is None or target_name is None:
            raise ValueError(
                f"No component found using implementation '{implementation}'."
            )

        print(f"The target model is {target_model}")
        print(f"The target name is {target_name}")
        print(f"The target component is {target_comp}")

        tester_o_i_ports = []
        tester_s_ports = []

        # F_INIT and S of target (inputs) → tester needs O_I (outputs) to send to them
        for port_attr in ["f_init", "s"]:
            ports = getattr(target_comp.ports, port_attr, None)
            if ports:
                if isinstance(ports, str):
                    ports = [ports]
                tester_o_i_ports.extend([f"send_{port}" for port in ports])

                for port_name in ports:
                    conduit = Conduit(
                        f"tester.send_{port_name}",
                        f"{target_name}.{port_name}",
                    )
                    target_model.conduits.append(conduit)

        print(f"The tester O_I ports are: {tester_o_i_ports}")

        # O_I and O_F of target (outputs) → tester needs S (inputs) to receive from them
        for port_attr in ["o_i", "o_f"]:
            ports = getattr(target_comp.ports, port_attr, None)
            if ports:
                if isinstance(ports, str):
                    ports = [ports]
                tester_s_ports.extend([f"receive_{port}" for port in ports])

                for port_name in ports:
                    conduit = Conduit(
                        f"{target_name}.{port_name}",
                        f"tester.receive_{port_name}",
                    )
                    target_model.conduits.append(conduit)

        print(f"The tester S ports are: {tester_s_ports}")

        tester_ports = Ports(
            o_i=tester_o_i_ports if tester_o_i_ports else None,
            s=tester_s_ports if tester_s_ports else None,
        )

        tester_comp = Component(
            name="tester",
            ports=tester_ports,
            description="Manual tester component for implementation testing",
            implementation="muscle3_implementation_tester",
            optional=False,
        )
        target_model.components[Reference("tester")] = tester_comp

        tester_program = Program(
            name="muscle3_implementation_tester",
            execution_model=ExecutionModel.MANUAL,
            description="Manual tester program for implementation testing",
        )
        if config.programs is None:
            config.programs = {}
        config.programs[Reference("muscle3_implementation_tester")] = tester_program
        return config

    def start_implementation(
        self, ymmsl_path: str, implementation: str, *, default_timeout: float = 60
    ) -> ImplementationTester:
        ymmsl_config = ymmsl.load_as(ymmsl.v0_2.Configuration, Path(ymmsl_path))
        test_ymmsl_config = self.add_tester_component(ymmsl_config, implementation)

        # Save the test configuration to a temporary file
        test_ymmsl_path = self.run_dir / "test_config.ymmsl"
        ymmsl.save(test_ymmsl_config, test_ymmsl_path)

        # Start the manager process with --start-all flag
        manager_stdout = self.run_dir / "manager_stdout.txt"
        manager_stderr = self.run_dir / "manager_stderr.txt"

        with open(manager_stdout, "w") as f_out, open(manager_stderr, "w") as f_err:
            self._manager_process = subprocess.Popen(
                ["muscle_manager", "--start-all", str(test_ymmsl_path)],
                stdout=f_out,
                stderr=f_err,
                cwd=str(self.run_dir),
            )

        return ImplementationTester(default_timeout)

    def cleanup(self) -> None:
        # Clean up any running processes, etc. log appropriate errors when the test
        # implementation doesn't shut down nicely?
        # N.B. allow calling this multiple times
        if self._manager_process is not None:
            # Try to terminate gracefully first
            self._manager_process.terminate()
            try:
                self._manager_process.wait(timeout=5.0)
            except subprocess.TimeoutExpired:
                # Force kill if it doesn't terminate gracefully
                self._manager_process.kill()
                self._manager_process.wait()
            self._manager_process = None
