#pragma once

#ifdef LIBMUSCLE_MOCK_PROFILER
#include LIBMUSCLE_MOCK_PROFILER
#else


#include <libmuscle/mmp_client.hpp>
#include <libmuscle/profiling.hpp>
#include <libmuscle/timestamp.hpp>


namespace libmuscle { namespace impl {

/** Collects profiling events and sends them to the manager.
 */
class Profiler {
    public:
        /** Create a Profiler.
         *
         * @param manager The client used to submit data to the manager.
         */
        Profiler(MMPClient & manager);

        /** Shut down the profiler.
         *
         * This flushes any remaining data to the manager.
         */
        void shutdown();

        /** Record a profiling event.
         *
         * This will record the event, and may flush this and previously
         * recorded events to the manager. If the time is still running,
         * it will be stopped. Other than this the event must be complete
         * when it is submitted. Allocate an event on the stack, then move
         * it into this member function. Do not use the event object after
         * calling this function with it.
         *
         * @param event The event to record.
         */
        void record_event(ProfileEvent && event);

    private:
        friend class TestProfiler;

        MMPClient & manager_;
        std::vector<ProfileEvent> events_;

        void flush_();
};

} }

#endif

