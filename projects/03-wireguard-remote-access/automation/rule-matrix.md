# WG_FRIENDS rule matrix & troubleshooting

## Who can reach what
| Peer group | LAB-MGMT | RED | TARGETS | BLUE | AD | Scoreboard 10.10.10.20:80 | Firewall | Home |
|---|---|---|---|---|---|---|---|---|
| WG_ADMINS (.2, .3) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ 443/22 | ❌ |
| Friends (.11–.49) | ❌ | ❌ | ✅ | ❌ | ⏱ game nights | ✅ | ❌ | ❌ |

## Rules (WG_FRIENDS tab)
1. Pass WG_ADMINS → LAB_NETS any
2. Pass WG_ADMINS → This Firewall 443,22
3. Block WG_FRIENDS net → This Firewall
4. Pass WG_FRIENDS net → TARGETS net
5. Pass WG_FRIENDS net → SCORING:80
6. (disabled) Pass WG_FRIENDS net → AD net
7. Block any → any (log)

TARGETS tab (above its final block): (disabled) Pass TARGETS net → WG_FRIENDS net : REV_SHELL_PORTS

## Troubleshooting
| Symptom | Likely cause | Check / fix |
|---|---|---|
| No handshake at all | Port forward missing, wrong endpoint, CGNAT, WAN rule missing | Capture UDP 51820 on OPNsense WAN while client connects. No packets = home router/ISP problem. Packets but no reply = WAN rule / instance disabled |
| Handshake OK, can't ping anything | Client AllowedIPs too narrow, or WG_FRIENDS rules | `wg show` on client: are bytes sent? Firewall live log filtered on 10.10.99.x |
| Can ping firewall but not targets | Rule order / missing rule 4 | Live log shows which rule blocked |
| Works outside home, not at home | Home router lacks hairpin NAT | Use OPNsense WAN IP as Endpoint when home |
| Drops after a few minutes idle | NAT mapping expired | `PersistentKeepalive = 25` |
| "Key is not correct length" | Pasted key truncated / extra spaces | Keys are 44 chars ending in `=` |
