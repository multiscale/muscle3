from enum import Enum
import logging
import os
from pathlib import Path
from threading import Condition, Lock, Thread
import time
from typing import cast, Dict, List, Tuple

from qcg.pilotjob.api.job import Jobs as QCGJobs
from qcg.pilotjob.api.manager import Manager as QCGManager
from ymmsl import Component, Configuration, Reference

from libmuscle.manager.run_dir import RunDir


_logger = logging.getLogger(__name__)


class _ProcessStatus(Enum):
    SUBMITTED = 0,      # we sent it to PJM
    RUNNING = 1,        # PJM says it's queued or executing
    DONE = 2,           # PJM says it is done
    ERROR = 3           # PJM says it is done, unexpectedly


class ProcessManager:
    """Starts, stops and monitors instance processes.

    The ProcessManager starts any needed instance processes, stops them
    when needed, and monitors them for crashes. If a process crashes,
    it will detect that, log it, and shut down the other processes as
    well.
    """
    def __init__(
            self, configuration: Configuration, run_dir: RunDir
            ) -> None:
        """Construct a ProcessManager.

        Args:
            expected_instances: List of instance names expected to
                    exist at some point during the simulation.
            run_dir: Path to working directory for this run.
        """
        self._config = configuration
        self._run_dir = run_dir

        self._status = dict()  # type: Dict[Reference, _ProcessStatus]
        self._status_lock = Lock()
        self._all_done = Condition(self._status_lock)
        self._simulation_started = False

        self._job_ids = list()    # type: List[str]

        # make manager create its dir inside muscle_dir
        cwd = Path.cwd()
        os.chdir(str(run_dir.muscle_dir))
        self._qcg_manager = QCGManager()
        os.chdir(str(cwd))

        self._manager_lock = Lock()

        # create and start monitoring thread
        _logger.debug('Starting monitoring thread')
        self._monitor_thread = Thread(target=self._monitor_instances)
        self._monitor_thread.start()

        with self._manager_lock:
            _logger.info('Available resources: {}'.format(
                self._qcg_manager.resources()))

    def start_all(self) -> None:
        """Start all instances required by the simulation."""
        _logger.info('Starting all instances')

        qcg_jobs = QCGJobs()
        for instance_name, component in self._required_instances():
            impl_name = cast(Reference, component.implementation)
            impl = self._config.implementations[impl_name]
            res = self._config.resources[component.name]

            # write user script
            if not impl.script.startswith('#!'):
                user_script = '#!/bin/bash\n\n{}'.format(impl.script)
            else:
                user_script = impl.script

            idir = self._run_dir.add_instance_dir(instance_name)
            user_script_file = idir / 'user_script.sh'
            with user_script_file.open('w') as f:
                f.write(user_script)
            user_script_file.chmod(0o750)

            # create MUSCLE run script
            run_script = '#!/bin/bash\n\n'
            run_script += 'export MUSCLE_START_DIR={}\n'.format(Path.cwd())
            run_script += 'export MUSCLE_INSTANCE={}\n'.format(instance_name)
            run_script += '{}\n'.format(user_script_file)
            run_script_file = idir / 'run_script.sh'
            with run_script_file.open('w') as f:
                f.write(run_script)
            run_script_file.chmod(0o750)

            # create work dir
            workdir = idir / 'work_dir'
            workdir.mkdir()

            # paths to redirect output to
            outfile = str(idir / '{}.out'.format(instance_name))
            errfile = str(idir / '{}.err'.format(instance_name))

            _logger.debug('Adding job {} {} {} {} {}'.format(
                instance_name, user_script_file, res.num_cores, outfile,
                errfile))

            qcg_jobs.add(
                    name=str(instance_name),
                    wd=str(workdir),
                    script=str(run_script_file),
                    numCores=res.num_cores,
                    stdout=outfile, stderr=errfile)

            with self._status_lock:
                self._status[instance_name] = _ProcessStatus.SUBMITTED

        _logger.info('Jobs: {}'.format(qcg_jobs))
        _logger.info('Going to call submit()')
        with self._manager_lock:
            _logger.info('Calling submit()')
            self._job_ids = self._qcg_manager.submit(qcg_jobs)
            _logger.info('Submitted')

    def wait(self) -> bool:
        """Waits until all instances are done.

        This function blocks, and returns after each expected instance
        has been started and stopped, signalling the end of the
        simulation run.

        Returns:
            True iff the model finished successfully.
        """
        def all_done() -> bool:
            return all(map(
                    lambda x: x in (_ProcessStatus.DONE, _ProcessStatus.ERROR),
                    self._status.values()))

        with self._all_done:
            while not all_done():
                self._all_done.wait()

        with self._status_lock:
            return _ProcessStatus.ERROR not in self._status.values()

    def _required_instances(self) -> List[Tuple[Reference, Component]]:
        """Creates a list of elements to expect to exist.

        The first item of each returned tuple is the name of the
        instance, the second the component it is an instance of.
        """
        def increment(index: List[int], dims: List[int]) -> None:
            # assumes index and dims are the same length > 0
            # modifies index argument
            i = len(index) - 1
            index[i] += 1
            while index[i] == dims[i]:
                index[i] = 0
                i -= 1
                if i == -1:
                    break
                index[i] += 1

        def generate_indices(multiplicity: List[int]) -> List[List[int]]:
            # n-dimensional counter
            indices = list()    # type: List[List[int]]

            index = [0] * len(multiplicity)
            indices.append(index.copy())
            increment(index, multiplicity)
            while sum(index) > 0:
                indices.append(index.copy())
                increment(index, multiplicity)
            return indices

        result = list()     # type: List[Tuple[Reference, Component]]
        for component in self._config.model.components:
            if len(component.multiplicity) == 0:
                result.append((component.name, component))
            else:
                for index in generate_indices(component.multiplicity):
                    result.append((component.name + index, component))
        return result

    def _monitor_instances(self) -> None:
        """Monitors status of instances.

        This is run in a separate thread, and keeps an eye on the
        instances' statuses in the pilot job manager.
        """
        _logger.info('Monitoring thread started')
        sleep_time = 0.1
        simulation_started = False
        while True:
            none_running = True
            if self._job_ids:
                with self._manager_lock:
                    status = self._qcg_manager.status(self._job_ids)
            else:
                status = {'jobs': {}}

            _logger.info('Monitoring instances, status: {}'.format(status))
            for name_str, data in status['jobs'].items():
                if name_str == 'muscle_manager':
                    continue

                simulation_started = True
                name = Reference(name_str)
                pj_status = data['data']['status']

                is_running = pj_status in ('QUEUED', 'SCHEDULED', 'EXECUTING')
                is_done = pj_status == 'SUCCEED'
                has_error = pj_status == 'FAILED'
                was_cancelled = pj_status in ('CANCELED', 'OMITTED')

                with self._status_lock:
                    if name not in self._status:
                        self._fatal_error(
                                'Unknown process {} encountered'.format(name))

                    if is_running:
                        none_running = False
                        if self._status[name] not in (
                                _ProcessStatus.SUBMITTED,
                                _ProcessStatus.RUNNING):
                            self._fatal_error((
                                    'Running process {} in invalid state'
                                    ' {}').format(name, self._status[name]))
                        self._status[name] = _ProcessStatus.RUNNING

                    elif is_done:
                        self._status[name] = _ProcessStatus.DONE

                    elif has_error:
                        if self._status[name] != _ProcessStatus.ERROR:
                            self._status[name] = _ProcessStatus.ERROR
                            # TODO: point user to relevant log files
                            self._fatal_error(
                                    'Process {} quit with an error'.format(
                                        name))
                    elif was_cancelled:
                        if self._status[name] != _ProcessStatus.ERROR:
                            self._status[name] = _ProcessStatus.ERROR
                            self._fatal_error((
                                    'Process {} was stopped due to another'
                                    ' error').format(name))

            if simulation_started and none_running:
                with self._status_lock:
                    self._all_done.notify_all()
                break

            if sleep_time < 10:
                sleep_time *= 1.6
            time.sleep(sleep_time)

    def _fatal_error(self, message: str) -> None:
        """Handles a fatal error."""
        _logger.error(message)
        if self._job_ids:
            with self._manager_lock:
                status = self._qcg_manager.status(self._job_ids)
                for name, data in status['jobs'].items():
                    if data['data']['status'] in (
                            'QUEUED', 'SCHEDULED', 'EXECUTING'):
                        # Not implemented yet in QCG-PJ.
                        # self._qcg_manager.cancel(name)
                        pass
