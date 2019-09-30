#include <libmuscle/message.hpp>


using ymmsl::Settings;


namespace libmuscle {

Message::Message(
        double timestamp,
        DataConstRef const & data)
    : timestamp_(timestamp)
    , next_timestamp_()
    , data_(data)
    , settings_()
{}

Message::Message(
        double timestamp,
        double next_timestamp,
        DataConstRef const & data)
    : timestamp_(timestamp)
    , next_timestamp_(next_timestamp)
    , data_(data)
    , settings_()
{}

Message::Message(
        double timestamp,
        DataConstRef const & data,
        Settings const & settings)
    : timestamp_(timestamp)
    , next_timestamp_()
    , data_(data)
    , settings_(settings)
{}

Message::Message(
        double timestamp,
        double next_timestamp,
        DataConstRef const & data,
        Settings const & settings)
    : timestamp_(timestamp)
    , next_timestamp_(next_timestamp)
    , data_(data)
    , settings_(settings)
{}

Message::Message(Message const & message)
    : timestamp_(message.timestamp_)
    , next_timestamp_(message.next_timestamp_)
    , settings_(message.settings_)
{
    data_.reseat(message.data_);
}

Message::Message(Message && message)
    : timestamp_(message.timestamp_)
    , next_timestamp_(message.next_timestamp_)
    , settings_(std::move(message.settings_))
{
    data_.reseat(std::move(message.data_));
}

Message & Message::operator=(Message const & message) {
    timestamp_ = message.timestamp_;
    next_timestamp_ = message.next_timestamp_;
    data_.reseat(message.data_);
    settings_ = message.settings_;
    return *this;
}

Message & Message::operator=(Message && message) {
    timestamp_ = message.timestamp_;
    next_timestamp_ = message.next_timestamp_;
    data_.reseat(std::move(message.data_));
    settings_ = std::move(message.settings_);
    return *this;
}

double Message::timestamp() const {
    return timestamp_;
}

void Message::set_timestamp(double timestamp) {
    timestamp_ = timestamp;
}

bool Message::has_next_timestamp() const {
    return next_timestamp_.is_set();
}

double Message::next_timestamp() const {
    return next_timestamp_.get();
}

void Message::set_next_timestamp(double next_timestamp) {
    next_timestamp_ = next_timestamp;
}

void Message::unset_next_timestamp() {
    next_timestamp_ = {};
}

DataConstRef const & Message::data() const {
    return data_;
}

void Message::set_data(DataConstRef const & data) {
    data_.reseat(data);
}

bool Message::has_settings() const {
    return settings_.is_set();
}

Settings const & Message::settings() const {
    return settings_.get();
}

void Message::set_settings(::ymmsl::Settings const & settings) {
    settings_ = settings;
}

void Message::unset_settings() {
    settings_ = {};
}

}

