// Inject mocks
#define LIBMUSCLE_MOCK_COMMUNICATOR <mocks/mock_communicator.hpp>
#define LIBMUSCLE_MOCK_LOGGER <mocks/mock_logger.hpp>
#define LIBMUSCLE_MOCK_MMP_CLIENT <mocks/mock_mmp_client.hpp>
#define LIBMUSCLE_MOCK_PROFILER <mocks/mock_profiler.hpp>

// into the real implementation,
#include <ymmsl/ymmsl.hpp>

#include <libmuscle/close_port.cpp>
#include <libmuscle/data.cpp>
#include <libmuscle/instance.cpp>
#include <libmuscle/logging.cpp>
#include <libmuscle/mcp/data_pack.cpp>
#include <libmuscle/message.cpp>
#include <libmuscle/port.cpp>
#include <libmuscle/settings_manager.cpp>
#include <libmuscle/snapshot_manager.cpp>
#include <libmuscle/timestamp.cpp>

// then add mock implementations as needed.
#include <mocks/mock_communicator.cpp>
#include <mocks/mock_logger.cpp>
#include <mocks/mock_mmp_client.cpp>
#include <mocks/mock_profiler.cpp>

// Test code dependencies
#include <memory>
#include <stdexcept>
#include <typeinfo>

#include <gtest/gtest.h>

#include <libmuscle/instance.hpp>
#include <libmuscle/namespace.hpp>
#include <libmuscle/settings_manager.hpp>
#include <mocks/mock_communicator.hpp>

using libmuscle::_MUSCLE_IMPL_NS::ClosePort;
using libmuscle::_MUSCLE_IMPL_NS::Instance;
using libmuscle::_MUSCLE_IMPL_NS::InstanceFlags;
using libmuscle::_MUSCLE_IMPL_NS::Message;
using libmuscle::_MUSCLE_IMPL_NS::MockCommunicator;
using libmuscle::_MUSCLE_IMPL_NS::MockMMPClient;
using libmuscle::_MUSCLE_IMPL_NS::PortsDescription;

using ymmsl::Reference;


int main(int argc, char *argv[]) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}


// Helpers for accessing internal state
namespace libmuscle { namespace _MUSCLE_IMPL_NS {

class TestInstance {
    public:
        static Reference & instance_name_(Instance & instance) {
            return instance.impl_()->instance_name_;
        }

        static SettingsManager & settings_manager_(Instance & instance) {
            return instance.impl_()->settings_manager_;
        }
};

} }

using libmuscle::_MUSCLE_IMPL_NS::TestInstance;

/* Mocks have internal state, which needs to be reset before each test. This
 * means that the tests are not reentrant, and cannot be run in parallel.
 * It's all fast enough, so that's not a problem.
 */
void reset_mocks() {
    MockCommunicator::reset();
    MockMMPClient::reset();
}

std::vector<char const *> test_argv() {
    char const * arg0 = "\0";
    char const * arg1 = "--muscle-instance=test_instance[13][42]";
    char const * arg2 = "--muscle-manager=node042:9000";
    return std::vector<char const *>({arg0, arg1, arg2});
}


TEST(libmuscle_instance, create_instance) {
    reset_mocks();

    auto argv = test_argv();
    Instance instance(argv.size(), argv.data(),
            PortsDescription({
                {Operator::F_INIT, {"in1"}},
                {Operator::O_F, {"out1", "out2[]"}}
                }));

    ASSERT_EQ(TestInstance::instance_name_(instance), "test_instance[13][42]");
    ASSERT_EQ(MockMMPClient::num_constructed, 1);
    ASSERT_EQ(MockMMPClient::last_instance_id, "test_instance[13][42]");
    ASSERT_EQ(MockMMPClient::last_location, "node042:9000");
    ASSERT_EQ(MockCommunicator::num_constructed, 1);
    ASSERT_EQ(MockMMPClient::last_registered_locations.at(0), "tcp:test1,test2");
    ASSERT_EQ(MockMMPClient::last_registered_locations.at(1), "tcp:test3");
    ASSERT_EQ(MockMMPClient::last_registered_ports.size(), 3);
    auto & settings = TestInstance::settings_manager_(instance);
    ASSERT_EQ(settings.base["test_int"], 10);
    ASSERT_EQ(settings.base["test_string"], "testing");
    ASSERT_TRUE(settings.overlay.empty());
}


