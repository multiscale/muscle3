from ymmsl import Experiment

from libmuscle.configuration import Configuration


def config_for_experiment(experiment: Experiment) -> Configuration:
    """Creates a Configuration from a yMMSL Experiment.

    Args:
        experiment: The experiment to create a Configuration for.
    """
    configuration = Configuration()
    if experiment.parameter_values is not None:
        for setting in experiment.parameter_values:
            configuration[setting.parameter] = setting.value
    return configuration