#pragma once

namespace ymmsl {

enum class Operator {
    NONE = 0,
    F_INIT = 1,
    O_I = 2,
    S = 3,
    B = 4,
    O_F = 5
};

bool allows_sending(Operator op);

bool allows_receiving(Operator op);

}

