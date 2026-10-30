# Answer Key: Project 02

## Lab 1: ARP
- You do **not** see the RED test box's ARP on lab-docker. ARP is layer 2 and doesn't
  cross a router. The test box ARPs for its gateway (10.10.20.1); OPNsense then ARPs on the
  TARGETS VLAN for 10.10.30.10 *from 10.10.30.1*. Each VLAN is its own broadcast domain, so an
  ARP spoofer in RED can't poison hosts in TARGETS.

## Lab 2: DHCP
- Discover (client 0.0.0.0:68 → 255.255.255.255:67), Offer (server → client, proposed IP),
  Request (client broadcasts which offer it accepts), Ack (server confirms + lease time).
- Options to note: 1 subnet mask, 3 router, 6 DNS, 51 lease time, 54 server identifier.

## Lab 3: DNS
- `dig +trace` from TARGETS fails because it queries the root servers directly (internet),
  and TARGETS has no egress. Plain `dig @10.10.30.1` works because Unbound on the firewall
  does the recursion for you.
- The second query is faster and its TTL is lower: the answer comes from Unbound's cache.
- Flags: RD = recursion desired (client asks), RA = recursion available (server offers).

## Lab 4: TCP and scans
- `-sS`: SYN → SYN/ACK (open) → scanner sends **RST** (never completes the handshake). Closed
  port: SYN → RST/ACK.
- `-sT`: full handshake, then RST/ACK. The application *sees* the connection (whoami logs it),
  so it's noisier at the application layer.
- `-sU`: open|filtered when there's no reply; closed = ICMP type 3 code 3 (port unreachable).
  UDP scans are slow because of ICMP rate limiting.
- `-sV`: completes connections and sends probes; very visible in app logs.
- Scanning 10.10.40.10 from RED: the firewall **drops** silently, so nmap reports
  *filtered* (no response). *Closed* means the host answered with RST. Filtered means
  something in between ate the packet.

## Lab 5: HTTP/TLS
- HTTP POST body shows `user=alice&pass=Secret123` in cleartext.
- TLS: the ClientHello extension `server_name` shows `example.com`. Defenders still see IPs,
  SNI (unless ECH is used), certificate (TLS 1.2), packet sizes and timing, and JA3/JA4
  client fingerprints.

## Lab 6: Routing
- From RED to 10.10.30.10: 2 hops (10.10.20.1, then the target).
- To 1.1.1.1: 10.10.20.1 (OPNsense) → home router (192.168.x.1) → ISP… **Double NAT:** OPNsense
  translates 10.10.20.99 → its WAN IP (192.168.x.y); the home router translates that → your
  public IP. Replies are un-translated in reverse via each device's state table.

## Exercise 2: example display filters
- SYN-only: `tcp.flags.syn == 1 && tcp.flags.ack == 0`
- DNS for a domain: `dns.qry.name contains "example"`
- HTTP POSTs: `http.request.method == "POST"`
- TLS ClientHello: `tls.handshake.type == 1`
- Between two hosts: `ip.addr == 10.10.20.99 && ip.addr == 10.10.30.10`

## Exercise 3: troubleshooting method (runbook outline)
1. Define the failing flow precisely (src, dst, port, protocol).
2. Test layer by layer: link/IP (`ip a`, gateway ping) → DNS (`dig`) → TCP (`curl -v`,
   `/dev/tcp`) → app.
3. Check *Firewall → Log Files → Live View* filtered on the source IP. Is there a block, and
   which rule (label)?
4. If there's no block: capture on *both* firewall interfaces (ingress and egress VLAN). Did the
   packet leave? Did the reply come back?
5. Check the destination host firewall (`ufw status`, Windows Firewall) and that the service
   listens (`ss -lntp`).
6. Fix one thing at a time and re-test. Record the change.
