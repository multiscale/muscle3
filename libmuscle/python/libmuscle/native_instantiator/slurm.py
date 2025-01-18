from itertools import product
import logging
import os
from parsimonious import Grammar, NodeVisitor
from parsimonious.nodes import Node
import subprocess
from typing import Any, cast, List, Optional, Sequence, Tuple


_logger = logging.getLogger(__name__)


_node_range_expression_grammar = Grammar(
        """
        nre = nre_parts ("," nre_parts)*
        nre_parts = nre_part+
        nre_part = identifier ("[" index_set "]")?
        index_set = index_range ("," index_range)*
        index_range = integer ("-" integer)?
        identifier = ~"[a-z 0-9 _-]+"i
        integer = padded_int / int
        int = ~"[0-9]+"
        padded_int = ~"0[0-9]+"
        """
        )


class NREVisitor(NodeVisitor):
    """Processes a parsed NRE and produces a list of nodes.

    Node range expressions are used by SLURM to describe collections of nodes. See
    parse_slurm_nodelist() below.
    """
    def visit_nre(
            self, node: Node,
            visited_children: Tuple[List[str], Sequence[Tuple[Any, List[str]]]]
            ) -> List[str]:
        """Return a list of nodes corresponding to the NRE."""
        nodes = visited_children[0].copy()
        for _, more_nodes in visited_children[1]:
            nodes.extend(more_nodes)
        return nodes

    def visit_nre_parts(
            self, node: Node, visited_children: Sequence[Tuple[str, List[str]]]
            ) -> List[str]:
        """Return a list of node ids for the part."""
        fmt = ''.join([c[0] + '{}' for c in visited_children])
        index_lists = [c[1] for c in visited_children]
        return [fmt.format(*idxs) for idxs in product(*index_lists)]

    def visit_nre_part(
            self, node: Node, visited_children: Tuple[
                str, Sequence[Tuple[Any, List[str], Any]]]
            ) -> Tuple[str, List[str]]:
        """Return the identifier part and a list of indexes for the set."""
        identifier = visited_children[0]
        if not visited_children[1]:
            index_set = ['']
        else:
            index_set = visited_children[1][0][1]
        return identifier, index_set

    def visit_index_set(
            self, node: Node,
            visited_children: Tuple[List[str], Sequence[Tuple[Any, List[str]]]]
            ) -> List[str]:
        """Return a list of indexes corresponding to the set."""
        indexes = visited_children[0].copy()
        for _, more_indexes in visited_children[1]:
            indexes.extend(more_indexes)
        return indexes

    def visit_index_range(
            self, node: Node,
            visited_children: Tuple[
                Tuple[int, int],
                Sequence[
                    Tuple[Any, Tuple[int, int]]
                    ]]
            ) -> List[str]:
        """Return a list of indexes corresponding to the range."""

        def format_str(width: int) -> str:
            if width == -1:
                return '{}'
            return f'{{:0{width}}}'

        start_value, width = visited_children[0]
        if visited_children[1]:
            end_value, _ = visited_children[1][0][1]
            fmt = format_str(width)
            return [fmt.format(i) for i in range(start_value, end_value + 1)]

        fmt = format_str(width)
        return [fmt.format(start_value)]

    def visit_identifier(self, node: Node, _: Sequence[Any]) -> str:
        return node.text

    def visit_integer(
            self, node: Node, visited_children: Sequence[Tuple[int, int]]
            ) -> Tuple[int, int]:
        """Returns the value of the int, and a field width or -1."""
        return visited_children[0]

    def visit_int(self, node: Node, _: Sequence[Any]) -> Tuple[int, int]:
        """Returns the value and a field width of -1."""
        return int(node.text), -1

    def visit_padded_int(self, node: Node, _: Sequence[Any]) -> Tuple[int, int]:
        """Returns the value of the int and the field width."""
        return int(node.text), len(node.text)

    def generic_visit(
            self, node: Node, visited_children: Sequence[Any]) -> Sequence[Any]:
        return visited_children


_nre_visitor = NREVisitor()


