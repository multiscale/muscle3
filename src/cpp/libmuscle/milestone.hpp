#pragma once

#include <libmuscle/data.hpp>
#include <libmuscle/namespace.hpp>
#include <libmuscle/timeline_manager.hpp>


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

/** Represents a Milestone message.
 *
 * We need to be able to send a Milestone message just like we send user data
 * and settings. Adding support for it to the Data class would expose it to
 * the user, while it's an internal sentinel object. We could also go full-OO
 * and create interfaces for external, internal and read-only use of the Data
 * class, add some factories, teach users about shared pointers, and so on,
 * but I'm not sure it would make anyone's life easier either. So we'll go with
 * this, it's a bit ugly, but it works.
 */
class Milestone : public DataConstRef {
    public:
        /** Create a Milestone object with given iteration.
         */
        Milestone(IterationCount const & iteration);
        /** Create a Milestone from received Data
         */
        Milestone(DataConstRef const & data);

        /** IterationCount of the milestone.
         */
        IterationCount iteration() const;

        /** Check whether this is the final milestone.
         */
        bool is_final_milestone() const;

        operator std::string() const;
    
    private:
        DataConstRef iteration_list_() const;
};

} }

