from collections import OrderedDict

from ymmsl import Reference, Settings

from muscle_manager.muscle_manager import config_for_settings


def test_config_from_experiment():
    settings = Settings(OrderedDict([
            ('x', 1.1),
            ('y', 3.0),
            ('alpha', 2),
            ('interpolation', 'linear'),
            ('diffusion', [[1.1, 0.9], [0.9, 1.1]])]))

    config = config_for_settings(settings)

    assert config['x'] == 1.1
    assert config['y'] == 3.0
    assert config['alpha'] == 2
    assert config['interpolation'] == 'linear'
    assert config['diffusion'] == [[1.1, 0.9], [0.9, 1.1]]
    assert len(config) == 5
    assert 'z' not in config
