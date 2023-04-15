#include "libmuscle/data.hpp"
#include "libmuscle/mcp/data_pack.hpp"
#include <libmuscle/namespace.hpp>

#include <cstddef>
#include <cstdio>
#include <iostream>
#include <ostream>

#include <malloc.h>
#include <sys/time.h>
#include <sys/resource.h>

#include <gtest/gtest.h>


using libmuscle::_MUSCLE_IMPL_NS::Data;


int main(int argc, char *argv[]) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}

TEST(libmuscle_mcp_data, large_structure) {
    // produce a large with items in it
    // regression test for excess memory usage

    // at default malloc settings, we can measure to about 128kB accuracy
    const std::size_t granularity = 128u * 1024u;

    // we want to measure to 1% accuracy
    const std::size_t data_size = granularity * 100u;

    // we set max overhead at 110%, because msgpack's allocator allocates
    // in powers of 2 so we need 100% for that, and a bit of overhead for
    // the list itself and overhead.
    const std::size_t overhead = data_size * 110 / 100;

    // data segment before allocating is about 200kB
    const std::size_t base_size = 200 * 1024;

    const std::size_t max_size = base_size + data_size + overhead;

    // tell the kernel to kill us if we're using too much memory
    struct rlimit old_limits, limits;
    getrlimit(RLIMIT_DATA, &old_limits);
    getrlimit(RLIMIT_DATA, &limits);
    limits.rlim_cur = max_size;
    setrlimit(RLIMIT_DATA, &limits);

    // This many items are  needed to reach the given data size
    // A MsgPack object is 24 bytes
    const std::size_t num_items = data_size / 24;

    malloc_info(0, stderr);

    Data list = Data::nils(num_items);
    malloc_info(0, stderr);
    for (std::size_t i = 0; i < num_items; ++i)
        list[i] = Data(42424242);

    malloc_info(0, stderr);

    // reset memory limit
    setrlimit(RLIMIT_DATA, &old_limits);
}

TEST(libmuscle_mcp_data, nested_structure) {
    // produce a large list with nested structures in it
    // regression test for excess memory usage

    // Originally reported with a 10M item list, which would try to use
    // 600GB. Scaled down here to speed things up, and we want to do at least
    // 100x better than that, so 10k items in 6MB.

    // tell the kernel to kill us if we're using too much memory
    struct rlimit old_limits, limits;
    getrlimit(RLIMIT_DATA, &old_limits);
    getrlimit(RLIMIT_DATA, &limits);
    limits.rlim_cur = 6 * 1024 * 1024;
    setrlimit(RLIMIT_DATA, &limits);

    const std::size_t num_items = 10000;
    malloc_info(0, stderr);

    Data list = Data::nils(num_items);
    malloc_info(0, stderr);
    for (std::size_t i = 0; i < num_items; ++i) {
        auto pos = Data::list(1.2, 3.4, 5.6);
        list[i] = Data::list(pos, 7.8, 2);
    }

    malloc_info(0, stderr);

    // reset memory limit
    setrlimit(RLIMIT_DATA, &old_limits);
}

