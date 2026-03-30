from types import TracebackType
from pathlib import Path

from libmuscle.pytest.implementation_tester import ImplementationTester


class MuscleTester:
    """Helper class to test an implementation."""

    def __init__(self, run_dir: Path) -> None:
        self.run_dir = run_dir

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

    def start_implementation(
        self, ymmsl: str, implementation: str, *, default_timeout: float = 60
    ) -> ImplementationTester:
        # 1. Parse ymmsl string
        # 2. Remove all models and programs except for the one(s) we need to test
        #    `implementation`.
        # 3. Add a component (muscle3_implementation_tester), mark as manual (so manager
        #    doesn't start it), create one port (O_I/S) for each port of the
        #    implementation to be tested, and add conduits to connect the ports.
        # 4. Create a subprocess to start the manager, see e.g.
        #    muscle3/integration_test/conftest.py:make_server_process, ensure manager is
        #    invoked as with --start-all
        # 5. Create an ImplementationTester instance and return it
        ...

    def cleanup(self) -> None:
        # Clean up any running processes, etc. log appropriate errors when the test
        # implementation doesn't shut down nicely?
        # N.B. allow calling this multiple times
        ...
