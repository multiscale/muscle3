import sys

YMMSL_CONFIG = f"""
ymmsl_version: v0.2
description: MUSCLE3 built-in timeline bridge implementations
programs:
  unidirectional_bridge:
    description: |
      MUSCLE3 built-in unidirectional timeline bridge
    executable: {sys.executable}
    args: -m muscle3.actors.bridges.unidirectional_bridge
"""
