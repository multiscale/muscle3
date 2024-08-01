// Inject mocks
#define LIBMUSCLE_MOCK_API_GUARD <mocks/mock_api_guard.hpp>
#define LIBMUSCLE_MOCK_COMMUNICATOR <mocks/mock_communicator.hpp>
#define LIBMUSCLE_MOCK_LOGGER <mocks/mock_logger.hpp>
#define LIBMUSCLE_MOCK_MMP_CLIENT <mocks/mock_mmp_client.hpp>
#define LIBMUSCLE_MOCK_PORT_MANAGER <mocks/mock_port_manager.hpp>
#define LIBMUSCLE_MOCK_PROFILER <mocks/mock_profiler.hpp>
#define LIBMUSCLE_MOCK_SETTINGS_MANAGER <mocks/mock_settings_manager.hpp>
#define LIBMUSCLE_MOCK_SNAPSHOT_MANAGER <mocks/mock_snapshot_manager.hpp>
#define LIBMUSCLE_MOCK_TRIGGER_MANAGER <mocks/mock_trigger_manager.hpp>

// into the real implementation to test.
#include <ymmsl/ymmsl.hpp>

#include <libmuscle/close_port.cpp>
#include <libmuscle/data.cpp>
#include <libmuscle/instance.cpp>
#include <libmuscle/logging.cpp>
#include <libmuscle/mcp/data_pack.cpp>
#include <libmuscle/message.cpp>
#include <libmuscle/port.cpp>
#include <libmuscle/timestamp.cpp>

// Test code dependencies
#include <cstdlib>
#include <memory>
#include <stdexcept>
#include <typeinfo>

#include <gtest/gtest.h>

#include <libmuscle/instance.hpp>
#include <libmuscle/namespace.hpp>
#include <libmuscle/settings_manager.hpp>
#include <libmuscle/tests/fixtures.hpp>
#include <mocks/mock_api_guard.hpp>
#include <mocks/mock_communicator.hpp>
#include <mocks/mock_logger.hpp>
#include <mocks/mock_mmp_client.hpp>
#include <mocks/mock_port_manager.hpp>
#include <mocks/mock_profiler.hpp>
#include <mocks/mock_settings_manager.hpp>
#include <mocks/mock_snapshot_manager.hpp>
#include <mocks/mock_trigger_manager.hpp>


using libmuscle::_MUSCLE_IMPL_NS::APIGuard;
using libmuscle::_MUSCLE_IMPL_NS::ClosePort;
using libmuscle::_MUSCLE_IMPL_NS::Data;
using libmuscle::_MUSCLE_IMPL_NS::DataConstRef;
using libmuscle::_MUSCLE_IMPL_NS::Instance;
using libmuscle::_MUSCLE_IMPL_NS::InstanceFlags;
using libmuscle::_MUSCLE_IMPL_NS::Message;
using libmuscle::_MUSCLE_IMPL_NS::MockCommunicator;
using libmuscle::_MUSCLE_IMPL_NS::MockLogger;
using libmuscle::_MUSCLE_IMPL_NS::MockMMPClient;
using libmuscle::_MUSCLE_IMPL_NS::MockPortManager;
using libmuscle::_MUSCLE_IMPL_NS::MockProfiler;
using libmuscle::_MUSCLE_IMPL_NS::MockSettingsManager;
using libmuscle::_MUSCLE_IMPL_NS::MockSnapshotManager;
using libmuscle::_MUSCLE_IMPL_NS::MockTriggerManager;
using libmuscle::_MUSCLE_IMPL_NS::Optional;
using libmuscle::_MUSCLE_IMPL_NS::PeerInfo;
using libmuscle::_MUSCLE_IMPL_NS::Port;
using libmuscle::_MUSCLE_IMPL_NS::PortsDescription;

using ymmsl::Operator;
using ymmsl::Reference;
using ymmsl::Settings;
using ymmsl::SettingValue;


int main(int argc, char *argv[]) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

