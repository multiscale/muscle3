#pragma once

#include "libmuscle/namespace.hpp"

#include <condition_variable>
#include <memory>
#include <mutex>
#include <tuple>
#include <vector>


namespace libmuscle { namespace _MUSCLE_IMPL_NS { namespace mcp {

/** Tracks the state of an RPC session
 *
 * This keeps track of whether and which response has been received, and whether a
 * response is available for it. This information is used to coordinate between
 * different connections (possibly serviced by different threads) for the same session.
 * See the Python version for a full explanation of the algorithm.
 */
class RpcState {
    public:
        /** Create an RpcState object.
         *
         * The first request will be 1, so we initialise to a state in which request 0
         * has seemingly been processed already and we're ready to do number 1 next.
         */
        RpcState();

        /** Decide what to do about an incoming request.
         *
         * Possible answers are: process and send, send only, or do nothing. See the
         * Python version for a full explanation of the algorithm.
         *
         * @param request_nr Number of the received request
         * @return A tuple (should_process, should_send) that determines whether to call
         *      the handler for this request, and/or whether to send the response.
         */
        std::tuple<bool, bool> triage_request(int64_t request_nr);

        /** Set the response and notify that we're done.
         *
         * This sets the response and notifies any threads waiting in
         * wait_get_response() that one is available.
         *
         * @param response A newly generated response
         */
        void set_response(std::shared_ptr<std::vector<char>> response);

        /** Return the given response, if available.
         *
         * @return The response for the current request, or null if it's not yet
         * available.
         */
        std::shared_ptr<std::vector<char>> get_response();

    private:
        // Protects cur_request_ and response_ (but not what it points to)
        std::mutex mutex_;

        int64_t cur_request_;
        std::shared_ptr<std::vector<char>> response_;
};


} } }

