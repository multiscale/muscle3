from pathlib import Path

from ymmsl import Reference


class RunDir:
    """Manages a run directory containing files for a simulation run.

    The directory is laid out as follows:

    <run_dir>/
        input/
        muscle3/
            1_<name>.ymmsl
            2_<name>.ymmsl
            muscle_manager.log
            muscle_stats.sqlite
            .qcgpj/
        instances/
            <instance_name[i]>/
                run_script.sh
                <instance_name[i]>.out
                <instance_name[i]>.err
                work_dir/
    """
    def __init__(self, run_dir: Path) -> None:
        """Create a RunDir managing the given directory.

        This creates the run dir if it does not exist.
        """
        self.path = run_dir

        if not self.path.exists():
            self.path.mkdir()

        self.muscle_dir = self.path / 'muscle3'
        if not self.muscle_dir.exists():
            self.muscle_dir.mkdir()

        instances_dir = self.path / 'instances'
        if not instances_dir.exists():
            instances_dir.mkdir()

    def add_instance_dir(self, name: Reference) -> Path:
        """Add a directory for this instance to the run dir.

        Args:
            name: Name of the instance

        Returns:
            The path to the new, empty directory
        """
        idir = self.path / 'instances' / str(name)
        if idir.exists():
            raise ValueError('Instance already has a directory')
        idir.mkdir()
        return idir
