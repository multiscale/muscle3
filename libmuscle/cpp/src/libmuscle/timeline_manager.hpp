#pragma once

#include <libmuscle/data.hpp>
#include <libmuscle/namespace.hpp>
#include <libmuscle/port.hpp>
#include <libmuscle/port_manager.hpp>
#include <libmuscle/util.hpp>

#include <ymmsl/ymmsl.hpp>

#include <stdexcept>
#include <string>
#include <tuple>
#include <unordered_map>
#include <utility>
#include <vector>


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

/** A (port name, slot) pair */
using PortAndSlot = std::pair<std::string, Optional<int>>;

Data encode_port_and_slot(PortAndSlot const & port_and_slot);
PortAndSlot decode_port_and_slot(DataConstRef const & data);

Data encode_participated(std::vector<PortAndSlot> const & participated);
std::vector<PortAndSlot> decode_participated(DataConstRef const & data);

/** The iteration of a (sub-)timeline, as embedded in outgoing messages. */
using IterationCount = std::vector<int>;

Data encode_iteration(Optional<IterationCount> const & iteration);
Optional<IterationCount> decode_iteration(DataConstRef const & data);

/** A single expected next action: send or receive on the given port, and if
 * the port is a vector port, the slots that are still expected ([] for a
 * scalar port). */
using ExpectedAction = std::tuple<std::string, Port, std::vector<int>>;
using ExpectedActions = std::vector<ExpectedAction>;

/** A single sub-timeline's state, as returned by SubTimelineManager::get_state()
 * for saving in a snapshot. */
struct SubTimelineState {
    Optional<IterationCount> iteration;
    Optional<::ymmsl::Operator> first_operator;
    std::vector<PortAndSlot> send_participated;
    std::vector<PortAndSlot> receive_participated;

    Data to_data() const;
    static SubTimelineState from_data(DataConstRef const & data);
};


/** The main timeline's iteration and participation, and every sub-timeline's
 * state.
 *
 * Returned by TimelineManager::get_state() for saving in a snapshot, and
 * passed back into TimelineManager::restore_state() to resume from one.
 * iteration is unset if the main timeline has not started yet (or has been
 * reset).
 */
struct TimelineState {
    Optional<IterationCount> iteration;
    std::vector<PortAndSlot> send_participated;
    std::vector<PortAndSlot> receive_participated;
    std::unordered_map<std::string, SubTimelineState> subtimeline_states;

    Data to_data() const;
    static TimelineState from_data(DataConstRef const & data);
};


/** Base class for exceptions raised when Instance's send/receive calls
 * violate the timeline consistency rules. */
class TimelineError : public std::runtime_error {
    public:
        using std::runtime_error::runtime_error;
};


/** The given port cannot send/receive yet: other ports must send or receive
 * a message first. */
class PortBlocked : public TimelineError {
    public:
        PortBlocked(Port const & port, Optional<int> slot, ExpectedActions expected);

        std::string action;
        Port port;
        Optional<int> slot;
        ExpectedActions expected;
};


/** reuse_instance() was called before the previous reuse loop iteration
 * finished. */
class ReuseLoopIncomplete : public TimelineError {
    public:
        explicit ReuseLoopIncomplete(ExpectedActions expected);

        ExpectedActions expected;
};


/** The given port already sent/received a message this reuse loop
 * iteration. */
class AlreadyParticipated : public TimelineError {
    public:
        AlreadyParticipated(Port const & port, Optional<int> slot);

        std::string action;
        Port port;
        Optional<int> slot;
};


/** A received message doesn't belong where this component expects it.
 *
 * The timeline manager's bookkeeping should never let this state be reached.
 * Seeing this means there is probably a bug in MUSCLE3. */
class MessageOutOfSync : public TimelineError {
    public:
        MessageOutOfSync(Port const & port, Optional<int> slot);

        Port port;
        Optional<int> slot;
};


/** Tracks one direction (send or receive) of a (sub-)timeline's ports.
 *
 * Records the connected ports of that direction, how many port/slot
 * combinations they make up, and which of those have already sent or
 * received a message for the current (sub-)iteration.
 */
class TimelinePorts {
    public:
        explicit TimelinePorts(std::vector<Port> const & ports);

        /** Record that the given port/slot has participated. */
        void participate(std::string const & port_name, Optional<int> slot);

        /** Return whether the given port/slot has already participated. */
        bool has_participated(std::string const & port_name, Optional<int> slot) const;

        /** Return whether every port/slot combination has participated. */
        bool all_participated() const;

        /** Return each connected port that still has slots which haven't
         * participated yet, paired with the list of those slots ([] for a
         * scalar port). */
        std::vector<std::pair<Port, std::vector<int>>> missing_ports() const;

        /** Return every connected port together with all of its slots ([]
         * for a scalar port), regardless of participation. */
        std::vector<std::pair<Port, std::vector<int>>> all_ports() const;

        /** Clear participation, keeping the tracked ports. */
        void reset();

        std::vector<Port> ports;
        std::size_t num_slots;
        std::vector<PortAndSlot> participated;
};


/** Tracks iteration state for a single sub-timeline. */
class SubTimelineManager {
    public:
        /** Create a SubTimelineManager.
         *
         * @param timeline The timeline this manager tracks.
         * @param port_manager The port manager; used to look up the O_I and S
         *      ports belonging to this sub-timeline.
         */
        SubTimelineManager(
                ::ymmsl::Timeline const & timeline, PortManager const & port_manager);

        /** Return whether this sub-timeline is done with this reuse loop
         * iteration.
         *
         * If it was used this reuse loop iteration, every one of its ports
         * must have participated. If it wasn't used this reuse loop
         * iteration, that's fine: a sub-timeline may be skipped entirely.
         */
        bool is_complete() const;

