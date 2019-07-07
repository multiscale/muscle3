/* This is a part of the integration test suite, and is run from a Python
 * test in /integration_test. It is not a unit test.
 */
#include <libmuscle/mmp_client.hpp>

using libmuscle::MMPClient;


int main(int argc, char *argv[]) {
    auto client = MMPClient("localhost:9000");

    return 0;
}

