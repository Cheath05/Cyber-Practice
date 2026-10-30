# ⚠️ Solution: use only if stuck

| File | What it does |
|---|---|
| `setup-lab-docker.sh` | Run on the Proxmox host: clones VM 301 (lab-docker) into TARGETS |
| `install-docker.sh` | Run inside lab-docker (TEMP egress on): installs Docker, tcpdump, guest agent, whoami app |
| `remote-capture.sh` | Run on your laptop: streams tcpdump from a lab host into Wireshark |
| `answer-key.md` | Answers to the lab questions and exercises |
| `python/pcap_summary.py` | Python exercise solution (scapy): top talkers, protocols, DNS, scan detection |
| `cpp/sniffer.cpp` + `Makefile` | C++ exercise solution: libpcap packet summarizer with scan detection (`make && ./sniffer -r file.pcap`) |
| `python/subnet_quiz.py` | Subnetting practice quiz (standard library only) |