def parse_slurm_nodelist(s: str) -> List[str]:
    """Parse a SLURM node range expression and produce node names.

    Exactly what the syntax is for a "node range expression" isn't entirely
    clear. Some examples are given throughout the documentation:

    linux[00-17]
    lx[10-20]
    tux[2,1-2]
    tux[1-2,2]
    tux[1-3]
    linux[0-64,128]
    alpha,beta,gamma
    lx[15,18,32-33]
    linux[0000-1023]
    rack[0-63]_blade[0-41]

    unit[0-31]rack is invalid

    If a range uses leading zeros, then so should the generated indexes.
    See _node_range_expression_grammar above for my best guess at the
    correct grammar.

    This function takes a string containing an NRE and returns the
    corresponding list of node names.
    """
    ast = _node_range_expression_grammar.parse(s)
    return cast(List[str], _nre_visitor.visit(ast))


_nodes_cores_expression_grammar = Grammar(
        """
        nce = nce_run ("," nce_run)*
        nce_run = int ("(" run_length ")")?
        run_length = "x" int
        int = ~"[0-9]+"
        """
        )


class NCEVisitor(NodeVisitor):
    """Processes a parsed NCE and produces a list of cpu counts per node.

    Nodes cores expressions are used by SLURM to describe cores on a collection of
    nodes.  See parse_slurm_nodes_cores() below.
    """
    def visit_nce(
            self, node: Node,
            visited_children: Tuple[List[int], Sequence[Tuple[Any, List[int]]]]
            ) -> List[int]:
        """Return a list of nodes corresponding to the NRE."""
        nodes_cores = visited_children[0].copy()
        for _, more_nodes_cores in visited_children[1]:
            nodes_cores.extend(more_nodes_cores)
        return nodes_cores

    def visit_nce_run(
            self, node: Node,
            visited_children: Tuple[int, Sequence[Tuple[Any, int, Any]]]
            ) -> List[int]:
        """Return a list of core counts produced by this run."""
        num_cores = visited_children[0]
        result = [num_cores]

        if visited_children[1]:
            result *= visited_children[1][0][1]

        return result

    def visit_run_length(
            self, node: Node, visited_children: Tuple[str, int]) -> int:
        """Return the number of repetitions."""
        return visited_children[1]

    def visit_int(self, node: Node, _: Sequence[Any]) -> int:
        """Returns the value as an int"""
        return int(node.text)

    def generic_visit(
            self, node: Node, visited_children: Sequence[Any]) -> Sequence[Any]:
        return visited_children


_nce_visitor = NCEVisitor()


def parse_slurm_nodes_cores(s: str) -> List[int]:
    """Parse a SLURM nodes cores expression and produce node names.

    The sbatch documentation page describes the format under
    SLURM_JOB_CPUS_PER_NODE as CPU_count[(xnumber_of_nodes)][,CPU_count
    [(xnumber_of_nodes)] ...]. and gives the example of '72(x2),36' describing a set of
    three nodes, the first two with 72 cores and the third with 36.

    See _nodes_cores_expression_grammar above for the corresponding grammar.

    This function takes a string containing an NCE and returns the corresponding list of
    node names.
    """
    ast = _nodes_cores_expression_grammar.parse(s)
    return cast(List[int], _nce_visitor.visit(ast))


class SlurmQuirks:
    """Collects features of the present SLURM."""
    overlap: bool
    """True iff --overlap must be specified for srun."""
    cpu_bind: str
    """CPU binding argument, --cpu-bind or --cpu_bind."""


