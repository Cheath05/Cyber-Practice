// sniffer.cpp - tiny packet summarizer in C++ using libpcap (Project 02 C++ exercise, solution).
//
// Reads a pcap file (or a live interface) and prints protocol counts, top talkers, and
// sources that sent SYNs to many ports (scan detection), mirroring pcap_summary.py.
//
// Build:  sudo apt install g++ libpcap-dev && make
// Run:    ./sniffer -r capture.pcap            (offline)
//         sudo ./sniffer -i eth0 -c 500        (live, 500 packets)
//
// Concepts: C structs over raw bytes, network byte order (ntohs), pointer arithmetic,
// std::map / std::set, callbacks with a user pointer.
#include <arpa/inet.h>
#include <netinet/if_ether.h>
#include <netinet/ip.h>
#include <netinet/tcp.h>
#include <pcap/pcap.h>

#include <algorithm>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <map>
#include <set>
#include <string>
#include <unistd.h>
#include <utility>
#include <vector>

namespace {

struct Stats {
    std::map<std::string, long> protocols;
    std::map<std::string, long> talkers;
    // (src, dst) -> distinct destination ports that received a bare SYN
    std::map<std::pair<std::string, std::string>, std::set<uint16_t>> syns;
    long total = 0;
};

std::string ip_to_string(in_addr addr) {
    char buf[INET_ADDRSTRLEN];
    inet_ntop(AF_INET, &addr, buf, sizeof buf);
    return buf;
}

// libpcap calls this once per packet. `user` is the Stats* we passed to pcap_loop.
void on_packet(u_char *user, const pcap_pkthdr *hdr, const u_char *bytes) {
    auto *stats = reinterpret_cast<Stats *>(user);
    stats->total++;

    if (hdr->caplen < sizeof(ether_header)) return;
    const auto *eth = reinterpret_cast<const ether_header *>(bytes);
    uint16_t ethertype = ntohs(eth->ether_type);   // network byte order -> host order

    if (ethertype == ETHERTYPE_ARP) { stats->protocols["ARP"]++; return; }
    if (ethertype != ETHERTYPE_IP) { stats->protocols["other"]++; return; }
    if (hdr->caplen < sizeof(ether_header) + sizeof(ip)) return;

    const auto *iph = reinterpret_cast<const ip *>(bytes + sizeof(ether_header));
    std::string src = ip_to_string(iph->ip_src);
    std::string dst = ip_to_string(iph->ip_dst);
    stats->talkers[src]++;

    size_t ip_header_len = static_cast<size_t>(iph->ip_hl) * 4;   // ip_hl counts 32-bit words
    switch (iph->ip_p) {
        case IPPROTO_TCP: {
            stats->protocols["TCP"]++;
            size_t offset = sizeof(ether_header) + ip_header_len;
            if (hdr->caplen < offset + sizeof(tcphdr)) break;
            const auto *tcp = reinterpret_cast<const tcphdr *>(bytes + offset);
            if (tcp->syn && !tcp->ack) {
                stats->syns[{src, dst}].insert(ntohs(tcp->dest));
            }
            break;
        }
        case IPPROTO_UDP:  stats->protocols["UDP"]++; break;
        case IPPROTO_ICMP: stats->protocols["ICMP"]++; break;
        default:           stats->protocols["other-IP"]++; break;
    }
}

void usage(const char *prog) {
    std::cerr << "Usage: " << prog << " -r file.pcap | -i iface [-c count] [-t scan_threshold]\n";
    std::exit(1);
}

}  // namespace

int main(int argc, char **argv) {
    std::string file, iface;
    int count = -1;            // -1 = until end of file / forever
    size_t threshold = 20;
    int opt;
    while ((opt = getopt(argc, argv, "r:i:c:t:")) != -1) {
        switch (opt) {
            case 'r': file = optarg; break;
            case 'i': iface = optarg; break;
            case 'c': count = std::atoi(optarg); break;
            case 't': threshold = static_cast<size_t>(std::atoi(optarg)); break;
            default: usage(argv[0]);
        }
    }
    if (file.empty() == iface.empty()) usage(argv[0]);   // exactly one source

    char errbuf[PCAP_ERRBUF_SIZE] = {};
    pcap_t *handle = file.empty()
        ? pcap_open_live(iface.c_str(), 65535, /*promisc=*/1, /*timeout ms=*/1000, errbuf)
        : pcap_open_offline(file.c_str(), errbuf);
    if (!handle) { std::cerr << "pcap: " << errbuf << "\n"; return 1; }
    if (pcap_datalink(handle) != DLT_EN10MB) {
        std::cerr << "Only Ethernet captures are supported\n";
        pcap_close(handle);
        return 1;
    }

    Stats stats;
    if (pcap_loop(handle, count, on_packet, reinterpret_cast<u_char *>(&stats)) == -1) {
        std::cerr << "pcap_loop: " << pcap_geterr(handle) << "\n";
    }
    pcap_close(handle);

    std::cout << "Packets: " << stats.total << "\n\nProtocols:\n";
    for (const auto &[proto, n] : stats.protocols) std::cout << "  " << proto << "\t" << n << "\n";

    std::vector<std::pair<std::string, long>> top(stats.talkers.begin(), stats.talkers.end());
    std::sort(top.begin(), top.end(), [](auto &a, auto &b) { return a.second > b.second; });
    std::cout << "\nTop talkers:\n";
    for (size_t i = 0; i < top.size() && i < 5; ++i)
        std::cout << "  " << top[i].first << "\t" << top[i].second << "\n";

    std::cout << "\nPossible port scans (> " << threshold << " ports):\n";
    bool found = false;
    for (const auto &[pair, ports] : stats.syns) {
        if (ports.size() > threshold) {
            found = true;
            std::cout << "  " << pair.first << " -> " << pair.second << ": " << ports.size() << " ports\n";
        }
    }
    if (!found) std::cout << "  none\n";
    return 0;
}
