#include <stdexcept>
#include <sstream>
#include <unordered_map>

#include <gtest/gtest.h>

#include "ymmsl/identity.hpp"


using ymmsl::Identifier;
using ymmsl::Reference;
using std::unordered_map;


TEST(ymmsl_identity, test_create_identifier) {
    ASSERT_NO_THROW(Identifier("testing"));
    ASSERT_NO_THROW(Identifier("CapiTaLs"));
    ASSERT_NO_THROW(Identifier("under_score"));
    ASSERT_NO_THROW(Identifier("_underscore"));
    ASSERT_NO_THROW(Identifier("digits123"));

    ASSERT_THROW(Identifier(""), std::invalid_argument);
    ASSERT_THROW(Identifier("1initialdigit"), std::invalid_argument);
    ASSERT_THROW(Identifier("test.period"), std::invalid_argument);
    ASSERT_THROW(Identifier("test-hyphen"), std::invalid_argument);
    ASSERT_THROW(Identifier("test space"), std::invalid_argument);
    ASSERT_THROW(Identifier("test/slash"), std::invalid_argument);
}

TEST(ymmsl_identity, test_compare_identifier) {
    ASSERT_EQ(Identifier("test"), Identifier("test"));
    ASSERT_NE(Identifier("test1"), Identifier("test2"));

    ASSERT_EQ(Identifier("test"), "test");
    ASSERT_EQ("test", Identifier("test"));
    ASSERT_NE(Identifier("test"), "test2");
    ASSERT_NE("test2", Identifier("test"));
}

TEST(ymmsl_identity, test_concatenate_with_string) {
    ASSERT_EQ(Identifier("test") + std::string("test"), "testtest");
    ASSERT_EQ(std::string("test") + Identifier("test"), "testtest");
    ASSERT_EQ(Identifier("test") + "test", "testtest");
    ASSERT_EQ("test" + Identifier("test"), "testtest");
}


TEST(ymmsl_identity, test_identifier_map_key) {
    auto test_map = unordered_map<Identifier, int>{{Identifier("test"), 1}};
    ASSERT_EQ(test_map[Identifier("test")], 1);
}

TEST(ymmsl_identity, test_create_reference) {
    auto test_ref = Reference("_testing");
    ASSERT_EQ(static_cast<std::string>(test_ref), "_testing");
    ASSERT_EQ(test_ref.length(), 1u);
    ASSERT_TRUE(test_ref[0].is_identifier());
    ASSERT_EQ(static_cast<std::string>(test_ref[0].identifier()), "_testing");

    ASSERT_THROW(Reference("1test"), std::invalid_argument);

    test_ref = Reference("test.testing");
    ASSERT_EQ(test_ref.length(), 2u);
    ASSERT_TRUE(test_ref[0].is_identifier());
    ASSERT_EQ(static_cast<std::string>(test_ref[0].identifier()), "test");
    ASSERT_TRUE(test_ref[1].is_identifier());
    ASSERT_EQ(static_cast<std::string>(test_ref[1].identifier()), "testing");
    ASSERT_EQ(static_cast<std::string>(test_ref), "test.testing");

    test_ref = Reference("test[12]");
    ASSERT_EQ(test_ref.length(), 2u);
    ASSERT_TRUE(test_ref[0].is_identifier());
    ASSERT_EQ(static_cast<std::string>(test_ref[0].identifier()), "test");
    ASSERT_TRUE(test_ref[1].is_index());
    ASSERT_EQ(test_ref[1].index(), 12);
    ASSERT_EQ(static_cast<std::string>(test_ref), "test[12]");

    test_ref = Reference("test[12].testing.ok.index[3][5]");
    ASSERT_EQ(test_ref.length(), 7u);
    ASSERT_TRUE(test_ref[0].is_identifier());
    ASSERT_EQ(static_cast<std::string>(test_ref[0].identifier()), "test");
    ASSERT_TRUE(test_ref[1].is_index());
    ASSERT_EQ(test_ref[1].index(), 12);
    ASSERT_TRUE(test_ref[2].is_identifier());
    ASSERT_EQ(static_cast<std::string>(test_ref[2].identifier()), "testing");
    ASSERT_TRUE(test_ref[3].is_identifier());
    ASSERT_EQ(static_cast<std::string>(test_ref[3].identifier()), "ok");
    ASSERT_TRUE(test_ref[4].is_identifier());
    ASSERT_EQ(static_cast<std::string>(test_ref[4].identifier()), "index");
    ASSERT_TRUE(test_ref[5].is_index());
    ASSERT_EQ(test_ref[5].index(), 3);
    ASSERT_TRUE(test_ref[6].is_index());
    ASSERT_EQ(test_ref[6].index(), 5);
    ASSERT_EQ(static_cast<std::string>(test_ref), "test[12].testing.ok.index[3][5]");

    ASSERT_THROW(Reference("ua\",.u8["), std::invalid_argument);
    ASSERT_THROW(Reference("test[4"), std::invalid_argument);
    ASSERT_THROW(Reference("test4]"), std::invalid_argument);
    ASSERT_THROW(Reference("test[_t]"), std::invalid_argument);
    ASSERT_THROW(Reference("testing_{3}"), std::invalid_argument);
    ASSERT_THROW(Reference("test.(x)"), std::invalid_argument);
    ASSERT_THROW(Reference("[3]test"), std::invalid_argument);
    ASSERT_THROW(Reference("[4].test"), std::invalid_argument);
}

