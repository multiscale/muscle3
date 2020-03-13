#pragma once

#include <string>
#include <vector>


namespace libmuscle { namespace impl { namespace bindings {

// Simple helper class for passing command line args from Fortran to C++.
class CmdLineArgs {
    public:
        CmdLineArgs(int count);

        void set_arg(int i, std::string const & arg);

        int argc() const;

        char const * const * argv() const;

    private:
        std::vector<char const *> ptrs_;
        std::vector<std::string> args_;
};

} } }

