# Learning Path: Courses, Videos & Programming Languages

The projects teach by doing. This page gives you the **theory to read and watch alongside
them**, plus a programming track (Python first, then C/C++, Bash, PowerShell and others) so the
code in the projects never feels like magic.

Everything here is free unless marked 💲. University courses are listed by their public
pages. Watch the lectures that match the project you're on; you don't need whole courses.

## Core university courses (free)

| Course | School | What it's good for | Projects |
|---|---|---|---|
| [6.858 Computer Systems Security (Fall 2014)](https://ocw.mit.edu/courses/6-858-computer-systems-security-fall-2014/) | MIT OCW | Video lectures: threat models, buffer overflows, privilege separation, web security, network security, Kerberos, TLS | 04–07, 12 |
| [The Missing Semester of Your CS Education](https://missing.csail.mit.edu/) | MIT | Shell, scripting, Vim, data wrangling, Git, debugging, security basics. **Do this first.** | All |
| [6.100L Intro to CS and Programming Using Python (Fall 2022)](https://ocw.mit.edu/courses/6-100l-introduction-to-cs-and-programming-using-python-fall-2022/) | MIT OCW | Python fundamentals with lectures + problem sets | All Python exercises |
| [6.096 Introduction to C++ (IAP 2011)](https://ocw.mit.edu/courses/6-096-introduction-to-c-january-iap-2011/) | MIT OCW | Short, compact C++ course: pointers, memory, classes | C/C++ exercises |
| [6.033 Computer System Engineering (Spring 2018)](https://ocw.mit.edu/courses/6-033-computer-system-engineering-spring-2018/) | MIT OCW | Systems design, networking layers, reliability, security | 01–03, 13 |
| [6.1810 / 6.S081 Operating System Engineering](https://pdos.csail.mit.edu/6.S081/) | MIT | How an OS works (xv6 in C): processes, memory, syscalls, permissions | 04, 06, 11 |
| [CS50x](https://cs50.harvard.edu/x/) | Harvard | Best intro to C (memory, pointers), then Python, SQL, web | C/C++ track |
| [CS50's Introduction to Cybersecurity](https://cs50.harvard.edu/cybersecurity/) | Harvard | Accounts, data, systems, software and privacy security for a broad audience | 03, 12 |
| [CS50's Introduction to Programming with Python (CS50P)](https://cs50.harvard.edu/python/) | Harvard | Python from scratch: regex, file I/O, libraries, unit tests | Python track |
| [CS 253 Web Security](https://web.stanford.edu/class/cs253/) | Stanford | Browser security model, XSS, CSRF, cookies, HTTPS: video lectures | 06, 09 |
| [CS 155 Computer and Network Security](https://cs155.stanford.edu/) | Stanford | Slides + projects: control hijacking, isolation, web, network attacks | 02, 06 |
| [Cryptography I](https://www.coursera.org/learn/crypto) (audit free) | Stanford / Coursera (Dan Boneh) | Rigorous but approachable crypto: stream/block ciphers, MACs, public key | 03, 12 |
| [Introduction to Cryptography (Christof Paar)](https://www.crypto-textbook.com/) | Ruhr-Uni Bochum (lecture videos linked from the book site / YouTube) | Excellent, beginner-friendly crypto lecture series | 03, 12 |
| [Computer Networking: A Top-Down Approach (Kurose & Ross)](https://gaia.cs.umass.edu/kurose_ross/) | UMass | Textbook companion site, lecture slides, interactive problems and Wireshark labs | 01–03 |

## Shorter video series

| Series | Topic | Projects |
|---|---|---|
| [Professor Messer: Network+ and Security+](https://www.professormesser.com/) | Exam-aligned overviews of every core concept | All; Sec+ study |
| [Practical Networking (Ed Harmoush): Packet Traveling](https://www.practicalnetworking.net/series/packet-traveling/) | How a packet moves through switches and routers: clearest explanation anywhere | 01, 02 |
| Chris Greer (YouTube): Wireshark / TCP deep dives | Packet analysis | 02 |
| Computerphile (YouTube) | Short explainers: hashing, TLS, buffer overflows, Kerberos | All |
| LiveOverflow (YouTube): Binary Exploitation playlist | Memory corruption from zero | 06, 09 |
| IppSec (YouTube) | HTB box walkthroughs; search his site for any technique | 06, 07 |
| John Hammond (YouTube) | CTFs, malware analysis | 09, 11 |
| 13Cubed (YouTube) | Windows forensics, memory forensics | 11 |
| Black Hills InfoSec / Antisyphon (YouTube + 💲 pay-what-you-can) | SOC core skills, threat hunting, AD attacks | 07, 08 |
| [Andrej Karpathy: Intro to Large Language Models](https://www.youtube.com/watch?v=zjkBMFhNj_g) | How LLMs work, and LLM security (jailbreaks, prompt injection) at the end | 14 |

## Hands-on learning platforms (complements to the projects)

| Platform | Best for |
|---|---|
| [pwn.college](https://pwn.college/) (Arizona State) | Linux, assembly, C memory errors, binary exploitation, with a free dojo for each topic |
| [OverTheWire Bandit](https://overthewire.org/wargames/bandit/) | Linux command line under pressure |
| [PortSwigger Web Security Academy](https://portswigger.net/web-security) | Web vulnerabilities with free labs |
| [Nightmare](https://guyinatuxedo.github.io/) | Binary exploitation course built on real CTF challenges |
| [CryptoHack](https://cryptohack.org/) | Learn cryptography by breaking it (Python) |

---

## Programming track

You don't need to be a software engineer for security, but **reading and writing small tools**
is expected in almost every internship posting (see [what-employers-want](what-employers-want.md)).
Every project has a Python exercise, and several have an exercise in another language.

### Python (primary language)

1. **Foundations** (pick one): [CS50P](https://cs50.harvard.edu/python/) or
   [MIT 6.100L](https://ocw.mit.edu/courses/6-100l-introduction-to-cs-and-programming-using-python-fall-2022/).
2. **Practical scripting:** [Automate the Boring Stuff with Python](https://automatetheboringstuff.com/)
   (free online), chapters on files, regex, CSV/JSON, and web requests.
3. **Security-specific:** the [Python primer](python-primer.md) in this repo explains every
   module the solutions use, with small examples. *Black Hat Python* (No Starch 💲) is the
   classic next step.
4. **Habit:** before opening a solution, read the primer section listed in the project's
   *Coding exercises* section.

### C and C++ (how memory really works)

Why bother: memory corruption (buffer overflows, use-after-free) is still a top vulnerability
class. Exploits, EDR products, malware and much of the OS are written in C/C++. Being able to
*read* C makes you a better pentester, reverse engineer and malware analyst. It also stands out
on a resume.

1. **C first:** [CS50x weeks 1–5](https://cs50.harvard.edu/x/) (C, arrays, memory, pointers, data structures).
2. **Then C++:** [MIT 6.096](https://ocw.mit.edu/courses/6-096-introduction-to-c-january-iap-2011/)
   and [learncpp.com](https://www.learncpp.com/) as a reference.
3. **Networking in C:** [Beej's Guide to Network Programming](https://beej.us/guide/bgnet/)
   (sockets, TCP/UDP from the system-call level).
4. **Security in C:** [pwn.college](https://pwn.college/) "Program Security" and LiveOverflow's
   binary exploitation playlist; [MIT 6.858 lecture 2–3](https://ocw.mit.edu/courses/6-858-computer-systems-security-fall-2014/) on buffer overflows.

C/C++ exercises in this repo:

| Project | Exercise | Concepts |
|---|---|---|
| 02 | Packet sniffer in C++ with libpcap | Raw packets, structs, byte order, the libpcap API |
| 04 | Plant a vulnerable SUID C program (PATH hijack) in your CyberPatriot image | Linux privileges, `execvp`, why SUID binaries are dangerous |
| 06 | Stack buffer overflow lab in C, debugged with GDB | Stack layout, return addresses, compiler protections (canaries, NX, ASLR) |
| 09 | Write a reversing challenge and a pwn challenge in C for your CTF | Compilation, stripping symbols, `checksec`, Docker isolation |
| 11 | File carver in C++ (recover JPEGs from a disk image by magic bytes) | Binary I/O, file signatures, the same logic forensic tools use |

### Bash

[MIT Missing Semester lectures 1–2 and 4](https://missing.csail.mit.edu/) plus
[Bandit](https://overthewire.org/wargames/bandit/). Every `automation/` folder has commented
Bash scripts to read. Run `shellcheck` on your own scripts (it teaches you as it complains).

### PowerShell (Windows, AD, blue team)

[Microsoft Learn: PowerShell 101](https://learn.microsoft.com/en-us/powershell/scripting/learn/ps101/00-introduction)
→ used heavily in Projects 05, 07, 08.

### Other languages you'll touch

| Language | Where | Learn from |
|---|---|---|
| SQL | P06 (SQL injection), P12 (querying scan data with SQLite) | [CS50x SQL week](https://cs50.harvard.edu/x/), [SQLBolt](https://sqlbolt.com/) |
| JavaScript | P06 (Juice Shop is Node.js), XSS payloads | [javascript.info](https://javascript.info/) |
| YAML / XML | P08 (Sigma rules, Wazuh rules), P13 (Ansible) | Read the examples in this repo |
| HCL | P13 (Terraform) | [HashiCorp Terraform tutorials](https://developer.hashicorp.com/terraform/tutorials) |
| YARA | P11 (malware/file matching rules) | [YARA docs](https://yara.readthedocs.io/) |
| Go (optional) | WireGuard-go, many modern security tools (nuclei) | [A Tour of Go](https://go.dev/tour/) |
