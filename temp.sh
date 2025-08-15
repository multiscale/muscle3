# Because I hate writing this over and over again
# Note to the reviewer: delete this script per your discretion

echo "=== Building C++ tests ==="
make cpp_tests \
    1>build_cpp_tests_out.log \
    2>build_cpp_tests_err.log
