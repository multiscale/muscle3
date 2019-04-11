#pragma once

/** A simple class to test the build system with.
 */
class Tooling {
public:
    /** Constructor
     */
    Tooling();

    /** An accessor for test_variable.
     */
    int get_test_variable() const;

private:
    /** A private member variable.
     */
    int test_variable_;
};

