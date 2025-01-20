// Inject mocks
#define LIBMUSCLE_MOCK_LOGGER <mocks/mock_logger.hpp>

// into the real implementation to test.
#include <ymmsl/ymmsl.hpp>

#include <libmuscle/logging.cpp>
#include <libmuscle/mmsf_validator.cpp>

// Test code dependencies
#include <stdexcept>
#include <memory>

#include <gtest/gtest.h>
#include <gmock/gmock-matchers.h>

#include <libmuscle/mmsf_validator.hpp>
#include <libmuscle/port_manager.hpp>


using libmuscle::_MUSCLE_IMPL_NS::LogLevel;
using libmuscle::_MUSCLE_IMPL_NS::MMSFValidator;
using libmuscle::_MUSCLE_IMPL_NS::MockLogger;
using libmuscle::_MUSCLE_IMPL_NS::PeerDims;
using libmuscle::_MUSCLE_IMPL_NS::PeerInfo;
using libmuscle::_MUSCLE_IMPL_NS::PeerLocations;
using libmuscle::_MUSCLE_IMPL_NS::PortManager;
using libmuscle::_MUSCLE_IMPL_NS::PortsDescription;

using ymmsl::Conduit;
using ymmsl::Operator;
using ymmsl::Reference;

using testing::HasSubstr;


int main(int argc, char *argv[]) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}


struct libmuscle_mmsf_validator : ::testing::Test {
    std::unique_ptr<PortManager> port_manager_;
    std::unique_ptr<MMSFValidator> validator_;
    std::unique_ptr<MockLogger> logger_;

    void create_validator(PortsDescription const & declared_ports) {
        logger_ = std::make_unique<MockLogger>();
        port_manager_ = std::make_unique<PortManager>(std::vector<int>(), declared_ports);

        // Build peer info for port_manager.connect_ports
        Reference component_id("other");
        std::vector<Conduit> conduits;
        for (auto const & item : declared_ports) {
            for (auto const & port_name : item.second) {
                if (::ymmsl::allows_receiving(item.first)) {
                    conduits.emplace_back("component."+port_name, "other."+port_name);
                } else {
                    conduits.emplace_back("other."+port_name, "component."+port_name);
                }
            }
        }
        PeerDims peer_dims({ {"component", {}}});
        PeerLocations peer_locations({{"component", {"direct:test"}}});
        PeerInfo peer_info(component_id, {}, conduits, peer_dims, peer_locations);

        port_manager_->connect_ports(peer_info);
        validator_ = std::make_unique<MMSFValidator>(*port_manager_, *logger_);
        // Discard the debug log statement in the MMSFValidator initializer:
        logger_->caplog.call_args_list.clear();
    }
};


struct libmuscle_simple_validator : libmuscle_mmsf_validator {
    libmuscle_simple_validator() {
        create_validator(PortsDescription{
                {Operator::F_INIT, {"f_i"}},
                {Operator::O_I, {"o_i"}},
                {Operator::S, {"s"}},
                {Operator::O_F, {"o_f"}}});
    }
};


TEST_F(libmuscle_simple_validator, test_simple_correct_0it) {
    for (std::size_t i = 0; i < 5; ++i) {
        validator_->reuse_instance();
        validator_->check_receive("f_i", {});
        validator_->check_send("o_f", {});
    }
    validator_->reuse_instance();
    ASSERT_FALSE(logger_->caplog.called());
}


TEST_F(libmuscle_simple_validator, test_simple_correct_1it) {
    for (std::size_t i = 0; i < 5; ++i) {
        validator_->reuse_instance();
        validator_->check_receive("f_i", {});
        validator_->check_send("o_i", {});
        validator_->check_receive("s", {});
        validator_->check_send("o_f", {});
    }
    validator_->reuse_instance();
    ASSERT_FALSE(logger_->caplog.called());
}


TEST_F(libmuscle_simple_validator, test_simple_correct_2it) {
    for (std::size_t i = 0; i < 5; ++i) {
        validator_->reuse_instance();
        validator_->check_receive("f_i", {});
        validator_->check_send("o_i", {});
        validator_->check_receive("s", {});
        validator_->check_send("o_i", {});
        validator_->check_receive("s", {});
        validator_->check_send("o_f", {});
    }
    validator_->reuse_instance();
    ASSERT_FALSE(logger_->caplog.called());
}


TEST_F(libmuscle_simple_validator, test_simple_skip_f_init) {
    validator_->reuse_instance();
    validator_->check_send("o_i", {});
    ASSERT_TRUE(logger_->caplog.called_once());
    ASSERT_EQ(logger_->caplog.call_arg<0>(0), LogLevel::WARNING);
    ASSERT_THAT(logger_->caplog.call_arg<1>(0), HasSubstr("Send on port 'o_i'"));
}


TEST_F(libmuscle_simple_validator, test_simple_skip_o_i) {
    validator_->reuse_instance();
    validator_->check_receive("f_i", {});

    validator_->check_receive("f_i", {});
    ASSERT_TRUE(logger_->caplog.called_once());
    ASSERT_EQ(logger_->caplog.call_arg<0>(0), LogLevel::WARNING);
    ASSERT_THAT(logger_->caplog.call_arg<1>(0), HasSubstr("Receive on port 'f_i'"));

    logger_->caplog.call_args_list.clear();
    validator_->check_receive("s", {});
    ASSERT_TRUE(logger_->caplog.called_once());
    ASSERT_EQ(logger_->caplog.call_arg<0>(0), LogLevel::WARNING);
    ASSERT_THAT(logger_->caplog.call_arg<1>(0), HasSubstr("Receive on port 's'"));

    logger_->caplog.call_args_list.clear();
    validator_->reuse_instance();
    ASSERT_TRUE(logger_->caplog.called_once());
    ASSERT_EQ(logger_->caplog.call_arg<0>(0), LogLevel::WARNING);
    ASSERT_THAT(logger_->caplog.call_arg<1>(0), HasSubstr("reuse_instance()"));
}


