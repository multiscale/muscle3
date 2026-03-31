from types import TracebackType
from pathlib import Path
import subprocess
from typing import Optional

import ymmsl.v0_2
from ymmsl.v0_2 import Component, Conduit, Ports, Configuration, Reference

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

    def prune_ymmsl_by_implementation(
        self, config: Configuration, implementation: str
    ) -> Configuration:
        """
        Return a pruned YMMSL configuration that only contains the parts needed for the
        given implementation.
        """
        pruned_models = {}
        for model_name, model in config.models.items():
            model.components = {
                name: comp
                for name, comp in model.components.items()
                if comp.implementation == implementation
            }

            valid_components = set(model.components.keys())

            model.conduits = [
                conduit
                for conduit in model.conduits
                if str(conduit.sender).split(".")[0] in valid_components
                and str(conduit.receiver).split(".")[0] in valid_components
            ]

            if model.components:
                pruned_models[model_name] = model

        config.models = pruned_models
        return config

    def add_tester_component(
        self, config: Configuration, implementation: str
    ) -> Configuration:
        """
        Add a 'muscle3_implementation_tester' component to a pruned YMMSL v0.2 config.
            - Assumes exactly one remaining component per model.
            - Verifies the component uses the given implementation.
            - Marks tester as manual and copies ports.
            - Adds conduits connecting tester ports to the target component.
        """
        for model in config.models.values():
            target_name, target_comp = next(iter(model.components.items()))

            if target_comp.implementation != implementation:
                raise ValueError(
                    f"Remaining component '{target_name}' uses implementation "
                    f"'{target_comp.implementation}', expected '{implementation}'."
                )

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
                            f"muscle3_implementation_tester.send_{port_name}",
                            f"{target_name}.{port_name}",
                        )
                        model.conduits.append(conduit)

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
                            f"muscle3_implementation_tester.receive_{port_name}",
                        )
                        model.conduits.append(conduit)

            # Create Ports object with collected port names
            tester_ports = Ports(
                o_i=tester_o_i_ports if tester_o_i_ports else None,
                s=tester_s_ports if tester_s_ports else None,
            )

            tester_comp = Component(
                name="muscle3_implementation_tester",
                ports=tester_ports,
                description="Manual tester component for implementation testing",
                implementation=None,  # makes it manual
                optional=True,  # manager won't require it
            )

            model.components[Reference("muscle3_implementation_tester")] = tester_comp
        return config

    def start_implementation(
        self, ymmsl_path: str, implementation: str, *, default_timeout: float = 60
    ) -> ImplementationTester:
        ymmsl_config = ymmsl.load_as(ymmsl.v0_2.Configuration, Path(ymmsl_path))

        pruned_ymmsl_config = self.prune_ymmsl_by_implementation(
            ymmsl_config, implementation
        )

        test_ymmsl_config = self.add_tester_component(
            pruned_ymmsl_config, implementation
        )

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
