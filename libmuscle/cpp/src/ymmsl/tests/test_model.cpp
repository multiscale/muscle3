#include <gtest/gtest.h>

#include "ymmsl/model.hpp"

#include "ymmsl/identity.hpp"


using ymmsl::Conduit;
using ymmsl::Identifier;
using ymmsl::ReferencePart;


TEST(ymmsl_model, conduit) {
    Conduit test_conduit("submodel1.port1", "submodel2.port2");
    ASSERT_EQ(test_conduit.sender[0], Identifier("submodel1"));
    ASSERT_EQ(test_conduit.sender[1], Identifier("port1"));
    ASSERT_EQ(test_conduit.receiver[0], Identifier("submodel2"));
    ASSERT_EQ(test_conduit.receiver[1], Identifier("port2"));

    ASSERT_EQ(test_conduit.sending_compute_element(), Identifier("submodel1"));
    ASSERT_EQ(test_conduit.sending_port(), Identifier("port1"));
    ASSERT_TRUE(test_conduit.sending_slot().empty());
    ASSERT_EQ(test_conduit.receiving_compute_element(), Identifier("submodel2"));
    ASSERT_EQ(test_conduit.receiving_port(), Identifier("port2"));
    ASSERT_TRUE(test_conduit.receiving_slot().empty());

    ASSERT_THROW(Conduit("x", "submodel1.port1"), std::runtime_error);
    ASSERT_THROW(Conduit("x[3].y.z", "submodel1.port1"), std::runtime_error);
    ASSERT_THROW(Conduit("x[3]", "submodel1.port1"), std::runtime_error);

    Conduit test_conduit2("submodel1.port1", "submodel2.port2");
    ASSERT_EQ(test_conduit, test_conduit2);

    std::string str(test_conduit);
    ASSERT_NE(str.find("Conduit"), str.npos);
    ASSERT_NE(str.find("submodel1.port1"), str.npos);
    ASSERT_NE(str.find("submodel2.port2"), str.npos);

    Conduit test_conduit3("x.y[1][2]", "a.b[3]");
    ASSERT_EQ(test_conduit3.sender[2], ReferencePart(1));
    ASSERT_EQ(test_conduit3.sender[3], ReferencePart(2));
    ASSERT_EQ(test_conduit3.sending_compute_element(), Identifier("x"));
    ASSERT_EQ(test_conduit3.sending_port(), Identifier("y"));
    ASSERT_EQ(test_conduit3.sending_slot(), (std::vector<int>{1, 2}));
    ASSERT_EQ(test_conduit3.receiver[2], ReferencePart(3));
    ASSERT_EQ(test_conduit3.receiving_compute_element(), Identifier("a"));
    ASSERT_EQ(test_conduit3.receiving_port(), Identifier("b"));
    ASSERT_EQ(test_conduit3.receiving_slot(), std::vector<int>{3});
}