TEST(libmuscle_instance, send) {
    reset_mocks();
    auto argv = test_argv();
    Instance instance(argv.size(), argv.data(),
            PortsDescription({
                {Operator::O_F, {"out"}}
                }));

    MockCommunicator::list_ports_return_value = PortsDescription({
                {Operator::O_F, {"out"}}
                });
    MockCommunicator::get_port_return_value.emplace(
            "out", Port("out", Operator::O_F, false, true, 0, {}));

    Message msg(3.0, 4.0, "Testing");
    instance.send("out", msg);

    ASSERT_EQ(MockCommunicator::last_sent_port, "out");
    ASSERT_FALSE(MockCommunicator::last_sent_slot.is_set());
    ASSERT_EQ(MockCommunicator::last_sent_message.timestamp(), 3.0);
    ASSERT_EQ(MockCommunicator::last_sent_message.next_timestamp(), 4.0);
    ASSERT_EQ(MockCommunicator::last_sent_message.data().as<std::string>(), "Testing");
}

TEST(libmuscle_instance, send_invalid_port) {
    reset_mocks();
    auto argv = test_argv();
    Instance instance(argv.size(), argv.data(),
            PortsDescription({
                {Operator::O_F, {"out"}}
                }));

    MockCommunicator::port_exists_return_value = false;

    Message msg(3.0, 4.0, "Testing");
    ASSERT_THROW(instance.send("out", msg), std::logic_error);
}

TEST(libmuscle_instance, get_setting) {
    reset_mocks();
    auto argv = test_argv();
    Instance instance(argv.size(), argv.data());

    Settings settings;
    settings["test1"] = "test";
    settings["test2"] = {1.0, 2.0};
    settings["test3"] = 10;
    settings["test4"] = 10000000000l;    // does not fit 32 bits
    settings["test5"] = 10.0;
    settings["test6"] = 1.0f / 3.0f;     // not exactly representable
    TestInstance::settings_manager_(instance).base = settings;

    ASSERT_TRUE(instance.get_setting("test1").is_a<std::string>());
    ASSERT_EQ(instance.get_setting("test1").as<std::string>(), "test");
    ASSERT_EQ(instance.get_setting_as<std::string>("test1"), "test");

    ASSERT_EQ(instance.get_setting_as<std::vector<double>>("test2"), std::vector<double>({1.0, 2.0}));

    ASSERT_EQ(instance.get_setting_as<int64_t>("test3"), 10l);
    ASSERT_EQ(instance.get_setting_as<int64_t>("test4"), 10000000000l);
    ASSERT_EQ(static_cast<int>(instance.get_setting_as<int32_t>("test3")), 10);
    ASSERT_THROW(instance.get_setting_as<int32_t>("test4"), std::bad_cast);

    ASSERT_EQ(instance.get_setting_as<double>("test5"), 10.0);
    ASSERT_EQ(instance.get_setting_as<double>("test6"), 1.0f / 3.0f);
    ASSERT_EQ(instance.get_setting_as<double>("test3"), 10.0);

    ASSERT_THROW(instance.get_setting("testx"), std::out_of_range);
    ASSERT_THROW(instance.get_setting_as<int64_t>("test1"), std::bad_cast);
}

