#include <libmuscle/milestone.hpp>

#include <msgpack.hpp>

#include <libmuscle/mcp/data_pack.hpp>
#include <libmuscle/mcp/ext_types.hpp>


using libmuscle::_MUSCLE_IMPL_NS::mcp::ExtTypeId;


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

Milestone::Milestone(IterationCount const & iteration)
    :  DataConstRef(static_cast<char>(ExtTypeId::milestone), encode_iteration(iteration))
{}


Milestone::Milestone(DataConstRef const & data)
    :  DataConstRef(data)
{
    if (!is_milestone(*this))
        throw std::runtime_error("Internal error: converting non-milestone data to milestone");
}

IterationCount Milestone::iteration() const {
    return decode_iteration(iteration_list_()).get();
}

bool Milestone::is_final_milestone() const {
    return iteration_list_().size() == 0;
}

Milestone::operator std::string() const {
    std::ostringstream oss;
    oss << "Milestone([";
    bool first = true;
    for (auto &i : iteration()) {
        if (!first) oss << ", ";
        first = false;
        oss << i;
    }
    oss << "])";
    return oss.str();
}

DataConstRef Milestone::iteration_list_() const {
    auto ext = mp_obj_->as<msgpack::type::ext>();
    auto oh = msgpack::unpack(ext.data(), ext.size());

    if (oh.get().type != msgpack::type::ARRAY)
        throw std::runtime_error("Invalid milestone format. Bug in MUSCLE3?");

    if (!obj_cache_)
        obj_cache_ = std::make_shared<DataConstRef>(
                mcp::unpack_data(mp_zones_->at(0), ext.data(), ext.size()));

    return *obj_cache_;
}

bool is_milestone(DataConstRef const & data) {
    return (data.mp_obj_->type == msgpack::type::EXT &&
            data.mp_obj_->via.ext.type() ==
                static_cast<int8_t>(ExtTypeId::milestone));
}

} }