class SlurmInfo:
    """Detects and holds information about the present SLURM scheduler."""
    def __init__(self) -> None:
        if self.in_slurm_allocation():
            self.version = self._slurm_version()
            self.quirks = SlurmQuirks()

            self.quirks.overlap = self.version > (20, 2)
            self.quirks.cpu_bind = (
                    '--cpu-bind' if self.version > (17, 2) else '--cpu_bind')

    def in_slurm_allocation(self) -> bool:
        """Check whether we're in a SLURM allocation.

        Returns true iff SLURM was detected.
        """
        return 'SLURM_JOB_ID' in os.environ

    def get_nodes(self) -> List[str]:
        """Get a list of node names from SLURM_JOB_NODELIST.

        This inspects SLURM_JOB_NODELIST or SLURM_NODELIST and returns an
        expanded list of node names.

        If SLURM_JOB_NODELIST is "node[020-023]" then this returns
        ["node020", "node021", "node022", "node023"].
        """
        nodelist = os.environ.get('SLURM_JOB_NODELIST')
        if not nodelist:
            nodelist = os.environ.get('SLURM_NODELIST')
        if not nodelist:
            raise RuntimeError('SLURM_(JOB_)NODELIST not set, are we running locally?')

        _logger.debug(f'SLURM node list: {nodelist}')

        return parse_slurm_nodelist(nodelist)

    def get_logical_cpus_per_node(self) -> List[int]:
        """Return the number of logical CPU cores per node.

        This returns a list with the number of cores of each node in the result of
        get_nodes(), which gets read from SLURM_JOB_CPUS_PER_NODE.
        """
        sjcpn = os.environ.get('SLURM_JOB_CPUS_PER_NODE')
        _logger.debug(f'SLURM_JOB_CPUS_PER_NODE: {sjcpn}')

        if sjcpn:
            return parse_slurm_nodes_cores(sjcpn)
        else:
            scon = os.environ.get('SLURM_CPUS_ON_NODE')
            _logger.debug(f'SLURM_CPUS_ON_NODE: {scon}')

            snn = os.environ.get('SLURM_JOB_NUM_NODES')
            if not snn:
                snn = os.environ.get('SLURM_NNODES')
            _logger.debug(f'SLURM num nodes: {snn}')

            if scon and snn:
                return [int(scon)] * int(snn)

        raise RuntimeError(
                'SLURM_JOB_CPUS_PER_NODE is not set in the environment, and also'
                ' SLURM_CPUS_ON_NODE is missing or neither SLURM_JOB_NUM_NODES nor'
                ' SLURM_NNODES is set. Please create an issue on GitHub with the output'
                ' of "sbatch --version" on this cluster.')

    def agent_launch_command(self, agent_cmd: List[str], nnodes: int) -> List[str]:
        """Return a command for launching one agent on each node.

        Args:
            agent_cmd: A command that will start the agent.
        """
        # TODO: On the latest Slurm, there's a special command for this that we should
        # use if we have that, --external-launcher. Poorly documented though, so will
        # require some experimentation.

        # On SLURM <= 23-02, the number of tasks is inherited by srun from sbatch rather
        # than calculated anew from --nodes and --ntasks-per-node, so we specify it
        # explicitly to avoid getting an agent per logical cpu rather than per node.
        srun_cmd = [
                'srun', f'--nodes={nnodes}', f'--ntasks={nnodes}',
                '--ntasks-per-node=1'
                ]

        if self.quirks.overlap:
            srun_cmd.append('--overlap')

        return srun_cmd + agent_cmd

    def _slurm_version(self) -> Tuple[int, int]:
        """Obtains current version of SLURM from srun -v.

        This returns only the first two numbers, hopefully there won't be any changes in
        behaviour within a release series.
        """
        proc = subprocess.run(
                ['srun', '--version'], check=True, capture_output=True, text=True,
                encoding='utf-8'
                )

        output = proc.stdout.strip().split()
        if len(output) < 2:
            raise RuntimeError(
                    f'Unexpected srun version output "{output}". MUSCLE3 does not know'
                    ' how to run on this version of SLURM. Please file an issue on'
                    ' GitHub.')

        version_str = output[1]
        version = version_str.split('.')
        if len(version) < 2:
            _logger.error(f'srun produced unexpected version {version_str}')
            raise RuntimeError(
                    f'Unexpected srun version output "{output}". MUSCLE3 does not know'
                    ' how to run on this version of SLURM. Please file an issue on'
                    ' GitHub.')
        return int(version[0]), int(version[1])


slurm_: Optional[SlurmInfo] = None


def slurm() -> SlurmInfo:
    """SlurmInfo singleton"""
    global slurm_

    if slurm_ is None:
        slurm_ = SlurmInfo()

    return slurm_
