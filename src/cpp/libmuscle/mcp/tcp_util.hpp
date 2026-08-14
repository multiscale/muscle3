#pragma once

#include <poll.h>
#include <stdexcept>
#include <sys/types.h>
#include <vector>

#include <libmuscle/namespace.hpp>


namespace libmuscle { namespace _MUSCLE_IMPL_NS { namespace mcp {

class Disconnect : public std::runtime_error {
    using std::runtime_error::runtime_error; };

class ConnectionRefused : public Disconnect {
    using Disconnect::Disconnect; };

/* Check for connection errors.
 *
 * This takes a result from send() or recv(), checks whether it indicates an error by
 * equalling -1, then inspects errno to see which error we've got and throws Disconnect
 * or ConnectionRefused (see above) as appropriate.
 *
 * This makes error handling easier, and makes this C++ code look more similar to the
 * corresponding Python code.
 */
ssize_t check_conn(ssize_t result);

/* Poll until timeout is reached. Retry when interrupted with EINTR.
 *
 * @param timeout Timeout in seconds
 * @return The number of ready sockets, or zero on timeout.
 */
int poll_retry_eintr(pollfd *fds, nfds_t nfds, double timeout);

/* Poll a single fd until the timeout is reached.
 *
 * @param socket_fd File descriptor of socket to poll
 * @param timeout Timeout in seconds
 * @return The number of ready sockets, or zero on timeout
 */
int do_poll_out(int socket_fd, double timeout);

/* Send a message on a socket.
 *
 * This calls send() as often as needed to send the whole message.
 */
ssize_t send_all(int fd, char const * data, ssize_t length);

/* Receive a message on a socket.
 *
 * This calls recv() as often as needed to receive the whole message.
 *
 * Make sure that the buffer that data points to is at least length bytes in
 * size.
 *
 * @param fd The socket to receive on.
 * @param data The buffer to write received data into.
 * @param length The length of the message to receive.
 */
ssize_t recv_all(int fd, char * data, ssize_t length);

/* Sends a uint64 in little-endian format.
 * Yes, I know network order is big endian, but who still has big endian? So
 * we're using little endian and save on the conversion. If this becomes a
 * problem, then we can detect endianness here and convert if we're on a
 * big-endian machine.
 */
void send_int64(int fd, int64_t data);

/* Receive an int64_t in little-endian format.
 *
 * See comment above.
 */
int64_t recv_int64(int fd);

/* Send a message on a socket, prefixed by its length.
 */
ssize_t send_frame(int fd, char const * data, ssize_t length);

/* Receive a message from a socket, prefixed by its length.
 */
std::vector<char> recv_frame(int fd);

} } }

