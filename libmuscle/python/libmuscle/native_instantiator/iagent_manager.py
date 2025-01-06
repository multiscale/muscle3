from typing import List, Tuple

from libmuscle.planner.resources import OnNodeResources


class IAgentManager:
    """Interface for Agent Managers.

    Only implemented by AgentManager, and only exists to avoid a circular dependency
    between AgentManager, MAPServer, and MAPRequestHandler. Ugh.
    """
    def report_resources(self, resources: OnNodeResources) -> None:
        """Report resources found on a node.

        Called by MAPServer from a server thread.

        Args:
            node_name: Id of the node these resources are on
            resources: Dict mapping resource type to resource ids
        """
        raise NotImplementedError()

    def report_result(self, names_exit_codes: List[Tuple[str, int]]) -> None:
        """Report results of finished processes.

        Called by MAPServer from a server thread.

        Args:
            names_exit_codes: A list of names and exit codes of finished processes.
        """
        raise NotImplementedError()
