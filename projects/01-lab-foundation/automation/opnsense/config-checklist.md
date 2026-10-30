# OPNsense Configuration Checklist (solution)

Menu names are from OPNsense 24.x/25.x. If yours differ slightly, search the menu (top-left
magnifier). Back up the config first: *System → Configuration → Backups → Download*.

## A. Resize & interface settings
- [ ] Proxmox: OPNsense VM memory 2048 MiB, ballooning **off**
- [ ] *Interfaces → Settings*: ☑ Disable hardware checksum offload, ☑ Disable hardware TCP
      segmentation offload, ☑ Disable hardware large receive offload → Save → reboot

## B. VLAN devices
*Interfaces → Devices → VLAN* (older: *Interfaces → Other Types → VLAN*)
| Device | Parent | Tag | Description |
|---|---|---|---|
| vlan0.20 | vtnet1 | 20 | RED |
| vlan0.30 | vtnet1 | 30 | TARGETS |
| vlan0.40 | vtnet1 | 40 | BLUE |
| vlan0.50 | vtnet1 | 50 | AD |

## C. Assign & address
*Interfaces → Assignments* → add each → click new OPTx interface:
| Interface | Enable | Description | IPv4 | Address |
|---|---|---|---|---|
| OPT1 | ☑ | RED | Static | 10.10.20.1/24 |
| OPT2 | ☑ | TARGETS | Static | 10.10.30.1/24 |
| OPT3 | ☑ | BLUE | Static | 10.10.40.1/24 |
| OPT4 | ☑ | AD | Static | 10.10.50.1/24 |

## D. DHCP (use the service your LAN already uses)
Per interface: range `.100`–`.199`, gateway = interface IP, DNS = interface IP.
AD: DNS servers `10.10.50.10, 10.10.50.1`, domain `lab.local`.

## E. Unbound DNS
- [ ] *Services → Unbound DNS → General*: Network interfaces = All, ☑ Register DHCP leases
      (or DHCP static mappings), domain `lab.home.arpa` (*System → Settings → General*)
- [ ] *Overrides → Domain overrides*: `lab.local` → `10.10.50.10` (add once dc01 exists, P07)
- [ ] *Overrides → Host overrides*: add hosts from `docs/network-reference.md` as you build them

## F. Aliases (*Firewall → Aliases*)
| Name | Type | Content |
|---|---|---|
| HOME_NET | Network(s) | <your home subnet> |
| RFC1918 | Network(s) | 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16 |
| LAB_NETS | Network(s) | 10.10.0.0/16 |
| WAZUH | Host(s) | 10.10.40.10 |
| WAZUH_PORTS | Port(s) | 1514, 1515 |
| SCORING | Host(s) | 10.10.10.20 |

## G. Rules (*Firewall → Rules → <interface>*), top to bottom, log all blocks
**LAN (LAB-MGMT)**: above the default allow: `Block | LAN net → HOME_NET | any`

**RED**
1. Pass · TCP/UDP · RED net → RED address · 53
2. Pass · ICMP · RED net → RED address
3. Block · any · RED net → This Firewall
4. Pass · any · RED net → TARGETS net
5. Pass · any · RED net → AD net *(disable outside P07)*
6. Block · any · RED net → RFC1918
7. Pass · any · RED net → any

**TARGETS**
1. Pass · TCP/UDP · TARGETS net → TARGETS address · 53
2. Pass · ICMP · TARGETS net → TARGETS address
3. Pass · TCP · TARGETS net → WAZUH · WAZUH_PORTS
4. Pass · any · TARGETS net → !RFC1918 *(DISABLED: TEMP egress)*
5. Block · any · TARGETS net → any

**BLUE**
1. Pass · TCP/UDP · BLUE net → BLUE address · 53
2. Pass · ICMP · BLUE net → BLUE address
3. Block · any · BLUE net → This Firewall
4. Pass · any · BLUE net → RED net
5. Pass · any · BLUE net → TARGETS net
6. Pass · any · BLUE net → AD net
7. Block · any · BLUE net → RFC1918
8. Pass · any · BLUE net → any

**AD**
1. Pass · TCP/UDP · AD net → AD address · 53, 123 (create port alias `DNS_NTP` = 53,123)
2. Pass · ICMP · AD net → AD address
3. Pass · TCP · AD net → WAZUH · WAZUH_PORTS
4. Pass · any · AD net → !RFC1918 *(DISABLED: TEMP Windows Update)*
5. Block · any · AD net → any

**WAN** (admin access until WireGuard, P01 step 5b)
- Interfaces → WAN: ☐ Block private networks (unchecked), ☑ Block bogon networks
- Alias `ADMIN_LAPTOP` = your laptop's reserved home-LAN IP
1. Pass · TCP/UDP/ICMP · ADMIN_LAPTOP → LAB_NETS · any (log)
2. Pass · TCP · ADMIN_LAPTOP → This Firewall · 443 *(optional, GUI)*
- Laptop: static route `10.10.0.0/16 via <OPNsense WAN IP>`

→ **Apply changes** → download config backup.

## H. NAT
- [ ] *Firewall → NAT → Outbound*: mode **Automatic**. Confirm new subnets appear in the
      automatic rules list.

## I. Verify
- [ ] Run `validate-isolation.sh` from a VM in each segment
- [ ] *Firewall → Log Files → Live View* shows your blocked test traffic