// These need to be in the namespace to use argument-dependent lookup (ADL)

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

    if (lhs.is_a<Settings>()) {
        if (!rhs.is_a<Settings>()) return false;
        return lhs.as<Settings>() == rhs.as<Settings>();
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

bool operator==(PeerInfo const & lhs, PeerInfo const & rhs) {
    if (lhs.kernel_ != rhs.kernel_) return false;
    if (lhs.index_ != rhs.index_) return false;
    if (lhs.incoming_ports_ != rhs.incoming_ports_) return false;
    if (lhs.outgoing_ports_ != rhs.outgoing_ports_) return false;
    if (lhs.peers_ != rhs.peers_) return false;
    if (lhs.peer_dims_ != rhs.peer_dims_) return false;
    if (lhs.peer_locations_ != rhs.peer_locations_) return false;
    return true;
}

bool operator==(Message const & lhs, Message const & rhs) {
    if (lhs.timestamp_ != rhs.timestamp_) return false;
    if (lhs.next_timestamp_ != rhs.next_timestamp_) return false;
    if (lhs.data_ != rhs.data_) return false;
    if (lhs.settings_ != rhs.settings_) return false;
    return true;
}

} }


struct libmuscle_instance_base : ::testing::Test, ConnectedPortManagerFixture {
    RESET_MOCKS(
            MockCommunicator, MockLogger, MockMMPClient, MockPortManager, MockProfiler,
            MockSettingsManager, MockSnapshotManager, MockTriggerManager);

    char const * test_argv_[5];
    int test_argc_;

    char const * instance_argv_[2];
    int instance_argc_;

    libmuscle_instance_base()
        : test_argc_(sizeof(test_argv_) / sizeof(test_argv_[0]))
        , instance_argc_(sizeof(instance_argv_) / sizeof(instance_argv_[0]))
    {
        // manager_location_argv
        test_argv_[0] = "--test";
        test_argv_[1] = "--muscle-manager=tcp:localhost:9001";
        test_argv_[2] = "--bla";

        // instance_argv
        instance_argv_[0] = "distraction";
        instance_argv_[1] = "--muscle-instance=component";
        test_argv_[3] = instance_argv_[0];
        test_argv_[4] = instance_argv_[1];

        auto & mock_comm = MockCommunicator::return_value;
        mock_comm.get_locations.return_value = std::vector<std::string>(
                {"tcp:test1,test2", "tcp:test3"});

        auto & mock_port_manager = MockPortManager::return_value;
        mock_port_manager.settings_in_connected.return_value = false;
        mock_port_manager.list_ports.return_value = PortsDescription();

        // no checkpoints by default
        MockTriggerManager::return_value.has_checkpoints.return_value = false;
        MockSnapshotManager::return_value.prepare_resume.return_value = Optional<double>();
        MockSnapshotManager::return_value.resume_overlay.return_value = Settings();

        // not resuming by default (no_resume_snapshot_manager)
        auto & snapshot_manager = MockSnapshotManager::return_value;
        snapshot_manager.resuming_from_intermediate.return_value = false;
        snapshot_manager.resuming_from_final.return_value = false;
        snapshot_manager.resume_overlay.return_value = Settings();

        // no settings by default
        MockSettingsManager::return_value.list_settings.return_value = (
                std::vector<std::string>());

        MockSettingsManager::return_value.get_setting.side_effect = [](
                Reference const &, Reference const &) -> SettingValue {
            throw std::out_of_range("No settings set in mock, unset or replace side_effect");
        };
    }
};


struct ConnectedPortManagerHelper : libmuscle_instance_base {
    // Sets the connected port manager mock as the default port manager before the
    // instance is made in libmuscle_instance. This is getting to be a bit too much
    // inheritance, but you get what you get I guess.
    ConnectedPortManagerHelper() {
        MockPortManager::return_value = connected_port_manager_;
    }
};


struct libmuscle_instance : ConnectedPortManagerHelper {
    Instance instance_;

    MockLogger & logger_;
    MockMMPClient & mmp_client_;
    MockProfiler & profiler_;
    MockPortManager & port_manager_;
    MockCommunicator & communicator_;
    MockSettingsManager & settings_manager_;
    MockSnapshotManager & snapshot_manager_;
    MockTriggerManager & trigger_manager_;

    libmuscle_instance()
        : instance_(test_argc_, test_argv_, declared_ports_)
        , logger_(*instance_.impl_()->logger_)
        , mmp_client_(*instance_.impl_()->manager_)
        , profiler_(*instance_.impl_()->profiler_)
        , port_manager_(*instance_.impl_()->port_manager_)
        , communicator_(*instance_.impl_()->communicator_)
        , settings_manager_(instance_.impl_()->settings_manager_)
        , snapshot_manager_(*instance_.impl_()->snapshot_manager_)
        , trigger_manager_(*instance_.impl_()->trigger_manager_)
    {}
};


struct libmuscle_instance_dont_apply_overlay : ConnectedPortManagerHelper {
    Instance instance_dont_apply_overlay_;

