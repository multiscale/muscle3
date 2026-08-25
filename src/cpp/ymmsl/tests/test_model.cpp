#include <gtest/gtest.h>

#include <ymmsl/model.hpp>

#include <ymmsl/identity.hpp>


using ymmsl::impl::Conduit;
using ymmsl::impl::ConduitFilter;
using ymmsl::impl::Identifier;
using ymmsl::impl::ReferencePart;


TEST(ymmsl_model, conduit) {
    Conduit test_conduit("submodel1.port1", "submodel2.port2");
    ASSERT_EQ(test_conduit.sender[0], Identifier("submodel1"));
    ASSERT_EQ(test_conduit.sender[1], Identifier("port1"));
    ASSERT_EQ(test_conduit.receiver[0], Identifier("submodel2"));
    ASSERT_EQ(test_conduit.receiver[1], Identifier("port2"));

    ASSERT_EQ(test_conduit.sending_component(), Identifier("submodel1"));
    ASSERT_EQ(test_conduit.sending_port(), Identifier("port1"));
    ASSERT_TRUE(test_conduit.sending_slot().empty());
    ASSERT_EQ(test_conduit.receiving_component(), Identifier("submodel2"));
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
    ASSERT_EQ(test_conduit3.sending_component(), Identifier("x"));
    ASSERT_EQ(test_conduit3.sending_port(), Identifier("y"));
    ASSERT_EQ(test_conduit3.sending_slot(), (std::vector<int>{1, 2}));
    ASSERT_EQ(test_conduit3.receiver[2], ReferencePart(3));
    ASSERT_EQ(test_conduit3.receiving_component(), Identifier("a"));
    ASSERT_EQ(test_conduit3.receiving_port(), Identifier("b"));
    ASSERT_EQ(test_conduit3.receiving_slot(), std::vector<int>{3});

    Conduit test_conduit4("a.b", "b.c", "last repeat pad");
    ASSERT_EQ(test_conduit4.filters.size(), 3);
    ASSERT_EQ(test_conduit4.filters[0], ConduitFilter::LAST);
    ASSERT_EQ(test_conduit4.filters[1], ConduitFilter::REPEAT);
    ASSERT_EQ(test_conduit4.filters[2], ConduitFilter::PAD);
    ASSERT_EQ(std::string(test_conduit4), "Conduit(a.b -> last repeat pad -> b.c)");

    ASSERT_TRUE(is_repeater(ConduitFilter::REPEAT));
    ASSERT_TRUE(is_repeater(ConduitFilter::PAD));
    ASSERT_FALSE(is_repeater(ConduitFilter::LAST));

    ASSERT_FALSE(is_reducer(ConduitFilter::REPEAT));
    ASSERT_FALSE(is_reducer(ConduitFilter::PAD));
    ASSERT_TRUE(is_reducer(ConduitFilter::LAST));
}

