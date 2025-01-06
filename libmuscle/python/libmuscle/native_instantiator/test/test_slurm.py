from libmuscle.native_instantiator.slurm import (
        parse_slurm_nodelist, parse_slurm_nodes_cores)

import pytest


NRES_ = [
        # from various bits of SLURM documentation
        (
            'linux[00-17]', [
                'linux00', 'linux01', 'linux02', 'linux03', 'linux04', 'linux05',
                'linux06', 'linux07', 'linux08', 'linux09', 'linux10', 'linux11',
                'linux12', 'linux13', 'linux14', 'linux15', 'linux16', 'linux17']),
        (
            'lx[10-20]', [
                'lx10', 'lx11', 'lx12', 'lx13', 'lx14', 'lx15', 'lx16', 'lx17', 'lx18',
                'lx19', 'lx20']),
        ('tux[2,1-2]', ['tux2', 'tux1', 'tux2']),
        ('tux[1-2,2]', ['tux1', 'tux2', 'tux2']),
        ('tux[1-3]', ['tux1', 'tux2', 'tux3']),
        (
            'linux[0-64,128]', [
                'linux0', 'linux1', 'linux2', 'linux3', 'linux4', 'linux5', 'linux6',
                'linux7', 'linux8', 'linux9', 'linux10', 'linux11', 'linux12',
                'linux13', 'linux14', 'linux15', 'linux16', 'linux17', 'linux18',
                'linux19', 'linux20', 'linux21', 'linux22', 'linux23', 'linux24',
                'linux25', 'linux26', 'linux27', 'linux28', 'linux29', 'linux30',
                'linux31', 'linux32', 'linux33', 'linux34', 'linux35', 'linux36',
                'linux37', 'linux38', 'linux39', 'linux40', 'linux41', 'linux42',
                'linux43', 'linux44', 'linux45', 'linux46', 'linux47', 'linux48',
                'linux49', 'linux50', 'linux51', 'linux52', 'linux53', 'linux54',
                'linux55', 'linux56', 'linux57', 'linux58', 'linux59', 'linux60',
                'linux61', 'linux62', 'linux63', 'linux64', 'linux128']),
        ('alpha,beta,gamma', ['alpha', 'beta', 'gamma']),
        ('lx[15,18,32-33]', ['lx15', 'lx18', 'lx32', 'lx33']),
        ('linux[0000-1023]', [f'linux{i:04}' for i in range(1024)]),
        (
            'rack[0-63]_blade[0-41]', [
                f'rack{i}_blade{j}' for i in range(64) for j in range(42)]),
        # my additions
        ('linux', ['linux']),
        ('linux[0]', ['linux0']),
        ('linux[0,1]', ['linux0', 'linux1']),
        ('linux[0-2]', ['linux0', 'linux1', 'linux2']),
        (
            'rack[00-12,14]_blade[0-2],alpha,tux[1-3,6]', (
                [f'rack{i:02}_blade{j}' for i in range(13) for j in range(3)] + [
                    'rack14_blade0', 'rack14_blade1', 'rack14_blade2', 'alpha',
                    'tux1', 'tux2', 'tux3', 'tux6'])),
        ('node-0', ['node-0']),
        ('node-[0-3]', ['node-0', 'node-1', 'node-2', 'node-3']),
        ]


@pytest.mark.parametrize('nre,expected', NRES_)
def test_parse_slurm_nodelist(nre, expected):
    assert parse_slurm_nodelist(nre) == expected


NCES_ = [
        ('8', [8]),
        ('8(x2)', [8, 8]),
        ('16,24', [16, 24]),
        ('16,24(x3)', [16, 24, 24, 24]),
        ('1(x1),2', [1, 2]),
        ('72(x2),36', [72, 72, 36])
        ]


@pytest.mark.parametrize('nce,expected', NCES_)
def test_parse_slurm_nodes_cores(nce, expected):
    assert parse_slurm_nodes_cores(nce) == expected
