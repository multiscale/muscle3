// Inject mocks
#define LIBMUSCLE_MOCK_COMMUNICATOR <mocks/mock_communicator.hpp>
#define LIBMUSCLE_MOCK_LOGGER <mocks/mock_logger.hpp>
#define LIBMUSCLE_MOCK_MMP_CLIENT <mocks/mock_mmp_client.hpp>
#define LIBMUSCLE_MOCK_PROFILER <mocks/mock_profiler.hpp>

// into the real implementation to test.
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
using libmuscle::_MUSCLE_IMPL_NS::Optional;
using libmuscle::_MUSCLE_IMPL_NS::Port;
using libmuscle::_MUSCLE_IMPL_NS::PortsDescription;

using ymmsl::Reference;


int main(int argc, char *argv[]) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}


std::vector<char const *> test_argv() {
    char const * arg0 = "\0";
    char const * arg1 = "--muscle-instance=test_instance[13][42]";
    char const * arg2 = "--muscle-manager=node042:9000";
    return std::vector<char const *>({arg0, arg1, arg2});
}


class libmuscle_instance : public ::testing::Test {
    RESET_MOCKS(
            ::libmuscle::_MUSCLE_IMPL_NS::MockCommunicator,
            ::libmuscle::_MUSCLE_IMPL_NS::MockLogger,
            ::libmuscle::_MUSCLE_IMPL_NS::MockMMPClient,
            ::libmuscle::_MUSCLE_IMPL_NS::MockProfiler);
};


TEST_F(libmuscle_instance, create_instance) {
    auto argv = test_argv();
    Instance instance(argv.size(), argv.data(),
            PortsDescription({
                {Operator::F_INIT, {"in1"}},
                {Operator::O_F, {"out1", "out2[]"}}
                }));

    ASSERT_EQ(instance.impl_()->instance_name_, "test_instance[13][42]");

    auto const & constructor = instance.impl_()->manager_->constructor;
    ASSERT_TRUE(constructor.called_once());
    ASSERT_EQ(constructor.call_arg<0>(), "test_instance[13][42]");
    ASSERT_EQ(constructor.call_arg<1>(), "node042:9000");

    ASSERT_TRUE(instance.impl_()->communicator_->constructor.called_once());

    auto const & register_instance = instance.impl_()->manager_->register_instance;
    ASSERT_EQ(register_instance.call_arg<0>().at(0), "tcp:test1,test2");
    ASSERT_EQ(register_instance.call_arg<0>().at(1), "tcp:test3");
    ASSERT_EQ(register_instance.call_arg<1>().size(), 3);

    auto & settings = instance.impl_()->settings_manager_;
    ASSERT_EQ(settings.base["test_int"], 10);
    ASSERT_EQ(settings.base["test_string"], "testing");
    ASSERT_TRUE(settings.overlay.empty());
}


TEST_F(libmuscle_instance, send) {
    auto argv = test_argv();
    Instance instance(argv.size(), argv.data(),
            PortsDescription({
                {Operator::O_F, {"out"}}
                }));

    auto & communicator = *instance.impl_()->communicator_;
    communicator.list_ports.return_value = PortsDescription({
                {Operator::O_F, {"out"}}
                });
    communicator.port_exists.return_value = true;
    Port out_port("out", Operator::O_F, false, true, 0, {});
    communicator.get_port.return_value = &out_port;

    Message msg(3.0, 4.0, "Testing");
    instance.send("out", msg);

    ASSERT_EQ(communicator.send_message.call_arg<0>(), "out");
    ASSERT_FALSE(communicator.send_message.call_arg<2>().is_set());
    auto const & sent_msg = communicator.send_message.call_arg<1>();
    ASSERT_EQ(sent_msg.timestamp(), 3.0);
    ASSERT_EQ(sent_msg.next_timestamp(), 4.0);
    ASSERT_EQ(sent_msg.data().as<std::string>(), "Testing");
}

TEST_F(libmuscle_instance, send_invalid_port) {
    auto argv = test_argv();
    Instance instance(argv.size(), argv.data(),
            PortsDescription({
                {Operator::O_F, {"out"}}
                }));

    instance.impl_()->communicator_->port_exists.return_value = false;

    Message msg(3.0, 4.0, "Testing");
    ASSERT_THROW(instance.send("out", msg), std::logic_error);
}

