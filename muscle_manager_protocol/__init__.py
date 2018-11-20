import os
import sys


# The gRPC generated code contains an absolute import. So either it
# needs to be in the top-level directory, or the user needs to modify
# their PYTHONPATH environment variable, or we add it to the path here.
sys.path.append(os.path.dirname(os.path.expanduser(__file__)))
