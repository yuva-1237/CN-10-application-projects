# Project 04: DNS Resolver and Domain Lookup — Viva Questions & Answers

### Q1: What is DNS and what is its primary function in computer networks?
**Answer:** The Domain Name System (DNS) is a hierarchical, decentralized naming database that translates human-readable hostnames (e.g. `www.google.com`) into machine-routable IP addresses (e.g. `142.250.190.46`).

### Q2: On which port and transport layer protocol does DNS normally operate?
**Answer:** DNS operates on Port 53. It primarily uses the User Datagram Protocol (UDP) for standard queries to achieve low latency, and falls back to TCP when responses exceed 512 bytes or during zone transfers.

### Q3: What is the difference between an 'A' record and an 'AAAA' record?
**Answer:** An 'A' record maps a hostname to a 32-bit IPv4 address (e.g. `192.0.2.1`), while an 'AAAA' (quad-A) record maps a hostname to a 128-bit IPv6 address (e.g. `2001:db8::1`).

### Q4: What is a Reverse DNS (PTR) lookup?
**Answer:** A Pointer (PTR) lookup performs the reverse operation: resolving an IP address back to its associated canonical domain name (using the special `in-addr.arpa` or `ip6.arpa` domains).

### Q5: What does the Recursion Desired (RD) flag indicate in a DNS query header?
**Answer:** When the RD bit is set (`1`), the client requests that the contacted DNS server recursively resolve the query across the root, TLD, and authoritative name servers on the client's behalf rather than returning a referral.

### Q6: What is DNS caching and why is TTL important?
**Answer:** Caching stores resolved DNS records locally so future requests avoid traversing the network. Time-To-Live (TTL) is an integer set by the authoritative server indicating how many seconds the record can be cached before it must be discarded and re-queried.

### Q7: What is DNS label compression in RFC 1035?
**Answer:** To minimize UDP packet size, domain names repeated in answer records are replaced by 2-byte compression pointers (marked with leading bits `11` / `0xC0`) pointing to the byte offset in the packet where the domain name was first defined.

### Q8: What is the hierarchical structure of DNS?
**Answer:** Root Servers (`.`) $\rightarrow$ Top-Level Domain (TLD) Servers (`.com`, `.org`, `.edu`) $\rightarrow$ Authoritative Name Servers (`google.com`) $\rightarrow$ Host records (`www`).

### Q9: When does DNS use TCP instead of UDP?
**Answer:** When the DNS response payload exceeds 512 bytes (indicated by the TrunCation `TC` flag set in the response header), during DNS zone transfers between primary and secondary name servers, and for certain cryptographic DNSSEC responses.

### Q10: What is the purpose of an MX record?
**Answer:** A Mail Exchange (MX) record specifies the mail server responsible for accepting incoming email messages on behalf of a domain, along with a preference priority value.
