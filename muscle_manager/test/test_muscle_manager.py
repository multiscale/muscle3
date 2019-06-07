from ymmsl import Experiment, Reference, Setting

from muscle_manager.muscle_manager import config_for_experiment


def test_config_from_experiment():
    parameters = [
            Setting('x', 1.1),
            Setting('y', 3.0),
            Setting('alpha', 2),
            Setting('interpolation', 'linear'),
            Setting('diffusion', [[1.1, 0.9], [0.9, 1.1]])]
    experiment = Experiment('test_model', parameters)

    config = config_for_experiment(experiment)

    assert config['x'] == 1.1
    assert config['y'] == 3.0
    assert config['alpha'] == 2
    assert config['interpolation'] == 'linear'
    assert config['diffusion'] == [[1.1, 0.9], [0.9, 1.1]]
    assert len(config) == 5
    assert 'z' not in config
