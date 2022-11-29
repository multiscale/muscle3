#include <libmuscle/profiling.hpp>

#include <libmuscle/timestamp.hpp>


using ymmsl::Port;


namespace libmuscle { namespace impl {

ProfileEvent::ProfileEvent(
        ProfileEventType event_type,
        Optional<Timestamp> start_time,
        Optional<Timestamp> stop_time,
        Optional<Port> const & port,
        Optional<int> port_length,
        Optional<int> slot,
        Optional<std::size_t> message_size,
        Optional<double> message_timestamp)
    : event_type(event_type)
    , start_time(start_time)
    , stop_time(stop_time)
    , port(port)
    , port_length(port_length)
    , slot(slot)
    , message_size(message_size)
    , message_timestamp(message_timestamp)
{}

void ProfileEvent::start() {
    start_time = Timestamp();
}

void ProfileEvent::stop() {
    stop_time = Timestamp();
}

} }


