# Packet Analysis Report: <Capture / scenario name>

| Field | Value |
|---|---|
| Analyst | <you> |
| Date | YYYY-MM-DD |
| Capture source | <host/interface, tool, filter> |
| Capture window | YYYY-MM-DD HH:MM–HH:MM UTC |
| File | <name.pcap>, SHA-256 `<hash>` |

## 1. Summary
> 3–5 sentences: what traffic this is, what you found, and why it matters.

## 2. Environment
> Hosts involved (IP, role) and where the capture point sits in the network diagram.

| IP | Hostname / role |
|---|---|

## 3. Traffic overview
| Protocol | Packets | % | Notes |
|---|---|---|---|

Top talkers (Wireshark *Statistics → Conversations*):
| Source | Destination | Packets | Bytes |
|---|---|---|---|

## 4. Findings
### Finding 1: <title>
- **Observation:** <what the packets show; filter used, e.g. `tcp.flags.syn==1 && tcp.flags.ack==0`>
- **Evidence:** frame numbers <n–m>, *Figure 1*
- **Interpretation:** <what it means; label inference vs. fact>

## 5. Protocol walkthroughs
> e.g. annotated DHCP DORA, TCP 3-way handshake, DNS query/response, TLS ClientHello (SNI).

## 6. Indicators (if malicious)
| Type | Value | Context |
|---|---|---|

## 7. Conclusions & recommendations

## Appendix: filters used
| Filter | Purpose |
|---|---|
