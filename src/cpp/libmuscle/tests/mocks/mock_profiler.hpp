#pragma once

#include <libmuscle/profiling.hpp>
#include <libmuscle/mmp_client.hpp>
#include <libmuscle/namespace.hpp>
#include <mocks/mock_support.hpp>

#include <string>


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

class MockProfiler : public MockClass<MockProfiler> {
    public:
        MockProfiler(ReturnValue) {
            NAME_MOCK_MEM_FUN(MockProfiler, constructor);
            NAME_MOCK_MEM_FUN(MockProfiler, shutdown);
            NAME_MOCK_MEM_FUN(MockProfiler, set_level);
            NAME_MOCK_MEM_FUN(MockProfiler, record_event);
        }

        MockProfiler() {
            init_from_return_value();
        }

        MockProfiler(MMPClient & manager) {
            init_from_return_value();
            constructor(manager);
        }

        MockFun<Void, Obj<MMPClient &>> constructor;

        MockFun<Void> shutdown;

        MockFun<Void, Val<std::string const &>> set_level;

        MockFun<Void, Val<ProfileEvent &&>> record_event;
};

using Profiler = MockProfiler;

} }