    MockLogger & logger_;
    MockMMPClient & mmp_client_;
    MockProfiler & profiler_;
    MockPortManager & port_manager_;
    MockCommunicator & communicator_;
    MockSettingsManager & settings_manager_;
    MockSnapshotManager & snapshot_manager_;
    MockTriggerManager & trigger_manager_;

    libmuscle_instance_dont_apply_overlay()
        : instance_dont_apply_overlay_(
                test_argc_, test_argv_, declared_ports_,
                InstanceFlags::DONT_APPLY_OVERLAY)
        , logger_(*instance_dont_apply_overlay_.impl_()->logger_)
        , mmp_client_(*instance_dont_apply_overlay_.impl_()->manager_)
        , profiler_(*instance_dont_apply_overlay_.impl_()->profiler_)
        , port_manager_(*instance_dont_apply_overlay_.impl_()->port_manager_)
        , communicator_(*instance_dont_apply_overlay_.impl_()->communicator_)
        , settings_manager_(instance_dont_apply_overlay_.impl_()->settings_manager_)
        , snapshot_manager_(*instance_dont_apply_overlay_.impl_()->snapshot_manager_)
        , trigger_manager_(*instance_dont_apply_overlay_.impl_()->trigger_manager_)
    {}
};


TEST_F(libmuscle_instance_base, create_instance_manager_location_default) {
    Instance instance(instance_argc_, instance_argv_, declared_ports_);

    ASSERT_TRUE(
            instance.impl_()->manager_->constructor.called_once_with(
                Reference("component"), "tcp:localhost:9000"));
}

TEST_F(libmuscle_instance_base, create_instance_manager_location_argv) {
    Instance instance(test_argc_, test_argv_, declared_ports_);

    ASSERT_TRUE(
            instance.impl_()->manager_->constructor.called_once_with(
                Reference("component"), "tcp:localhost:9001"));
}

TEST_F(libmuscle_instance_base, create_instance_manager_location_envvar) {
    setenv("MUSCLE_MANAGER", "tcp:localhost:9002", 1);
    setenv("MUSCLE_INSTANCE", "component[13]", 1);

    Instance instance(0, nullptr, declared_ports_);

    ASSERT_TRUE(
            instance.impl_()->manager_->constructor.called_once_with(
                Reference("component[13]"), "tcp:localhost:9002"));
}

TEST_F(libmuscle_instance_base, create_instance_registration) {
    Instance instance(test_argc_, test_argv_, declared_ports_);

    auto const & impl = *instance.impl_();
    auto const & locations = impl.communicator_->get_locations.return_value.get();

    ASSERT_TRUE(impl.manager_->register_instance.called_once());
    ASSERT_EQ(impl.manager_->register_instance.call_arg<0>(), locations);

    auto const & port_desc = impl.manager_->register_instance.call_arg<1>();

    auto check = [&port_desc](std::string const & name, ::Operator op) {
        for (auto const & p : port_desc) {
            if (p.name == name) {
                ASSERT_EQ(p.oper, op);
                break;
            }
        }
    };

    ASSERT_EQ(port_desc.size(), 8u);
    check("in", ::Operator::F_INIT);
    check("not_connected", ::Operator::F_INIT);
    check("out_v", ::Operator::O_I);
    check("out_r", ::Operator::O_I);
    check("in_v", ::Operator::S);
    check("in_r", ::Operator::S);
    check("not_connected_v", ::Operator::S);
    check("out", ::Operator::O_F);
}

TEST_F(libmuscle_instance_base, create_instance_profiling) {
    Instance instance(test_argc_, test_argv_, declared_ports_);

    ASSERT_EQ(instance.impl_()->profiler_->record_event.call_args_list.size(), 2);
}

