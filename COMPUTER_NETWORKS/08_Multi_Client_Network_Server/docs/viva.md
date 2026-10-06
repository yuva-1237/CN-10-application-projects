# Project 08: Multi-Client Network Server — Viva Questions & Answers

### Q1: Why can't a single-threaded blocking socket server handle multiple clients simultaneously?
**Answer:** In blocking mode, calls like `accept()` and `recv()` suspend thread execution until network activity occurs. If a single-threaded server is blocked waiting for data from Client A, it cannot accept connections from Client B or read messages from Client C.

### Q2: What is I/O Multiplexing?
**Answer:** I/O multiplexing is a mechanism where an operating system system call (`select`, `poll`, `epoll`, or `kqueue`) monitors multiple non-blocking socket file descriptors simultaneously and notifies the application when any descriptor is ready for reading or writing.

### Q3: What is the Python `selectors` module?
**Answer:** `selectors` is a high-level Python standard library module that provides platform-independent I/O multiplexing. It automatically selects the most efficient OS primitive available: `epoll` on Linux, `kqueue` on macOS/BSD, and `select` on Windows.

### Q4: What does `sock.setblocking(False)` do?
**Answer:** It configures the socket to return immediately instead of pausing thread execution. If a non-blocking `recv()` has no data waiting, it raises `BlockingIOError` or `EWOULDBLOCK` instead of hanging.

### Q5: What are `EVENT_READ` and `EVENT_WRITE` in selectors?
**Answer:** `EVENT_READ` indicates that the socket has incoming data in its receive buffer ready to be read. `EVENT_WRITE` indicates that the socket's network transmit buffer has capacity to accept outgoing data.

### Q6: Why must we remove `EVENT_WRITE` interest when a client's outbound buffer is empty?
**Answer:** A TCP socket is almost always ready to accept writes under normal conditions. If `EVENT_WRITE` remains registered continuously, the event loop will trigger non-stop on every iteration, driving CPU utilization to 100% (busy-waiting).

### Q7: What is the "C10K problem"?
**Answer:** The C10K problem refers to the historical challenge of designing web and network servers capable of handling 10,000 concurrent client connections on a single machine, solved by transitioning from thread-per-connection to event-driven non-blocking I/O.

### Q8: How does this project handle message fragmentation over non-blocking streams?
**Answer:** Every incoming byte chunk is appended to a client-specific `in_buffer`. The `unpack_frames()` function parses length-prefixed headers, extracts only complete JSON messages, and leaves partial frames in the buffer until more data arrives.

### Q9: What happens when a client disconnects unexpectedly?
**Answer:** The non-blocking socket becomes readable, but `recv()` returns zero bytes (`b""`). The server detects this EOF condition, unregisters the socket from the selector, closes the socket descriptor, removes the user from the registry, and updates connection statistics.

### Q10: How do production servers like Nginx, Redis, and Node.js relate to this architecture?
**Answer:** Nginx, Redis, and Node.js use the identical non-blocking event-loop architecture (using `epoll` and `kqueue`) to service tens of thousands of concurrent connections with low memory usage.
