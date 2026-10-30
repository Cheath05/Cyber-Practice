#!/usr/bin/env python3
"""Subnetting practice quiz (standard library only).

    python3 subnet_quiz.py [--questions 10]

Each question gives an IP/prefix and asks for one of: network address, broadcast address,
number of usable hosts, first usable host, or the smallest prefix for N hosts.
"""
import argparse
import ipaddress
import random


def random_interface():
    prefix = random.randint(16, 30)
    addr = ipaddress.IPv4Address(random.choice([
        random.randint(0x0A000000, 0x0AFFFFFF),   # 10.0.0.0/8
        random.randint(0xAC100000, 0xAC1FFFFF),   # 172.16.0.0/12
        random.randint(0xC0A80000, 0xC0A8FFFF),   # 192.168.0.0/16
    ]))
    return ipaddress.IPv4Interface(f"{addr}/{prefix}")


def make_question():
    iface = random_interface()
    net = iface.network
    kind = random.choice(["network", "broadcast", "hosts", "first", "prefix_for"])
    if kind == "network":
        return f"Network address of {iface}?", str(net.network_address)
    if kind == "broadcast":
        return f"Broadcast address of {iface}?", str(net.broadcast_address)
    if kind == "hosts":
        return f"Usable hosts in a /{net.prefixlen}?", str(max(net.num_addresses - 2, 0))
    if kind == "first":
        return f"First usable host in {iface}?", str(net.network_address + 1)
    needed = random.randint(2, 4000)
    prefix = 32
    while (2 ** (32 - prefix)) - 2 < needed:
        prefix -= 1
    return f"Smallest prefix that fits {needed} hosts? (answer like /22)", f"/{prefix}"


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--questions", type=int, default=10)
    args = parser.parse_args()
    score = 0
    for i in range(1, args.questions + 1):
        question, answer = make_question()
        reply = input(f"[{i}/{args.questions}] {question} ").strip()
        if reply.lstrip("/") == answer.lstrip("/"):
            score += 1
            print("  correct")
        else:
            print(f"  wrong, answer: {answer}")
    print(f"\nScore: {score}/{args.questions}")


if __name__ == "__main__":
    main()