TEST_F(libmuscle_instance, get_setting) {
    auto argv = test_argv();
    Instance instance(argv.size(), argv.data());

    Settings settings;
    settings["test1"] = "test";
    settings["test2"] = {1.0, 2.0};
    settings["test3"] = 10;
    settings["test4"] = 10000000000l;    // does not fit 32 bits
    settings["test5"] = 10.0;
    settings["test6"] = 1.0f / 3.0f;     // not exactly representable
    instance.impl_()->settings_manager_.base = settings;

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

TEST_F(libmuscle_instance, receive) {
    auto argv = test_argv();
    Port in_port("in", Operator::S, false, true, 0, {});

    Instance instance(argv.size(), argv.data(),
            PortsDescription({
                {Operator::S, {"in"}}
                }));


    auto & communicator = *instance.impl_()->communicator_;
    communicator.list_ports.return_value = PortsDescription({
            {Operator::S, {"in"}}
            });
    communicator.port_exists.return_value = true;
    communicator.get_port.return_value = &in_port;
    communicator.receive_message.return_value = Message(
            1.0, 2.0, "Testing receive", Settings());

    Message msg(instance.receive("in"));

    ASSERT_EQ(msg.timestamp(), 1.0);
    ASSERT_TRUE(msg.has_next_timestamp());
    ASSERT_EQ(msg.next_timestamp(), 2.0);
    ASSERT_TRUE(msg.data().is_a<std::string>());
    ASSERT_EQ(msg.data().as<std::string>(), "Testing receive");

    // Make sure Instance shuts down cleanly
    // in_port will be gone already because it was created after instance, but it will
    // still be returned by get_port, and then we crash. If the instance thinks that
    // there are no ports, then it won't try to close them either.
    communicator.list_ports.return_value = PortsDescription();
}

TEST_F(libmuscle_instance, receive_f_init) {
    auto argv = test_argv();
    Port in_port("in", Operator::F_INIT, false, true, 0, {});

    Instance instance(argv.size(), argv.data(),
            PortsDescription({
                {Operator::F_INIT, {"in"}}
                }));

    auto & communicator = *instance.impl_()->communicator_;
    communicator.settings_in_connected.return_value = false;
    communicator.port_exists.return_value = true;
    communicator.list_ports.return_value = PortsDescription({
                {Operator::F_INIT, {"in"}}
                });
    communicator.get_port.return_value = &in_port;
    communicator.receive_message.return_value = Message(
            1.0, 2.0, "Testing receive", Settings());

    ASSERT_TRUE(instance.reuse_instance());
    Message msg(instance.receive("in"));

    ASSERT_EQ(msg.timestamp(), 1.0);
    ASSERT_TRUE(msg.has_next_timestamp());
    ASSERT_EQ(msg.next_timestamp(), 2.0);
    ASSERT_TRUE(msg.data().is_a<std::string>());
    ASSERT_EQ(msg.data().as<std::string>(), "Testing receive");

    Port port("in", Operator::F_INIT, false, true, 0, {});
    port.set_closed();
    communicator.get_port.return_value = &port;
    ASSERT_THROW(instance.receive("in"), std::logic_error);

    // Make sure Instance shuts down cleanly (see receive above)
    communicator.list_ports.return_value = PortsDescription();
}

TEST_F(libmuscle_instance, receive_default) {
    auto argv = test_argv();
    Port in_port("in", Operator::S, false, false, 0, {});

    Instance instance(argv.size(), argv.data(),
            PortsDescription({
                {Operator::S, {"in"}}
                }));

    auto & communicator = *instance.impl_()->communicator_;
    communicator.list_ports.return_value = PortsDescription({
                {Operator::S, {"in"}}
                });
    communicator.port_exists.return_value = true;
    communicator.get_port.return_value = &in_port;

    Message default_msg(1.0, 2.0, "Testing receive");
    communicator.receive_message.return_value = default_msg;
    Message msg(instance.receive("in", default_msg));

    ASSERT_EQ(msg.timestamp(), 1.0);
    ASSERT_TRUE(msg.has_next_timestamp());
    ASSERT_EQ(msg.next_timestamp(), 2.0);
    ASSERT_TRUE(msg.data().is_a<std::string>());
    ASSERT_EQ(msg.data().as<std::string>(), "Testing receive");

    // Make sure Instance shuts down cleanly (see receive above)
    communicator.list_ports.return_value = PortsDescription();
}

TEST_F(libmuscle_instance, receive_invalid_port) {
    auto argv = test_argv();
    Port in_port("in", Operator::S, false, false, 0, {});

    Instance instance(argv.size(), argv.data(),
            PortsDescription({
                {Operator::S, {"in"}}
                }));

    auto & communicator = *instance.impl_()->communicator_;
    communicator.list_ports.return_value = PortsDescription({
                {Operator::S, {"in"}}
                });
    communicator.port_exists.return_value = false;
    communicator.get_port.return_value = &in_port;

    ASSERT_THROW(instance.receive("does_not_exist", 1), std::logic_error);

    // Make sure Instance shuts down cleanly (see receive above)
    communicator.list_ports.return_value = PortsDescription({});
}

TEST_F(libmuscle_instance, receive_with_settings) {
    auto argv = test_argv();
    Port in_port("in", Operator::F_INIT, false, true, 0, {});

    Instance instance(argv.size(), argv.data(),
            PortsDescription({
                {Operator::F_INIT, {"in"}}
                }),
            InstanceFlags::DONT_APPLY_OVERLAY);

    auto & communicator = *instance.impl_()->communicator_;
    communicator.settings_in_connected.return_value = false;
    communicator.list_ports.return_value = PortsDescription({
                {Operator::F_INIT, {"in"}}
                });
    communicator.port_exists.return_value = true;
    communicator.get_port.return_value = &in_port;

    Settings recv_settings;
    recv_settings["test1"] = 12;
    communicator.receive_message.return_value = Message(
            1.0, "Testing with settings", recv_settings);

    ASSERT_TRUE(instance.reuse_instance());
    Message msg(instance.receive_with_settings("in"));

    ASSERT_EQ(msg.timestamp(), 1.0);
    ASSERT_FALSE(msg.has_next_timestamp());
    ASSERT_TRUE(msg.data().is_a<std::string>());
    ASSERT_EQ(msg.data().as<std::string>(), "Testing with settings");
    ASSERT_TRUE(msg.has_settings());
    ASSERT_EQ(msg.settings().at("test1"), 12);

    // Make sure Instance shuts down cleanly (see receive above)
    communicator.list_ports.return_value = PortsDescription({});
}

TEST_F(libmuscle_instance, receive_parallel_universe) {
    auto argv = test_argv();
    Port port("in", Operator::F_INIT, false, true, 0, {});

    Instance instance(argv.size(), argv.data(),
            PortsDescription({
                {Operator::F_INIT, {"in"}}
                }));

    auto & communicator = *instance.impl_()->communicator_;
    communicator.list_ports.return_value = PortsDescription({
                {Operator::F_INIT, {"in"}}
                });
    port.set_closed();
    communicator.get_port.return_value = &port;

    communicator.settings_in_connected.return_value = true;

    communicator.receive_message.side_effect = [](
            std::string const & port_name, Optional<int> slot,
            Optional<Message> const & default_msg) -> Message
    {
        Settings recv_settings;
        if (port_name == "in") {
            recv_settings["test1"] = 12;
            return Message(1.0, "Testing", recv_settings);
        }
        if (port_name == "muscle_settings_in") {
            recv_settings["test2"] = "test";
            return Message(1.0, "Testing", recv_settings);
        }
        throw std::runtime_error("Unexpected port name in receive_parallel_universe");
    };

    ASSERT_THROW(instance.reuse_instance(), std::logic_error);

    // Make sure Instance shuts down cleanly (see receive above)
    communicator.list_ports.return_value = PortsDescription({});
}

TEST_F(libmuscle_instance, receive_with_settings_default) {
    auto argv = test_argv();
    Port in_port("in", Operator::F_INIT, false, false, 0, {});

    Instance instance(argv.size(), argv.data(),
            PortsDescription({
                {Operator::F_INIT, {"not_connected"}}
                }),
            InstanceFlags::DONT_APPLY_OVERLAY);

    auto & communicator = *instance.impl_()->communicator_;
    communicator.settings_in_connected.return_value = false;
    communicator.list_ports.return_value = PortsDescription({
            {Operator::F_INIT, {"not_connected"}}
            });

    communicator.port_exists.return_value = true;
    communicator.get_port.return_value = &in_port;

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


TEST_F(libmuscle_instance, reuse_instance_receive_overlay) {
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

    auto & communicator = *instance.impl_()->communicator_;
    communicator.settings_in_connected.return_value = true;
    communicator.receive_message.return_value = Message(
            0.0, test_overlay, test_base_settings);

    instance.reuse_instance();

    ASSERT_EQ(instance.impl_()->settings_manager_.overlay.size(), 2);
    ASSERT_EQ(instance.impl_()->settings_manager_.overlay.at("test1"), 24);
    ASSERT_EQ(instance.impl_()->settings_manager_.overlay.at("test2"), "abc");
}

TEST_F(libmuscle_instance, reuse_instance_closed_port) {
    auto argv = test_argv();
    std::unordered_map<std::string, Port> ports = {
        {"not_connected", Port("not_connected", Operator::F_INIT, false, false, 0, {})},
        {"in", Port("in", Operator::F_INIT, false, true, 0, {})},
        {"out", Port("out", Operator::O_F, false, true, 0, {})}};

    Instance instance(argv.size(), argv.data(),
            PortsDescription({
                {Operator::F_INIT, {"in", "not_connected"}},
                {Operator::O_F, {"out"}}
                }));

    auto & communicator = *instance.impl_()->communicator_;
    communicator.settings_in_connected.return_value = true;
    communicator.receive_message.side_effect = [&ports](
            std::string const & port_name, Optional<int> slot,
            Optional<Message> const & default_msg) -> Message
    {
        if (port_name == "in") {
            ports.at(port_name).set_closed();
            return Message(0.0, ClosePort(), Settings());
        }
        if (port_name == "muscle_settings_in") {
            return Message(0.0, Settings(), Settings());
        }
        throw std::runtime_error("Unexpected port name in reuse_instance_closed_port");
    };

    communicator.list_ports.return_value = PortsDescription({
                {Operator::F_INIT, {"in", "not_connected"}},
                {Operator::O_F, {"out"}}
                });

    communicator.get_port.side_effect = [&ports]
        (std::string const & port_name) -> Port &
    {
        return ports.at(port_name);
    };

    ASSERT_FALSE(instance.reuse_instance());

    // Make sure Instance shuts down cleanly (see receive above)
    communicator.settings_in_connected.return_value = false;
    communicator.list_ports.return_value = PortsDescription({});
}

TEST_F(libmuscle_instance, reuse_instance_vector_port) {
    auto argv = test_argv();
    Port in_port("in", Operator::F_INIT, true, true, 0, {10});

    std::unordered_map<ymmsl::Reference, Message> messages = {
        {"muscle_settings_in", Message(0.0, Settings(), Settings())}};

    for (int i = 0; i < 10; ++i) {
        Reference port_slot("in");
        port_slot += i;
        std::ostringstream oss;
        oss << "test " << i;
        messages.insert({port_slot, Message(0.0, oss.str(), Settings())});
    }

    Instance instance(argv.size(), argv.data(),
            PortsDescription({
                {Operator::F_INIT, {"in[]"}}
                }));

    auto & communicator = *instance.impl_()->communicator_;

    communicator.settings_in_connected.return_value = true;

    communicator.receive_message.side_effect = [&messages, &in_port](
            std::string const & port, Optional<int> slot,
            Optional<Message> const & default_msg)
    {
        Reference port_slot(port);
        if (slot.is_set())
            port_slot += slot.get();
        auto const & msg = messages.at(port_slot);
        if (is_close_port(msg.data()))
            in_port.set_closed(slot.get());
        return msg;
    };

    communicator.list_ports.return_value = PortsDescription({
                {Operator::F_INIT, {"in"}}
                });

    communicator.port_exists.return_value = true;
    communicator.get_port.return_value = &in_port;

    ASSERT_TRUE(instance.reuse_instance());

    auto msg = instance.receive("in", 5);
    ASSERT_EQ(msg.timestamp(), 0.0);
    ASSERT_FALSE(msg.has_next_timestamp());
    ASSERT_EQ(msg.data().as<std::string>(), "test 5");

    // make sure Instance shuts down cleanly
    messages.clear();
    for (int i = 0; i < 10; ++i) {
        Reference port_slot("in");
        port_slot += i;
        messages.insert({port_slot, Message(0.0, ClosePort(), Settings())});
    }
}

TEST_F(libmuscle_instance, reuse_instance_no_f_init_ports) {
    auto argv = test_argv();
    Instance instance(argv.size(), argv.data(), PortsDescription({}));

    instance.impl_()->communicator_->settings_in_connected.return_value = false;

    ASSERT_TRUE(instance.reuse_instance());
    ASSERT_FALSE(instance.reuse_instance());
}

