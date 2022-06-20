#include "libmuscle/util.hpp"

#include <fcntl.h>
#include <string>
#include <sys/stat.h>


namespace libmuscle { namespace impl {

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

} }