TEST_F(libmuscle_instance_base, create_instance_connecting) {
    auto & rpret = MockMMPClient::return_value.request_peers.return_value.get();
    auto & peer_dims = std::get<1>(rpret);
    peer_dims["component"] = {};
    peer_dims["other"] = {};

    auto & peer_locs = std::get<2>(rpret);
    peer_locs["component"] = {"tcp:localhost:9003"};
    peer_locs["other"] = {"tcp:localhost:9004"};

    MockMMPClient::return_value.get_settings.return_value.get()["test"] = 37;

    Instance instance(test_argc_, test_argv_, declared_ports_);

    auto const & connect_ports = instance.impl_()->port_manager_->connect_ports;
    ASSERT_TRUE(connect_ports.called_once());
    auto const & peer_info = connect_ports.call_arg<0>(0);
    ASSERT_EQ(peer_info.kernel_, "component");
    ASSERT_EQ(peer_info.index_.size(), 0u);
    ASSERT_EQ(peer_info.peer_dims_, peer_dims);
    ASSERT_EQ(peer_info.peer_locations_, peer_locs);

    auto const & impl = *instance.impl_();
    ASSERT_TRUE(impl.communicator_->set_peer_info.called_once());
    ASSERT_EQ(impl.communicator_->set_peer_info.call_arg<0>(), peer_info);
    ASSERT_EQ(impl.settings_manager_.base.at("test"), 37);
}

TEST_F(libmuscle_instance_base, create_instance_set_up_checkpointing) {
    auto & gci_ret = MockMMPClient::return_value.get_checkpoint_info.return_value.get();
    std::get<2>(gci_ret) = "/dummy/resume/path";
    std::get<3>(gci_ret) = "/dummy/snapshot/path";

    Instance instance(test_argc_, test_argv_, declared_ports_);

    auto const & impl = *instance.impl_();
    ASSERT_TRUE(impl.trigger_manager_->set_checkpoint_info.called_with(
            std::get<0>(gci_ret), std::get<1>(gci_ret)));
    ASSERT_TRUE(impl.snapshot_manager_->prepare_resume.called_with(
            std::get<2>(gci_ret), std::get<3>(gci_ret)));
    // no need to test that it's a different object due to value semantics
}

TEST_F(libmuscle_instance_base, create_instance_set_up_logging) {
    std::unordered_map<Reference, SettingValue> settings = {
        {"muscle_local_log_level", "debug"},
        {"muscle_remote_log_level", "error"}};

    MockSettingsManager::return_value.get_setting.side_effect = [&settings](
            Reference const & instance, Reference const & setting_name) -> SettingValue const & {
        return settings.at(setting_name);
    };

    Instance instance(test_argc_, test_argv_, declared_ports_);

    auto const & impl = *instance.impl_();
    ASSERT_EQ(impl.logger_->set_local_level.call_arg<0>(), LogLevel::DEBUG);
    ASSERT_EQ(impl.logger_->set_remote_level.call_arg<0>(), LogLevel::ERROR);
}

TEST_F(libmuscle_instance, shutdown_instance) {
    std::string msg = "Testing";

    auto const & prof_rec_ev = instance_.impl_()->profiler_->record_event;
    std::size_t num_profile_events = prof_rec_ev.call_args_list.size();

    instance_.error_shutdown(msg);

    ASSERT_TRUE(logger_.caplog.any_call(LogLevel::CRITICAL, msg));
    ASSERT_TRUE(communicator_.shutdown.called());

    ASSERT_TRUE(mmp_client_.deregister_instance.called_once_with());
    ASSERT_TRUE(mmp_client_.close.called_once_with());

    ASSERT_EQ(prof_rec_ev.call_args_list.size(), num_profile_events + 1);
    ASSERT_TRUE(profiler_.shutdown.called_once_with());
}

TEST_F(libmuscle_instance, list_settings) {
    instance_.list_settings();
    ASSERT_TRUE(settings_manager_.list_settings.called_with("component"));
}

TEST_F(libmuscle_instance, get_setting) {
    settings_manager_.get_setting.side_effect = {};
    settings_manager_.get_setting.return_value = 42;
    ASSERT_EQ(instance_.get_setting_as<int>("test"), 42);
    ASSERT_TRUE(settings_manager_.get_setting.called_with("component", "test"));
}

TEST_F(libmuscle_instance, list_ports) {
    instance_.list_ports();
    ASSERT_TRUE(port_manager_.list_ports.called_once_with());
}

TEST_F(libmuscle_instance, is_connected) {
    ASSERT_TRUE(instance_.is_connected("in"));
    ASSERT_FALSE(instance_.is_connected("not_connected"));
    ASSERT_TRUE(instance_.is_connected("out_v"));
    ASSERT_TRUE(instance_.is_connected("out_r"));
    ASSERT_TRUE(instance_.is_connected("in_v"));
    ASSERT_TRUE(instance_.is_connected("in_r"));
    ASSERT_FALSE(instance_.is_connected("not_connected_v"));
    ASSERT_TRUE(instance_.is_connected("out"));
}