TEST_F(libmuscle_simple_validator, test_simple_skip_s) {
    validator_->reuse_instance();
    validator_->check_receive("f_i", {});
    validator_->check_send("o_i", {});

    validator_->check_send("o_i", {});
    ASSERT_TRUE(logger_->caplog.called_once());
    ASSERT_EQ(logger_->caplog.call_arg<0>(0), LogLevel::WARNING);
    ASSERT_THAT(logger_->caplog.call_arg<1>(0), HasSubstr("Send on port 'o_i'"));

    logger_->caplog.call_args_list.clear();
    validator_->check_send("o_f", {});
    ASSERT_TRUE(logger_->caplog.called_once());
    ASSERT_EQ(logger_->caplog.call_arg<0>(0), LogLevel::WARNING);
    ASSERT_THAT(logger_->caplog.call_arg<1>(0), HasSubstr("Send on port 'o_f'"));
}


TEST_F(libmuscle_simple_validator, test_simple_skip_o_f) {
    validator_->reuse_instance();
    validator_->check_receive("f_i", {});
    validator_->check_send("o_i", {});
    validator_->check_receive("s", {});

    validator_->reuse_instance();
    ASSERT_TRUE(logger_->caplog.called_once());
    ASSERT_EQ(logger_->caplog.call_arg<0>(0), LogLevel::WARNING);
    ASSERT_THAT(logger_->caplog.call_arg<1>(0), HasSubstr("reuse_instance()"));
}

TEST_F(libmuscle_simple_validator, test_simple_skip_reuse_instance) {
    validator_->reuse_instance();
    validator_->check_receive("f_i", {});
    validator_->check_send("o_f", {});

    validator_->check_receive("f_i", {});
    ASSERT_TRUE(logger_->caplog.called_once());
    ASSERT_EQ(logger_->caplog.call_arg<0>(0), LogLevel::WARNING);
    ASSERT_THAT(logger_->caplog.call_arg<1>(0), HasSubstr("Receive on port 'f_i'"));
}


TEST_F(libmuscle_mmsf_validator, test_only_o_f) {
    create_validator(PortsDescription{{Operator::O_F, {"o_f"}}});

    for (std::size_t i = 0; i < 5; ++i) {
        validator_->reuse_instance();
        validator_->check_send("o_f", {});
    }

    validator_->check_send("o_f", {});
    ASSERT_TRUE(logger_->caplog.called_once());
    ASSERT_EQ(logger_->caplog.call_arg<0>(0), LogLevel::WARNING);
    ASSERT_THAT(logger_->caplog.call_arg<1>(0), HasSubstr("Send on port 'o_f'"));
}


TEST_F(libmuscle_mmsf_validator, test_only_f_i) {
    create_validator(PortsDescription{{Operator::F_INIT, {"f_i"}}});

    for (std::size_t i = 0; i < 5; ++i) {
        validator_->reuse_instance();
        validator_->check_receive("f_i", {});
    }

    validator_->check_receive("f_i", {});
    ASSERT_TRUE(logger_->caplog.called_once());
    ASSERT_EQ(logger_->caplog.call_arg<0>(0), LogLevel::WARNING);
    ASSERT_THAT(logger_->caplog.call_arg<1>(0), HasSubstr("Receive on port 'f_i'"));
}


TEST_F(libmuscle_mmsf_validator, test_micro) {
    create_validator(PortsDescription{
            {Operator::F_INIT, {"f_i"}},
            {Operator::O_F, {"o_f"}}});

    for (std::size_t i = 0; i < 5; ++i) {
        validator_->reuse_instance();
        validator_->check_receive("f_i", {});
        validator_->check_send("o_f", {});
    }
    validator_->reuse_instance();
    validator_->check_receive("f_i", {});

    validator_->check_receive("f_i", {});
    ASSERT_TRUE(logger_->caplog.called_once());
    ASSERT_EQ(logger_->caplog.call_arg<0>(0), LogLevel::WARNING);
    ASSERT_THAT(logger_->caplog.call_arg<1>(0), HasSubstr("Receive on port 'f_i'"));

    logger_->caplog.call_args_list.clear();
    validator_->reuse_instance();
    ASSERT_TRUE(logger_->caplog.called_once());
    ASSERT_EQ(logger_->caplog.call_arg<0>(0), LogLevel::WARNING);
    ASSERT_THAT(logger_->caplog.call_arg<1>(0), HasSubstr("reuse_instance()"));
}


TEST_F(libmuscle_mmsf_validator, test_not_all_ports_used) {
    create_validator(PortsDescription{
            {Operator::F_INIT, {"f_i1", "f_i2"}},
            {Operator::O_F, {"o_f"}}});

    validator_->reuse_instance();
    validator_->check_receive("f_i1", {});

    validator_->check_send("o_f", {});
    ASSERT_TRUE(logger_->caplog.called_once());
    ASSERT_EQ(logger_->caplog.call_arg<0>(0), LogLevel::WARNING);
    ASSERT_THAT(logger_->caplog.call_arg<1>(0), HasSubstr("Send on port 'o_f'"));
}
