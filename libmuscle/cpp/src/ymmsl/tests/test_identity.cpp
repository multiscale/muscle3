#include <stdexcept>
#include <sstream>

#include <gtest/gtest.h>

#include "ymmsl/identity.hpp"


using ymmsl::Identifier;


TEST(ymmsl_identity, valid_identifier_creation) {
    ASSERT_NO_THROW(Identifier("testing"));
    ASSERT_NO_THROW(Identifier("test_ing"));
    ASSERT_NO_THROW(Identifier("_testing"));
    ASSERT_NO_THROW(Identifier("TeSTing0129azAZ"));
}

TEST(ymmsl_identity, invalid_identifier_creation) {
    ASSERT_THROW(Identifier("#$#%"), std::invalid_argument);
    ASSERT_THROW(Identifier("0abcd"), std::invalid_argument);
    ASSERT_THROW(Identifier(""), std::invalid_argument);
}

TEST(ymmsl_identity, identifier_serialisation) {
    std::ostringstream oss;

    oss << Identifier("testing");
    ASSERT_EQ(oss.str(), "testing");
}