TEST_F(libmuscle_instance, is_vector_port) {
    ASSERT_FALSE(instance_.is_vector_port("in"));
    ASSERT_FALSE(instance_.is_vector_port("not_connected"));
    ASSERT_TRUE(instance_.is_vector_port("out_v"));
    ASSERT_TRUE(instance_.is_vector_port("out_r"));
    ASSERT_TRUE(instance_.is_vector_port("in_v"));
    ASSERT_TRUE(instance_.is_vector_port("in_r"));
    ASSERT_TRUE(instance_.is_vector_port("not_connected_v"));
    ASSERT_FALSE(instance_.is_vector_port("out"));
}

TEST_F(libmuscle_instance, is_resizable) {
    for (auto const & port : {"in", "not_connected", "out_v", "in_v", "out"})
        ASSERT_FALSE(instance_.is_resizable(port));

    ASSERT_TRUE(instance_.is_resizable("out_r"));
    ASSERT_TRUE(instance_.is_resizable("in_r"));
    ASSERT_TRUE(instance_.is_resizable("not_connected_v"));
}

TEST_F(libmuscle_instance, get_port_length) {
    ASSERT_EQ(instance_.get_port_length("out_v"), 13);
    ASSERT_EQ(instance_.get_port_length("out_r"), 0);
    ASSERT_EQ(instance_.get_port_length("in_v"), 13);
    ASSERT_EQ(instance_.get_port_length("in_r"), 0);
}

TEST_F(libmuscle_instance, set_port_length) {
    instance_.set_port_length("not_connected_v", 7);
    ASSERT_EQ(port_manager_.get_port("not_connected_v").get_length(), 7);
}

TEST_F(libmuscle_instance, reuse_set_overlay) {
    port_manager_.settings_in_connected.return_value = true;
    mock_ports_["in"]->is_connected_ = false;

    Message mock_msg(
            0.0, {}, Settings({{"s1", 1}, {"s2", 2}}), Settings({{"s0", 0}}));
    communicator_.receive_message.return_value = std::make_tuple(mock_msg, 0.0);

    instance_.reuse_instance();

    ASSERT_TRUE(communicator_.receive_message.called_with("muscle_settings_in"));
    ASSERT_EQ(settings_manager_.overlay["s0"], 0);
    ASSERT_EQ(settings_manager_.overlay["s1"], 1);
    ASSERT_EQ(settings_manager_.overlay["s2"], 2);
}

TEST_F(libmuscle_instance, reuse_closed_port) {
    for (auto const & closed_port : {"muscle_settings_in", "in"}) {
        port_manager_.settings_in_connected.return_value = true;
        communicator_.receive_message.side_effect = [&closed_port](
                std::string const & port_name, Optional<int> slot = {},
                Optional<Message> const & default_msg = {}) -> std::tuple<Message, double>
            {
                if (port_name == closed_port)
                    return std::make_tuple(Message(0.0, ClosePort(), Settings()), 0.0);
                else
                    return std::make_tuple(Message(0.0, Settings(), Settings()), 0.0);
            };

        ASSERT_FALSE(instance_.reuse_instance());
    }
}

TEST_F(libmuscle_instance, reuse_f_init_vector_port) {
    port_manager_.get_port("in").length_ = 10;

    communicator_.receive_message.side_effect = [](
            std::string const & port_name, Optional<int> slot = {},
            Optional<Message> const & default_msg = {}) -> std::tuple<Message, double>
        {
            Message mock_msg(0.0, Settings());
            return std::make_tuple(mock_msg, 0.0);
        };

    ASSERT_TRUE(instance_.reuse_instance());
}

TEST_F(libmuscle_instance, reuse_no_f_init_ports) {
    port_manager_.list_ports.return_value = PortsDescription();

    ASSERT_TRUE(instance_.reuse_instance());
    ASSERT_FALSE(instance_.reuse_instance());
}

TEST_F(libmuscle_instance, send_message) {
    std::string port("out_v");
    Message msg(0.0);
    int slot = 3;

    instance_.send(port, msg, slot);

    auto const & smsg = communicator_.send_message;
    ASSERT_TRUE(smsg.called_once());
    ASSERT_EQ(smsg.call_arg<0>(), port);
    ASSERT_EQ(smsg.call_arg<1>().settings_, settings_manager_.overlay);
    ASSERT_EQ(smsg.call_arg<2>(), slot);
}

TEST_F(libmuscle_instance, send_on_invalid_port) {
    Message mock_msg(0.0);
    ASSERT_THROW((instance_.send("does_not_exist", mock_msg)), std::logic_error);
}

