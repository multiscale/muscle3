#include "libmuscle/util.hpp"

#include <chrono>
#include <cmath>
#include <fcntl.h>
#include <stdexcept>
#include <string>
#include <sys/stat.h>
#include <sys/stat.h>
#include <thread>
#include <unistd.h>
#include <limits.h>


using std::chrono::duration;
using std::chrono::duration_cast;
using std::chrono::seconds;
using std::chrono::steady_clock;


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

int throw_on_error(int ret_val) {
    if (ret_val == -1)
        throw std::runtime_error("An unexpected error occurred");
    return ret_val;
}

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

double time_monotonic() {
    steady_clock::duration now = steady_clock::now().time_since_epoch();
    return duration_cast<duration<double>>(now).count();
}

Retrier::Retrier(double timeout, double base_delay)
    : base_delay_(base_delay)
    , timeout_(timeout)
    , start_(0.0)
    , tries_(0)
{}

void Retrier::sleep() {
    double delay = 0;
    if (tries_ > 0)
        delay = base_delay_ * std::pow(factor_, tries_ - 1);

    std::this_thread::sleep_for(duration<double>(delay));
    ++tries_;
}

bool Retrier::should_give_up() {
    if (tries_ == 0)
        start_ = time_monotonic();

    double elapsed = time_monotonic() - start_;
    return elapsed >= timeout_;
}

const double Retrier::default_base_delay_ = 0.5;
const double Retrier::default_timeout_ = 30.0;
const double Retrier::factor_ = std::pow(2.0, 1.0 / 3.0);
int get_process_id() {
    return ::getpid();
}

std::string get_hostname() {
    char hostname[HOST_NAME_MAX+1];
    if (::gethostname(hostname, HOST_NAME_MAX+1) != 0)
        throw std::runtime_error("Could not get hostname");
    return std::string(hostname);
}

} }

