#pragma once

/* Helper variable types for mocks dealing with encoded MPP messages.
 * Used by MockPostOffice and MockMPPServer.
 */

namespace mock_encoded_message {

using ::libmuscle::_MUSCLE_IMPL_NS::MPPMessage;

struct EncodedMessage {
    using ArgType = std::vector<char> &&;
    using StorageType = std::shared_ptr<MPPMessage>;

    static StorageType arg_to_store(ArgType const & message) {
        return std::make_shared<MPPMessage>(MPPMessage::from_bytes(message));
    }
};

struct EncodedMessageRet {
    using ArgType = std::vector<char>;
    using StorageType = std::shared_ptr<MPPMessage>;

    static StorageType arg_to_store(ArgType const & message) {
        return std::make_shared<MPPMessage>(MPPMessage::from_bytes(message));
    }

    static ArgType store_to_arg(StorageType const & stored) {
        return stored->encoded();
    }
};

struct EncodedMessageOut {
    using ArgType = std::vector<char> &;
    using StorageType = std::vector<char> *;

    static StorageType arg_to_store(ArgType const & buffer) {
        return &buffer;
    }
};

}

