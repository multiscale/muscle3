#include "libmuscle/mcp/rpc_state.hpp"

#include <memory>
#include <tuple>
#include <vector>


namespace libmuscle { namespace _MUSCLE_IMPL_NS { namespace mcp {

RpcState::RpcState()
    : cur_request_(0)
    , response_(std::make_shared<std::vector<char>>())
{}

std::tuple<bool, bool> RpcState::triage_request(int64_t request_nr) {
    const std::lock_guard<std::mutex> lock(mutex_);
    bool should_process = response_ && cur_request_ < request_nr;
    if (should_process) {
        cur_request_ = request_nr;
        response_.reset();
    }

    bool should_send = cur_request_ == request_nr;

    return std::make_tuple(should_process, should_send);
}

void RpcState::set_response(std::shared_ptr<std::vector<char>> response) {
    const std::lock_guard<std::mutex> lock(mutex_);
    response_ = response;
}

std::shared_ptr<std::vector<char>> RpcState::get_response() {
    const std::lock_guard<std::mutex> lock(mutex_);
    return response_;
}

} } }

