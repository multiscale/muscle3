#include "libmuscle/util.hpp"

#include <fcntl.h>
#include <string>
#include <sys/stat.h>


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

std::string extract_log_file_location(
        int argc, char const * const argv[], std::string const & filename
) {
    std::string prefix("--muscle-log-file");
    std::string given_path;
    for (int i = 1; i < argc; ++i) {
        std::string args(argv[i]);
        if (args.rfind(prefix, 0u) == 0u)
            given_path = args.substr(prefix.size(), std::string::npos);
    }

    if (given_path.empty())
        return given_path;

    struct stat statbuf;
    int err = stat(given_path.c_str(), &statbuf);
    if (err != 0) return std::string();

    if (S_ISDIR(statbuf.st_mode))
        return given_path + "/" + filename;
    return given_path;
}


Error::Error() : type_(0), message_() {}

Error::Error(std::exception const & exc) {
    type_ = 0;
    if (dynamic_cast<std::logic_error const *>(&exc)) type_ = 1;
    if (dynamic_cast<std::runtime_error const *>(&exc)) type_ = 2;
    message_ = exc.what();

    if (type_ == 0) {
        type_ = 1;
        message_ = std::string("Invalid exception type ") + typeid(exc).name() +
            " passed to Error, original error was: " + message_;
    }
}

#ifdef MUSCLE_ENABLE_MPI
void Error::bcast(MPI_Comm & comm, int root) const {
    MPI_Bcast(const_cast<int *>(&type_), 1, MPI_INT, root, comm);
}
#endif

bool Error::is_error() const {
    return type_ != 0;
}

std::string const & Error::get_message() const {
    return message_;
}

void Error::throw_if_error() const {
    if (type_ == 0) return;
    if (type_ == 1) throw std::logic_error(message_);
    if (type_ == 2) throw std::runtime_error(message_);
}

} }

