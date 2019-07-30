// Template implementation. Do not include directly!

#include <utility>


namespace libmuscle {

template <typename T>
Optional<T>::Optional()
    : is_set_(false)
{}

template <typename T>
Optional<T>::Optional(T const & t)
    : is_set_(true)
{
    new (&t_) T(t);
}

template <typename T>
Optional<T>::Optional(Optional<T> const & rhs)
    : is_set_(rhs.is_set_)
{
    if (is_set_)
        new (&t_) T(rhs.t_);
}

template <typename T>
Optional<T>::Optional(Optional<T> && rhs)
    : is_set_(rhs.is_set_)
{
    if (is_set_)
        new (&t_) T(std::move(rhs.t_));
}

template <typename T>
Optional<T> & Optional<T>::operator=(Optional<T> const & rhs) {
    if (!is_set_ && rhs.is_set_)
        new (&t_) T (rhs.t_);
    else if (is_set_ && !rhs.is_set_)
        destruct_();
    else if (is_set_ && rhs.is_set_)
        t_ = rhs.t_;

    is_set_ = rhs.is_set_;
    return *this;
}

template <typename T>
Optional<T> & Optional<T>::operator=(Optional<T> && rhs) {
    if (!is_set_ && rhs.is_set_)
        new (&t_) T (std::move(rhs.t_));
    else if (is_set_ && !rhs.is_set_)
        destruct_();
    else if (is_set_ && rhs.is_set_)
        t_ = std::move(rhs.t_);

    is_set_ = rhs.is_set_;
    return *this;
}

template <typename T>
Optional<T>::~Optional() {
    destruct_();
}

template <typename T>
bool Optional<T>::operator==(Optional<T> const & rhs) const {
    if (is_set_ != rhs.is_set_)
        return false;
    if (!is_set_ && !rhs.is_set_)
        return true;
    return t_ == rhs.t_;
}

template <typename T>
bool Optional<T>::operator!=(Optional<T> const & rhs) const {
    return !(*this == rhs);
}

template <typename T>
bool Optional<T>::is_set() const {
    return is_set_;
}

template <typename T>
T const & Optional<T>::get() const {
    return t_;
}

template <typename T>
void Optional<T>::destruct_() {
    if (is_set_)
        t_.~T();
    is_set_ = false;
}

}

