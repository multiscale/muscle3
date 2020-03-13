#include <cmdlineargs.hpp>


namespace echolib { namespace impl {

CmdLineArgs::CmdLineArgs(int count)
        : ptrs_(count, nullptr)
        , args_(count, "")
    {}

void CmdLineArgs::set_arg(int i, std::string const & arg) {
    args_[i] = arg;
    ptrs_[i] = args_[i].c_str();
}

int CmdLineArgs::argc() const {
    return ptrs_.size();
}

char const * const * CmdLineArgs::argv() const {
    return ptrs_.data();
}

} }