TEST_F(libmuscle_instance, send_after_resize) {
    Message mock_msg(0.0);
    ASSERT_THROW((instance_.send("out_r", mock_msg, 13)), std::runtime_error);

    instance_.set_port_length("out_r", 20);
    instance_.send("out_r", mock_msg, 13);
}

TEST_F(libmuscle_instance, receive_on_invalid_port) {
    ASSERT_THROW(instance_.receive("does_not_exist"), std::logic_error);
}

TEST_F(libmuscle_instance, receive_f_init) {
    Message mock_msg(0.0, Settings());
    communicator_.receive_message.return_value = std::make_tuple(mock_msg, 0.0);

    instance_.reuse_instance();

    auto msg = instance_.receive("in");

    ASSERT_EQ(msg, mock_msg);
}

TEST_F(libmuscle_instance, receive_default_f_init) {
    Message default_msg(0.0, "testing");

    auto msg = instance_.receive("not_connected", default_msg);

    ASSERT_EQ(msg, default_msg);
}

TEST_F(libmuscle_instance, receive_default) {
    Message default_msg(0.0, "testing");

    auto msg = instance_.receive("not_connected_v", 42, default_msg);

    ASSERT_EQ(msg, default_msg);
}

TEST_F(libmuscle_instance, receive_no_default) {
    ASSERT_THROW(instance_.receive("not_connected"), std::logic_error);
    ASSERT_THROW(instance_.receive("not_connected_v"), std::runtime_error);
}

TEST_F(libmuscle_instance, receive_inconsistent_settings) {
    communicator_.receive_message.side_effect = [](
            std::string const & port_name, Optional<int> const & slot,
            Optional<Message> const & default_msg)
        {
            if (port_name == "muscle_settings_in")
                return std::make_tuple(
                        Message(0.0, Settings({{"s1", 1}}), Settings()),
                        0.0);
            return std::make_tuple(
                    Message(0.0, DataConstRef(), Settings({{"s0", 0}})),
                    0.0);
        };

    port_manager_.settings_in_connected.return_value = true;

    ASSERT_THROW(instance_.reuse_instance(), std::logic_error);
}

TEST_F(libmuscle_instance_dont_apply_overlay, receive_with_settings) {
    Message mock_msg(0.0);
    mock_msg.settings_ = Settings({{"s0", 0}, {"s1", 1}});
    communicator_.receive_message.return_value = std::make_tuple(mock_msg, 0.0);

    instance_dont_apply_overlay_.reuse_instance();
    auto msg = instance_dont_apply_overlay_.receive("in");

    ASSERT_EQ(msg.settings().at("s0"), 0);
    ASSERT_EQ(msg.settings().at("s1"), 1);

    ASSERT_EQ(settings_manager_.overlay.size(), 0);
}

TEST_F(libmuscle_instance_dont_apply_overlay, receive_with_settings_default) {
    port_manager_.get_port("in").is_connected_ = false;

    instance_dont_apply_overlay_.reuse_instance();

    Message default_msg(11.1);
    default_msg.settings_ = Settings({{"test", "testing"}});

    auto msg = instance_dont_apply_overlay_.receive("in", default_msg);

    ASSERT_EQ(msg, default_msg);
    ASSERT_EQ(msg.settings_, default_msg.settings_);
    ASSERT_EQ(settings_manager_.overlay.size(), 0u);
}


struct libmuscle_instance_checkpoints : libmuscle_instance, TempDirFixture {
    libmuscle_instance_checkpoints() {
        MockTriggerManager::return_value.has_checkpoints.return_value = true;
    }
};


TEST_F(libmuscle_instance_checkpoints, checkpoint_support_0) {
    ASSERT_THROW(Instance(test_argc_, test_argv_, InstanceFlags::NONE), std::runtime_error);
}

TEST_F(libmuscle_instance_checkpoints, checkpoint_support_1) {
    Instance(test_argc_, test_argv_, InstanceFlags::USES_CHECKPOINT_API);
}

TEST_F(libmuscle_instance_checkpoints, checkpoint_support_2) {
    Instance(test_argc_, test_argv_, InstanceFlags::KEEPS_NO_STATE_FOR_NEXT_USE);
}

TEST_F(libmuscle_instance_checkpoints, checkpoint_support_3) {
    Instance(test_argc_, test_argv_, InstanceFlags::STATE_NOT_REQUIRED_FOR_NEXT_USE);
}

