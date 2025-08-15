#!/bin/bash

# Because I hate writing this over and over again
# Note to the reviewer: delete this script per your discretion

echo "=== Building C++ tests ==="
make cpp_tests \
    > >(tee build_cpp_tests_out.log) \
    2> >(tee build_cpp_tests_err.log >&2)
