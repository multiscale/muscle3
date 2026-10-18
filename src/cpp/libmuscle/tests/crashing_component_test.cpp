/* This is a part of the integration test suite, and is run from a Python
 * test in /integration_test. It is not a unit test.
 */
#include <iostream>


/** A component that crashes, for testing.
 */
int main(int argc, char * argv[]) {
    int * p = nullptr;
    std:: cout << *p;
    return 1;
}