TEST(libmuscle_instance, receive) {
    reset_mocks();
    auto argv = test_argv();
    Instance instance(argv.size(), argv.data(),
            PortsDescription({
                {Operator::S, {"in"}}
                }));

    MockCommunicator::list_ports_return_value = PortsDescription({
                {Operator::S, {"in"}}
                });
    MockCommunicator::get_port_return_value.emplace(
            "in", Port("in", Operator::S, false, true, 0, {}));
    MockCommunicator::next_received_message["in"] =
        std::make_unique<Message>(1.0, 2.0, "Testing receive", Settings());

    Message msg(instance.receive("in"));

    ASSERT_EQ(msg.timestamp(), 1.0);
    ASSERT_TRUE(msg.has_next_timestamp());
    ASSERT_EQ(msg.next_timestamp(), 2.0);
    ASSERT_TRUE(msg.data().is_a<std::string>());
    ASSERT_EQ(msg.data().as<std::string>(), "Testing receive");

    // make sure Instance shuts down cleanly
    MockCommunicator::next_received_message["in"] =
        std::make_unique<Message>(0.0, ClosePort(), Settings());
}

TEST(libmuscle_instance, receive_f_init) {
    reset_mocks();
    auto argv = test_argv();
    Instance instance(argv.size(), argv.data(),
            PortsDescription({
                {Operator::F_INIT, {"in"}}
                }));

    MockCommunicator::list_ports_return_value = PortsDescription({
                {Operator::F_INIT, {"in"}}
                });
    MockCommunicator::get_port_return_value.emplace(
            "in", Port("in", Operator::F_INIT, false, true, 0, {}));
    MockCommunicator::next_received_message["in"] =
        std::make_unique<Message>(1.0, 2.0, "Testing receive", Settings());

    ASSERT_TRUE(instance.reuse_instance());
    Message msg(instance.receive("in"));

    ASSERT_EQ(msg.timestamp(), 1.0);
    ASSERT_TRUE(msg.has_next_timestamp());
    ASSERT_EQ(msg.next_timestamp(), 2.0);
    ASSERT_TRUE(msg.data().is_a<std::string>());
    ASSERT_EQ(msg.data().as<std::string>(), "Testing receive");

    Port port("in", Operator::F_INIT, false, true, 0, {});
    port.set_closed();
    MockCommunicator::get_port_return_value.at("in") = port;
    ASSERT_THROW(instance.receive("in"), std::logic_error);
}

TEST(libmuscle_instance, receive_default) {
    reset_mocks();
    auto argv = test_argv();
    Instance instance(argv.size(), argv.data(),
            PortsDescription({
                {Operator::S, {"in"}}
                }));

    MockCommunicator::list_ports_return_value = PortsDescription({
                {Operator::S, {"in"}}
                });
    MockCommunicator::get_port_return_value.emplace(
            "in", Port("in", Operator::S, false, false, 0, {}));

    Message default_msg(1.0, 2.0, "Testing receive");

    Message msg(instance.receive("in", default_msg));

    ASSERT_EQ(msg.timestamp(), 1.0);
    ASSERT_TRUE(msg.has_next_timestamp());
    ASSERT_EQ(msg.next_timestamp(), 2.0);
    ASSERT_TRUE(msg.data().is_a<std::string>());
    ASSERT_EQ(msg.data().as<std::string>(), "Testing receive");
    ASSERT_THROW(instance.receive("not_connected"), std::logic_error);
}

TEST(libmuscle_instance, receive_invalid_port) {
    reset_mocks();
    auto argv = test_argv();
    Instance instance(argv.size(), argv.data(),
            PortsDescription({
                {Operator::S, {"in"}}
                }));

    MockCommunicator::list_ports_return_value = PortsDescription({
                {Operator::S, {"in"}}
                });
    MockCommunicator::get_port_return_value.emplace(
            "in", Port("in", Operator::S, false, false, 0, {}));

    ASSERT_THROW(instance.receive("does_not_exist", 1), std::logic_error);
}

