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

#include <libmuscle/message.hpp>
#include <libmuscle/port.hpp>
#include <libmuscle/timeline_manager.hpp>
#include <libmuscle/tests/mocks/mock_port_manager.hpp>
#include <ymmsl/ymmsl.hpp>


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

// These need to be in the namespace to use argument-dependent lookup (ADL).
// Several mocks (e.g. MockCommunicator's receive_message) need these to be
// comparable, whether or not a given test actually compares them.

bool operator!=(DataConstRef const &, DataConstRef const &);

bool operator==(DataConstRef const & lhs, DataConstRef const & rhs) {
    if (lhs.is_a_dict()) {
        if (!rhs.is_a_dict()) return false;
        if (lhs.size() != rhs.size()) return false;
        try {
            for (std::size_t i = 0u; i < lhs.size(); ++i)
                if (lhs.value(i) != rhs[lhs.key(i)]) return false;
        }
        catch (std::domain_error const &) {
            return false;
        }
        return true;
    }

    if (lhs.is_a_list()) {
        if (!rhs.is_a_list()) return false;
        if (lhs.size() != rhs.size()) return false;
        for (std::size_t i = 0u; i < lhs.size(); ++i)
            if (lhs[i] != rhs[i]) return false;
        return true;
    }

    if (lhs.is_a<::ymmsl::Settings>()) {
        if (!rhs.is_a<::ymmsl::Settings>()) return false;
        return lhs.as<::ymmsl::Settings>() == rhs.as<::ymmsl::Settings>();
    }

    if (lhs.is_a<bool>()) return rhs.is_a<bool>() && lhs.as<bool>() == rhs.as<bool>();

    if (lhs.is_a<double>())
        return rhs.is_a<double>() && lhs.as<double>() == rhs.as<double>();

    if (lhs.is_a<std::string>()) {
        if (!rhs.is_a<std::string>()) return false;
        return lhs.as<std::string>() == rhs.as<std::string>();
    }

    if (lhs.is_nil()) return rhs.is_nil();

    throw std::runtime_error("Not implemented");
}

bool operator!=(DataConstRef const & lhs, DataConstRef const & rhs) {
    return !(lhs == rhs);
}

bool operator==(Message const & lhs, Message const & rhs) {
    if (lhs.timestamp_ != rhs.timestamp_) return false;
    if (lhs.next_timestamp_ != rhs.next_timestamp_) return false;
    if (lhs.data_ != rhs.data_) return false;
    if (lhs.settings_ != rhs.settings_) return false;
    return true;
}

} }


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
        typedef ::ymmsl::Timeline Timeline;
        using PortReferences = std::vector<std::reference_wrapper<const Port>>;

        std::unordered_map<ymmsl::Operator, std::vector<std::string>> declared_ports_;

        std::unordered_map<
            std::string, std::unique_ptr<Port>> mock_ports_;
        Port muscle_settings_in_;

        ::libmuscle::_MUSCLE_IMPL_NS::MockPortManager connected_port_manager_;

        ConnectedPortManagerFixture()
            : declared_ports_{
                {Operator::F_INIT, {"in", "not_connected"}},
                {Operator::O_I, {"out_v", "out_r"}},
                {Operator::S, {"in_v", "in_r", "not_connected_v"}},
                {Operator::O_F, {"out"}}}
            , muscle_settings_in_{"muscle_settings_in", Operator::F_INIT, Timeline(""), false, true, 0, {}}
        {
            // Can't do this in the initializer list because you can't move from one,
            // and you can't copy a unique_ptr.
            mock_ports_["in"] = std::make_unique<Port>("in", Operator::F_INIT, Timeline(""), false, true, 0, std::vector<int>());
            mock_ports_["not_connected"] = std::make_unique<Port>("not_connected", Operator::F_INIT, Timeline(""), false, false, 0, std::vector<int>());
            mock_ports_["out_v"] = std::make_unique<Port>("out_v", Operator::O_I, Timeline(""), true, true, 0, std::vector<int>({13}));
            mock_ports_["out_r"] = std::make_unique<Port>("out_r", Operator::O_I, Timeline(""), true, true, 0, std::vector<int>());
            mock_ports_["in_v"] = std::make_unique<Port>("in_v", Operator::S, Timeline(""), true, true, 0, std::vector<int>({13}));
            mock_ports_["in_r"] = std::make_unique<Port>("in_r", Operator::S, Timeline(""), true, true, 0, std::vector<int>());
            mock_ports_["not_connected_v"] = std::make_unique<Port>("not_connected_v", Operator::S, Timeline(""), true, false, 0, std::vector<int>());
            mock_ports_["out"] = std::make_unique<Port>("out", Operator::O_F, Timeline(""), false, true, 0, std::vector<int>());

            connected_port_manager_.muscle_settings_in.return_value = &muscle_settings_in_;
            connected_port_manager_.get_port.side_effect = [this]
                (std::string const & name) -> Port &  {
                    if (name == "muscle_settings_in")
                        return muscle_settings_in_;
                    return *mock_ports_.at(name);
                };
            connected_port_manager_.list_ports.return_value = declared_ports_;
            connected_port_manager_.port_exists.side_effect = [this]
                (std::string const & name) -> bool {
                    return mock_ports_.count(name) != 0;
                };
            connected_port_manager_.has_f_init_connections.return_value = true;
            connected_port_manager_.get_connected_ports.side_effect = [&] (
                    ::ymmsl::Operator op, ::libmuscle::_MUSCLE_IMPL_NS::Optional<::ymmsl::Timeline> tl
                    ) -> PortReferences {
                assert(!tl.is_set());  // This mock doesn't support filtering on timeline
                PortReferences result;
                for (auto & port_name : declared_ports_.at(op)) {
                    Port & port = *mock_ports_.at(port_name);
                    if (port.is_connected())
                        result.push_back(port);
                }
                if (op == Operator::F_INIT && connected_port_manager_.settings_in_connected())
                    result.push_back(muscle_settings_in_);
                return result;
            };
        }
};


struct TimelineStateFixture {
    public:
        typedef ::libmuscle::_MUSCLE_IMPL_NS::TimelineState TimelineState;
        typedef ::libmuscle::_MUSCLE_IMPL_NS::PortAndSlot PortAndSlot;
        typedef ::libmuscle::_MUSCLE_IMPL_NS::IterationCount IterationCount;
        typedef ::libmuscle::_MUSCLE_IMPL_NS::Optional<int> OptionalSlot;

        TimelineState timeline_state_;

        TimelineStateFixture() {
            timeline_state_.iteration = IterationCount({1});
            timeline_state_.send_participated = {};
            timeline_state_.receive_participated = {
                    PortAndSlot("in", OptionalSlot())};
            timeline_state_.subtimeline_states = {};
        }
};

