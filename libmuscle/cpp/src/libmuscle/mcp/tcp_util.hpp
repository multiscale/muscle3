#pragma once

#include <sys/types.h>


namespace libmuscle { namespace impl { namespace mcp {

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
 * Yes, I know host order is big endian, but who still has big endian? So
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

} } }