TEST(libmuscle_instance, receive_with_settings) {
    reset_mocks();
    auto argv = test_argv();
    Instance instance(argv.size(), argv.data(),
            PortsDescription({
                {Operator::F_INIT, {"in"}}
                }),
            InstanceFlags::DONT_APPLY_OVERLAY);

    MockCommunicator::list_ports_return_value = PortsDescription({
                {Operator::F_INIT, {"in"}}
                });
    MockCommunicator::get_port_return_value.emplace(
            "in", Port("in", Operator::F_INIT, false, true, 0, {}));

    Settings recv_settings;
    recv_settings["test1"] = 12;
    MockCommunicator::next_received_message["in"] =
        std::make_unique<Message>(1.0, "Testing with settings", recv_settings);

    ASSERT_TRUE(instance.reuse_instance());
    Message msg(instance.receive_with_settings("in"));

    ASSERT_EQ(msg.timestamp(), 1.0);
    ASSERT_FALSE(msg.has_next_timestamp());
    ASSERT_TRUE(msg.data().is_a<std::string>());
    ASSERT_EQ(msg.data().as<std::string>(), "Testing with settings");
    ASSERT_TRUE(msg.has_settings());
    ASSERT_EQ(msg.settings().at("test1"), 12);

    // make sure Instance shuts down cleanly
    MockCommunicator::next_received_message["in"] =
        std::make_unique<Message>(0.0, ClosePort(), Settings());
}

TEST(libmuscle_instance, receive_parallel_universe) {
    reset_mocks();
    auto argv = test_argv();
    Instance instance(argv.size(), argv.data(),
            PortsDescription({
                {Operator::F_INIT, {"in"}}
                }));

    MockCommunicator::list_ports_return_value = PortsDescription({
                {Operator::F_INIT, {"in"}}
                });
    Port port("in", Operator::F_INIT, false, true, 0, {});
    port.set_closed();
    MockCommunicator::get_port_return_value.emplace("in", port);

    Settings recv_settings;
    recv_settings["test1"] = 12;
    MockCommunicator::next_received_message["in"] =
        std::make_unique<Message>(1.0, "Testing", recv_settings);
    recv_settings["test2"] = "test";
    MockCommunicator::next_received_message["muscle_settings_in"] =
        std::make_unique<Message>(1.0, recv_settings, Settings());

    ASSERT_THROW(instance.reuse_instance(), std::logic_error);
}

TEST(libmuscle_instance, receive_with_settings_default) {
    reset_mocks();
    auto argv = test_argv();
    Instance instance(argv.size(), argv.data(),
            PortsDescription({
                {Operator::F_INIT, {"not_connected"}}
                }),
            InstanceFlags::DONT_APPLY_OVERLAY);

    MockCommunicator::list_ports_return_value = PortsDescription({
                {Operator::F_INIT, {"not_connected"}}
                });
    MockCommunicator::get_port_return_value.emplace(
            "not_connected", Port("in", Operator::F_INIT, false, false, 0, {}));

    Settings default_settings;
    default_settings["test1"] = 12;
    Message default_msg(1.0, "Testing with settings", default_settings);

    ASSERT_TRUE(instance.reuse_instance());
    Message msg(instance.receive_with_settings("not_connected", default_msg));

    ASSERT_EQ(msg.timestamp(), 1.0);
    ASSERT_FALSE(msg.has_next_timestamp());
    ASSERT_TRUE(msg.data().is_a<std::string>());
    ASSERT_EQ(msg.data().as<std::string>(), "Testing with settings");
    ASSERT_TRUE(msg.has_settings());
    ASSERT_EQ(msg.settings().at("test1"), 12);
}