        /** Check and update this sub-timeline's iteration state before
         * sending.
         *
         * @param port The O_I port that is about to send.
         * @param slot The slot being sent on, if this is a vector port.
         * @param parent_iteration The main timeline's current iteration.
         *
         * @return The sub-timeline iteration.
         */
        IterationCount check_send_message(
                Port const & port, Optional<int> slot,
                IterationCount const & parent_iteration);

        /** Check that receiving on the given S port is currently allowed.
         *
         * @param port The S port that is about to receive.
         * @param slot The slot being received on, if this is a vector port.
         */
        void check_receive(Port const & port, Optional<int> slot);

        /** Record that a message has been received on the given S port.
         *
         * @param port The S port a message was received on.
         * @param slot The slot the message was received on, if this is a
         *      vector port.
         * @param iteration The iteration the received message was sent with.
         */
        void record_received_message(
                Port const & port, Optional<int> slot, IterationCount const & iteration);

        /** Reset this sub-timeline once the main timeline's reuse loop
         * iteration completes. */
        void reset();

        /** Return this sub-timeline's state, for saving in a snapshot. */
        SubTimelineState get_state() const;

        /** Restore this sub-timeline's state from a snapshot, for snapshot
         * resume. */
        void restore_state(SubTimelineState const & state);

        /** Append the send and receive actions this sub-timeline is still missing
         * this reuse loop iteration to result, for use in blocked-port error
         * messages. */
        void missing_actions(ExpectedActions & result) const;

    private:
        ::ymmsl::Timeline timeline_;
        Optional<IterationCount> iteration_;
        Optional<::ymmsl::Operator> first_operator_;
        TimelinePorts send_;
        TimelinePorts receive_;
};


/** Tracks the main timeline's iteration and participation, and manages its
 * sub-timelines.
 *
 * O_F and F_INIT ports live on the main timeline, tracked directly by this
 * manager. O_I and S ports live on sub-timelines, each tracked by its own
 * SubTimelineManager, grouped by the port's timeline attribute.
 *
 * Every TimelineManager and SubTimelineManager records, for each of its
 * ports, whether that port has already sent or received a message for the
 * current iteration, as a set of (port name, slot) pairs, split by
 * direction: one set for the ports that send (O_F or O_I) and one for the
 * ports that receive (F_INIT or S).
 */
#ifdef LIBMUSCLE_MOCK_TIMELINE_MANAGER
#include LIBMUSCLE_MOCK_TIMELINE_MANAGER
#else

class TimelineManager {
    public:
        /** Create a TimelineManager.
         *
         * The port_manager must already have its ports connected to their
         * peers, since this collects the main-timeline (F_INIT and O_F)
         * ports with its SubTimelineManagers, and starts the main timeline
         * at [] right away if it has no F_INIT message to wait for.
         *
         * @param port_manager The (already connected) port manager for this
         *      instance.
         */
        explicit TimelineManager(PortManager const & port_manager);

        /** Check and update the timeline state before sending on the given
         * port.
         *
         * By the time a send is possible, Instance has already received a
         * message on every F_INIT port for the current iteration, so this
         * delegates straight to the specific checks for the O_F or O_I port
         * and returns the iteration of its timeline.
         *
         * @param port_name Name of the O_F or O_I port that is about to send.
         * @param slot The slot being sent on, if this is a vector port.
         *
         * @return The iteration to embed in the outgoing message.
         */
        IterationCount check_send_message(
                std::string const & port_name, Optional<int> slot = {});

        /** Check that receiving on the given port is currently allowed.
         *
         * An F_INIT port may receive once after the reuse loop starts and
         * before any other ports are used. Whether an S port may receive is
         * delegated to the corresponding SubTimelineManager.
         *
         * @param port_name Name of the F_INIT or S port about to receive.
         * @param slot The slot being received on, if this is a vector port.
         */
        void check_receive(std::string const & port_name, Optional<int> slot = {});

        /** Record that a message has been received on the given port.
         *
         * check_receive already established that this receive is allowed.
         *
         * @param port_name Name of the F_INIT or S port a message was
         *      received on.
         * @param slot The slot the message was received on, if this is a
         *      vector port.
         * @param iteration The iteration the received message was sent with.
         */
        void record_received_message(
                std::string const & port_name, Optional<int> slot,
                IterationCount const & iteration);

        /** Reset the main timeline and its sub-timelines.
         *
         * Clears the main timeline's iteration (back to [] if there are no
         * connected F_INIT ports to wait for) and participation state, and
         * resets every sub-timeline in turn.
         */
        void reset();

        /** Check if the current reuse loop iteration has finished and reset
         * for the next one.
         *
         * The reuse loop iteration is complete once every main-timeline port
         * has participated and every sub-timeline has either completed a
         * sub-iteration or wasn't used at all this reuse loop iteration.
         */
        void finish_reuse_iteration();

        /** Return the main timeline's iteration and participation, and every
         * sub-timeline's state, for saving in a snapshot. */
        TimelineState get_state() const;

        /** Restore the main timeline and every sub-timeline, for snapshot
         * resume.
         *
         * @param state The saved timeline state, as returned by get_state().
         */
        void restore_state(TimelineState const & state);

    private:
        IterationCount check_send_o_f_(Port const & port, Optional<int> slot);

        PortManager const & port_manager_;
        TimelinePorts receive_;
        TimelinePorts send_;
        std::unordered_map<::ymmsl::Timeline, SubTimelineManager> submanagers_;
        Optional<IterationCount> iteration_;
};

#endif

} }
