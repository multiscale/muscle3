from ymmsl import load
from integration_test.test_all import macro, micro, NUM_MICROS
from libmuscle.runner import run_simulation


def test_nested(log_file_in_tmpdir, tmp_path):
    yaml_text = (
            'ymmsl_version: v0.2\n'
            'description: Simple nested test configuration\n'
            'models:\n'
            '  outer:\n'
            '    description: Model containing a submodel\n'
            '    components:\n'
            '      macro:\n'
            '        ports:\n'
            '          o_i: out\n'
            '          s: in\n'
            '        description: Macro model\n'
            '        implementation: macro_impl\n'
            '      sim:\n'
            '        ports:\n'
            '          f_init: in\n'
            '          o_f: out\n'
            '        description: Simulates stuff\n'
            '        implementation: inner\n'
            '    conduits:\n'
            '      macro.out: sim.in\n'
            '      sim.out: macro.in\n'
            '  inner:\n'
            '    ports:\n'
            '      f_init: in\n'
            '      o_f: out\n'
            '    description: Nested simulation model\n'
            '    components:\n'
            '      simulate:\n'
            '        ports:\n'
            '          f_init: in\n'
            '          o_f: out\n'
            '        description: Micro model\n'
            '        implementation: micro_impl\n'
            '    conduits:\n'
            '      in: simulate.in\n'
            '      simulate.out: out\n'
            'settings:\n'
            '  muscle_local_log_level: DEBUG\n'
            '  test1: 13\n'
            '  test2: 13.3\n'
            '  test3: testing\n'
            '  test4: true\n'
            '  test5: [2.3, 5.6]\n'
            '  test6:\n'
            '  - [1.0, 2.0]\n'
            '  - [3.0, 1.0]\n'
            )

    configuration = load(yaml_text)
    configuration.models['outer'].components['sim'].multiplicity = [NUM_MICROS]

    implementations = {'macro_impl': macro, 'micro_impl': micro}
    run_simulation(configuration, implementations)