TEST(libmuscle_instance, reuse_instance_receive_overlay) {
    reset_mocks();
    auto argv = test_argv();
    Instance instance(argv.size(), argv.data(),
            PortsDescription({
                {Operator::F_INIT, {"in"}}
                }));

    Settings test_base_settings;
    test_base_settings["test1"] = 24;
    test_base_settings["test2"] = {1.3, 2.0};

    Settings test_overlay;
    test_overlay["test2"] = "abc";

    MockCommunicator::settings_in_connected_return_value = true;
    MockCommunicator::next_received_message["muscle_settings_in"] =
        std::make_unique<Message>(0.0, test_overlay, test_base_settings);

    instance.reuse_instance();

    ASSERT_EQ(TestInstance::settings_manager_(instance).overlay.size(), 2);
    ASSERT_EQ(TestInstance::settings_manager_(instance).overlay.at("test1"), 24);
    ASSERT_EQ(TestInstance::settings_manager_(instance).overlay.at("test2"), "abc");
}

TEST(libmuscle_instance, reuse_instance_closed_port) {
    reset_mocks();
    auto argv = test_argv();
    Instance instance(argv.size(), argv.data(),
            PortsDescription({
                {Operator::F_INIT, {"in", "not_connected"}},
                {Operator::O_F, {"out"}}
                }));

    MockCommunicator::settings_in_connected_return_value = true;
    MockCommunicator::next_received_message["muscle_settings_in"] =
        std::make_unique<Message>(0.0, Settings(), Settings());
    MockCommunicator::next_received_message["in"] =
        std::make_unique<Message>(0.0, ClosePort(), Settings());

    MockCommunicator::list_ports_return_value = PortsDescription({
                {Operator::F_INIT, {"in", "not_connected"}},
                {Operator::O_F, {"out"}}
                });

    MockCommunicator::get_port_return_value.emplace(
            "not_connected",
            Port("not_connected", Operator::F_INIT, false, false, 0, {}));
    MockCommunicator::get_port_return_value.emplace(
            "in", Port("in", Operator::F_INIT, false, true, 0, {}));
    MockCommunicator::get_port_return_value.emplace(
            "out", Port("out", Operator::O_F, false, true, 0, {}));

    ASSERT_FALSE(instance.reuse_instance());
}

TEST(libmuscle_instance, reuse_instance_vector_port) {
    reset_mocks();
    auto argv = test_argv();
    Instance instance(argv.size(), argv.data(),
            PortsDescription({
                {Operator::F_INIT, {"in[]"}}
                }));

    MockCommunicator::settings_in_connected_return_value = true;
    MockCommunicator::next_received_message["muscle_settings_in"] =
        std::make_unique<Message>(0.0, Settings(), Settings());

    for (int i = 0; i < 10; ++i) {
        Reference port_slot("in");
        port_slot += i;
        std::ostringstream oss;
        oss << "test " << i;
        MockCommunicator::next_received_message[port_slot] =
            std::make_unique<Message>(0.0, oss.str(), Settings());
    }

    MockCommunicator::list_ports_return_value = PortsDescription({
                {Operator::F_INIT, {"in"}}
                });

    MockCommunicator::get_port_return_value.emplace(
            "in", Port("in", Operator::F_INIT, true, true, 0, {10}));

    ASSERT_TRUE(instance.reuse_instance());

    auto msg = instance.receive("in", 5);
    ASSERT_EQ(msg.timestamp(), 0.0);
    ASSERT_FALSE(msg.has_next_timestamp());
    ASSERT_EQ(msg.data().as<std::string>(), "test 5");

    // make sure Instance shuts down cleanly
    for (int i = 0; i < 10; ++i) {
        Reference port_slot("in");
        port_slot += i;
        MockCommunicator::next_received_message[port_slot] =
            std::make_unique<Message>(0.0, ClosePort(), Settings());
    }
}

TEST(libmuscle_instance, reuse_instance_no_f_init_ports) {
    reset_mocks();
    auto argv = test_argv();
    Instance instance(argv.size(), argv.data(),
            PortsDescription({}));

    MockCommunicator::settings_in_connected_return_value = false;

    ASSERT_TRUE(instance.reuse_instance());
    ASSERT_FALSE(instance.reuse_instance());
}

