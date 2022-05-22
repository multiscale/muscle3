#pragma once

namespace libmuscle { namespace impl {

/** Request type for MMP requests
 *
 * Needs to be kept in sync with the corresponding definition on the Python
 * side, including the numerical values. See there for an explanation.
 */
enum class RequestType {
    // MUSCLE Manager Protocol
    register_instance = 1,
    get_peers = 2,
    deregister_instance = 3,
    get_settings = 4,
    submit_log_message = 5,
    submit_profile_events = 6,

    // MUSCLE Peer Protocol
    get_next_message = 21
};


/** Response type for MMP responses
 *
 * Needs to be kept in sync with the corresponding definition on the Python
 * side, including the numerical values. See there for an explanation.
 */
enum class ResponseType {
    success = 0,
    error = 1,
    pending = 2
};


} }

