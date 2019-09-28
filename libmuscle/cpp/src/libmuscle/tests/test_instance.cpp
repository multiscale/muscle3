// Inject mocks
#define LIBMUSCLE_MOCK_COMMUNICATOR <mocks/mock_communicator.hpp>
#define LIBMUSCLE_MOCK_MMP_CLIENT <mocks/mock_mmp_client.hpp>

// into the real implementation,
#include <ymmsl/compute_element.cpp>
#include <ymmsl/identity.cpp>
#include <ymmsl/settings.cpp>

#include <libmuscle/data.cpp>
#include <libmuscle/instance.cpp>
#include <libmuscle/mcp/data_pack.cpp>
#include <libmuscle/message.cpp>
#include <libmuscle/port.cpp>
#include <libmuscle/settings_manager.cpp>

// then add mock implementations as needed.
#include <mocks/mock_communicator.cpp>
#include <mocks/mock_mmp_client.cpp>


// Test code dependencies
#include <memory>
#include <stdexcept>

#include <gtest/gtest.h>

#include <libmuscle/instance.hpp>
#include <libmuscle/settings_manager.hpp>
#include <mocks/mock_communicator.hpp>

using libmuscle::Instance;
using libmuscle::MockCommunicator;
using libmuscle::MockMMPClient;

using ymmsl::Reference;


int main(int argc, char *argv[]) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}


// Helpers for accessing internal state
namespace libmuscle {

struct TestInstance {
    static Reference & instance_name_(Instance & instance) {
        return instance.instance_name_;
    }

    static SettingsManager & settings_manager_(Instance & instance) {
        return instance.settings_manager_;
    }
};

}

using libmuscle::TestInstance;

/* Mocks have internal state, which needs to be reset before each test. This
 * means that the tests are not reentrant, and cannot be run in parallel.
 * It's all fast enough, so that's not a problem.
 */
void reset_mocks() {
    MockCommunicator::reset();
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
    Instance instance(argv.size(), argv.data());

    ASSERT_EQ(TestInstance::instance_name_(instance), "test_instance[13][42]");
    ASSERT_EQ(MockMMPClient::num_constructed, 1);
    ASSERT_EQ(MockMMPClient::last_location, "node042:9000");
}

