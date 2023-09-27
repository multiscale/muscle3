#pragma once

#ifdef LIBMUSCLE_MOCK_PROFILER
#include LIBMUSCLE_MOCK_PROFILER
#else


#include <libmuscle/mmp_client.hpp>
#include <libmuscle/namespace.hpp>
#include <libmuscle/profiling.hpp>
#include <libmuscle/timestamp.hpp>

#include <condition_variable>
#include <mutex>
#include <string>
#include <thread>


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

/** Collects profiling events and sends them to the manager.
 */
class Profiler {
    public:
        /** Create a Profiler.
         *
         * @param manager The client used to submit data to the manager.
         */
        Profiler(MMPClient & manager);

        Profiler(Profiler const &) = delete;

        /// Destruct the Profiler.
        ~Profiler();

        Profiler & operator=(Profiler const &) = delete;

        /** Shut down the profiler.
         *
         * This flushes any remaining data to the manager.
         */
        void shutdown();

        /** Set the detail level at which data is collected.
         *
         * @param level Either "none" or "all" to disable or enable sending
         *      events to the manager.
         */
        void set_level(std::string const & level);

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

        // mutex_ protects all member variables and flush_()
        std::mutex mutex_;

        MMPClient & manager_;
        bool enabled_;
        std::vector<ProfileEvent> events_;
        std::chrono::steady_clock::time_point next_send_;

        bool done_;
        std::condition_variable done_cv_;
        std::thread thread_;

        /* Background thread that ensures regular communication.
         *
         * This runs in the background, and periodically sends events to
         * the manager to ensure the manager is kept up to date even if no
         * new events are generated for a while.
         */
        static void communicate_(Profiler * self);

        // Helper, call only with mutex_ held!
        void flush_();

        // Stops the background thread and waits until it's gone
        void stop_thread_();
};

} }

#endif