TEST(ymmsl_identity, test_reference_slicing) {
    auto test_ref = Reference("test[12].testing.ok.index[3][5]");

    ASSERT_EQ(test_ref[0].identifier(), "test");
    ASSERT_EQ(test_ref[1].index(), 12);
    ASSERT_EQ(test_ref[3].identifier(), "ok");
}

TEST(ymmsl_identity, test_reference_map_key) {
    auto test_map = unordered_map<Reference, int>{{Reference("test[4]"), 1}};
    ASSERT_EQ(test_map[Reference("test[4]")], 1);
}

TEST(ymmsl_identity, test_reference_equivalence) {
    ASSERT_EQ(Reference("test.test[3]"), Reference("test.test[3]"));
    ASSERT_NE(Reference("test.test[3]"), Reference("test1.test[3]"));

    ASSERT_EQ(Reference("test.test[3]"), std::string("test.test[3]"));
    ASSERT_NE(Reference("test.test[3]"), std::string("test1.test[3]"));

    ASSERT_EQ(Reference("test.test[3]"), "test.test[3]");
    ASSERT_NE(Reference("test.test[3]"), "test1.test[3]");

    ASSERT_EQ(std::string("test.test[3]"), Reference("test.test[3]"));
    ASSERT_NE(std::string("test1.test[3]"), Reference("test.test[3]"));

    ASSERT_EQ("test.test[3]", Reference("test.test[3]"));
    ASSERT_NE("test1.test[3]", Reference("test.test[3]"));
}

TEST(ymmsl_identity, test_reference_concatenation) {
    ASSERT_EQ(Reference("test") + Reference("test2"), "test.test2");
    ASSERT_EQ(Reference("test") + Identifier("test2"), "test.test2");
    ASSERT_EQ(Reference("test") + 5, "test[5]");

    ASSERT_EQ(Reference("test[5]") + Reference("test2[3]"), "test[5].test2[3]");
    ASSERT_EQ(Reference("test[5]") + Identifier("test2"), "test[5].test2");
    ASSERT_EQ(Reference("test[5]") + 3, "test[5][3]");
}

TEST(ymmsl_identity, identifier_serialisation) {
    std::ostringstream oss;

    oss << Identifier("testing");
    ASSERT_EQ(oss.str(), "testing");
}

