#pragma once

#include <gtest/gtest.h>

#include <memory>
#include <unordered_map>
#include <string>
#include <vector>

// Note: using POSIX for filesystem calls
// Could be upgraded to std::filesystem when targeting C++17 or later
#include <cstdlib>
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <string.h>
#include <unistd.h>
#include <ftw.h>

#include <libmuscle/port.hpp>
#include <libmuscle/tests/mocks/mock_port_manager.hpp>
#include <ymmsl/ymmsl.hpp>


// callback for nftw() to delete all contents of a folder
int _nftw_rm_callback(
        const char *fpath, const struct stat *sb, int tflag, struct FTW *ftwbuf) {
    if (tflag == FTW_DP) {
        std::cerr << "DEBUG: removing dir " << fpath << std::endl;
        return rmdir(fpath);
    }
    if (tflag == FTW_F) {
        std::cerr << "DEBUG: removing file " << fpath << std::endl;
        return unlink(fpath);
    }
    std::cerr << "DEBUG: unknown file type " << fpath << std::endl;
    return -1;
}

struct TempDirFixture {
    TempDirFixture() {
            char tmpname[] = "/tmp/muscle3_test.XXXXXX";
            if (mkdtemp(tmpname) == nullptr) {
                throw std::runtime_error(strerror(errno));
            }
            temp_dir_ = tmpname;
            std::cerr << "DEBUG: using temp dir " << temp_dir_ << std::endl;
    }

    ~TempDirFixture() {
            // simulate rm -rf `temp_dir_` using a file-tree-walk
            if (nftw(temp_dir_.c_str(), _nftw_rm_callback, 3, FTW_DEPTH) < 0) {
                std::cerr << "ERROR: Could not remove temp dir at " << temp_dir_ << std::endl;
                std::cerr << "ERROR: " << strerror(errno) << std::endl;
            }
    }

    std::string temp_dir_;
};


struct ConnectedPortManagerFixture {
    public:
        typedef ::libmuscle::_MUSCLE_IMPL_NS::Port Port;
        typedef ::ymmsl::Operator Operator;

        std::unordered_map<ymmsl::Operator, std::vector<std::string>> declared_ports_;

        std::unordered_map<
            std::string, std::unique_ptr<Port>> mock_ports_;

        ::libmuscle::_MUSCLE_IMPL_NS::MockPortManager connected_port_manager_;

        ConnectedPortManagerFixture()
            : declared_ports_{
                {Operator::F_INIT, {"in", "not_connected"}},
                {Operator::O_I, {"out_v", "out_r"}},
                {Operator::S, {"in_v", "in_r", "not_connected_v"}},
                {Operator::O_F, {"out"}}}
        {
            // Can't do this in the initializer list because you can't move from one,
            // and you can't copy a unique_ptr.
            mock_ports_["in"] = std::make_unique<Port>("in", Operator::F_INIT, false, true, 0, std::vector<int>());
            mock_ports_["not_connected"] = std::make_unique<Port>("not_connected", Operator::F_INIT, false, false, 0, std::vector<int>());
            mock_ports_["out_v"] = std::make_unique<Port>("out_v", Operator::O_I, true, true, 0, std::vector<int>({13}));
            mock_ports_["out_r"] = std::make_unique<Port>("out_r", Operator::O_I, true, true, 0, std::vector<int>());
            mock_ports_["in_v"] = std::make_unique<Port>("in_v", Operator::S, true, true, 0, std::vector<int>({13}));
            mock_ports_["in_r"] = std::make_unique<Port>("in_r", Operator::S, true, true, 0, std::vector<int>());
            mock_ports_["not_connected_v"] = std::make_unique<Port>("not_connected_v", Operator::S, true, false, 0, std::vector<int>());
            mock_ports_["out"] = std::make_unique<Port>("out", Operator::O_F, false, true, 0, std::vector<int>());

            connected_port_manager_.get_port.side_effect = [this]
                (std::string const & name) -> Port &  {
                    return *mock_ports_.at(name);
                };
            connected_port_manager_.list_ports.return_value = declared_ports_;
            connected_port_manager_.port_exists.side_effect = [this]
                (std::string const & name) -> bool {
                    return mock_ports_.count(name) != 0;
                };
        }
};

