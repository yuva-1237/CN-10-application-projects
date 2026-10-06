# Project 01: LAN Chat and File Sharing — Viva Questions & Answers

### Q1: What is a socket and which socket type is used in this project?
**Answer:** A socket is a software abstraction representing an endpoint for two-way inter-process communication over a network. This project uses a stream socket (`SOCK_STREAM`) over the IPv4 family (`AF_INET`), which implements the Transmission Control Protocol (TCP).

### Q2: Why is TCP preferred over UDP for file sharing and chat applications?
**Answer:** TCP is connection-oriented, guarantees ordered delivery, performs automatic retransmission upon packet loss, and ensures data integrity. In file sharing and text chat, losing even a single byte or receiving out-of-order bytes can corrupt a file or render messages unreadable.

### Q3: What is the purpose of `setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)`?
**Answer:** When a TCP server closes, its socket enters the `TIME_WAIT` state for a brief period to ensure leftover packets clear the network. `SO_REUSEADDR` allows the server to immediately rebind to the same port without waiting for the `TIME_WAIT` timer to expire.

### Q4: What is the "TCP sticky packet" or stream boundary problem, and how does your project solve it?
**Answer:** TCP treats data as a continuous stream of bytes rather than discrete message frames. Multiple `send()` calls can be merged by the OS (Nagle's algorithm) or fragmented across packets. We solved this by implementing a length-prefixed framing protocol: every frame begins with a fixed 4-byte big-endian integer indicating the exact size of the payload.

### Q5: What does `bind()` do in socket programming?
**Answer:** `bind()` associates an unaddressed socket descriptor with a specific local IP address and port number on the host machine.

### Q6: What is the difference between `bind(('127.0.0.1', port))` and `bind(('0.0.0.0', port))`?
**Answer:** Binding to `127.0.0.1` restricts incoming connections to the local loopback interface only (same machine). Binding to `0.0.0.0` (INADDR_ANY) instructs the operating system to listen for connections across all available network interfaces, including Ethernet and Wi-Fi adapters on the LAN.

### Q7: Why is multi-threading necessary on the server?
**Answer:** Socket `accept()` and `recv()` calls are blocking by default. Without threading or asynchronous I/O, servicing one client would completely block the server, preventing any other client from connecting or communicating simultaneously.

### Q8: How is file integrity verified across the network?
**Answer:** Before sending, the client calculates the SHA-256 cryptographic hash of the file and sends it inside the metadata header. Upon receiving and reassembling all chunks, the receiving client computes the SHA-256 hash of the local file and verifies that it matches the original hash.

### Q9: What happens when a client disconnects abruptly (e.g., unplugging Ethernet)?
**Answer:** When a connection drops, `recv()` returns zero bytes (`b""`), indicating an End-Of-File (EOF) condition or raises an `OSError`/`ConnectionResetError`. The server catches this exception, closes the socket descriptor, removes the user from the active registry, and notifies peers.

### Q10: How does private messaging differ from broadcast messaging in this architecture?
**Answer:** In broadcast messaging, the server iterates through all entries in its connected client dictionary and writes the frame to every socket. In private messaging, the server looks up the specific recipient's socket descriptor in the registry and writes the frame exclusively to that client.
