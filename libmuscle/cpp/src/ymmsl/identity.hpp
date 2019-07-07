#pragma once

#include <ostream>
#include <string>


namespace ymmsl {

class Identifier {
    public:
        Identifier(std::string const & contents);

    private:
        friend std::ostream & operator<<(std::ostream & os, Identifier const & i);
        std::string data_;
};


}

