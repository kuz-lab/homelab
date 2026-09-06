# Network and Access

The goal is to keep the house online while I am working on the services, and to control which devices can talk to each other.

[Overview](../README.md) · [Hardware](../SETUP.md) · [Services](services.md)

## The main path

The DrayTek Vigor 167 modem runs in bridge mode and hands the PPPoE connection to OPNsense, which runs as a VM on the ZimaBoard. OPNsense does routing, firewalling, NAT, DHCP and VLAN assignment. A UniFi USW-Lite-8-PoE switch carries the tagged traffic, and a U7 Lite access point maps SSIDs onto the Trusted, IoT and Guest networks.

Cubi runs the applications separately. Taking it down for maintenance does not stop the router — although client DNS filtering and the web services do go with it.

## Network groups

A VLAN separates a group of devices across the shared switch and access point.

| Network | VLAN | Subnet | Purpose |
| --- | --- | --- | --- |
| Management | 99 | 192.168.99.0/24 | Router, Proxmox hosts and network equipment |
| Servers | 40 | 192.168.40.0/24 | VMs, containers and their supporting services |
| Trusted | 10 | 192.168.10.0/24 | Personal computers and phones |
| IoT | 20 | 192.168.20.0/24 | Smart-home devices |
| Guest | 30 | 192.168.30.0/24 | Guest Wi-Fi, internet access and the designated DNS resolver |
| Automation | 50 | 192.168.50.0/24 | Later addition for experimental automation, not covered here |

## Connections between networks

The main VLAN policy is to deny cross-network traffic unless an explicit rule allows it. Rules use named aliases rather than raw addresses. The saved export also includes fallback LAN allow rules, so it is not a blanket block on every interface.

The exceptions that make the lab usable:

- **Trusted → Servers:** Caddy over HTTPS, AdGuard DNS, the Wazuh agent and Home Assistant. No SSH — that goes through the jump host.
- **Trusted → IoT:** full access, for device administration, AirPlay and Sonos.
- **Trusted → Management:** SSH to the Cubi jump host, and the web interfaces of the Proxmox hosts and OPNsense, from my MacBook only.
- **IoT → Servers:** Home Assistant callbacks and DNS to AdGuard.
- **Guest → Servers:** DNS to AdGuard, not general access to the applications.
- **Servers → IoT:** Home Assistant polling ESPHome, Shelly, Sonos and similar devices.
- **Servers → Management:** the UniFi controller, Caddy proxying to Proxmox, monitoring, and Home Assistant reading host sensors.
- **Management → Servers:** the access point reaching its UniFi controller, Proxmox reading Home Assistant sensors, and the hosts sending notifications to ntfy.
- **IoT and Guest → Trusted or Management:** blocked.

The examples above are drawn from the saved [readable export](../OPNsense/firewall-rules.csv), which contains 50 rules. They are not a fresh export of the running firewall and do not cover the later Automation VLAN.

The [raw recovery export](../OPNsense/firewall-rules-recovery.csv) has 48 rules and is **not an equivalent restore copy**. It lacks rules 1269 and 1275; rule 1257 has a broader source, and rule 4522 has broader protocol/port permissions. Compare aliases, interfaces and permissions against the intended policy before importing either file.

## Names and HTTPS

Client devices resolve through AdGuard Home, with OPNsense Unbound upstream. Servers query Unbound directly, on purpose: infrastructure name resolution should not depend on a filtering service. There is no fallback resolver for clients — if AdGuard stops, DNS fails visibly rather than quietly bypassing the filtering.

Inside the lab, service names under `kuzlab.dev` resolve to Caddy, which forwards each request to the right application. Caddy uses Cloudflare's DNS API to prove control of the domain; an ACME certificate authority issues the certificates. DNS validation does not require exposing the applications to the internet or sending their traffic through Cloudflare. [How DNS-01 works](https://caddyserver.com/docs/automatic-https#dns-challenge)

## Administration

I started by learning SSH and setting up key-based access manually. The setup later evolved around Cubi as a bastion host, using ProxyJump and SSH aliases to simplify connections to the other machines. A separate key was later introduced for Ansible.

For connections and Ansible runs started on my Mac, the private keys stay on the Mac; the jump host relays the connection. ProxyJump does not require forwarding the SSH agent. I also used three hardware security keys for access in an earlier setup; they are currently out of use. [OpenSSH ProxyJump](https://man.openbsd.org/ssh_config#ProxyJump)

Everyday guest access uses the regular `slava` account with sudo. Automation has a separate account and key, and the later setup includes an Ansible role for users, keys and sudo. The two Proxmox hosts retain key-only root access for administration.

| Scenario | Path |
| --- | --- |
| Daily service access | Caddy, via `*.kuzlab.dev` |
| Usual guest SSH access | MacBook → Cubi jump host → target, via ProxyJump |
| Remote access | Tailscale on OPNsense, followed by the allowed local entry points |
| Shell in a container from Proxmox | `pct enter <id>` — no SSH, no keys |
| Local recovery | Direct connection to the Proxmox or OPNsense address |
| Break-glass | Cable into the Management switch port, static address, no routing needed |

These paths reduce different dependencies. Local access does not need the WAN or Tailscale. Connecting to the Management switch port with a static address avoids routing between VLANs, but still needs the switch and target device to be working.

Cubi is also the Proxmox applications host, so its administrative access remains especially important: a host administrator can manage its guests without using their SSH keys. Moving the jump-host role to the separate Raspberry Pi is a planned improvement, not the current arrangement.

**Configuration check, 6 September 2026:** the 18 service LXCs checked had password and root SSH login disabled. The UniFi VM still allowed password authentication. The same check could not establish Wazuh's effective SSH settings; that is an incomplete check, not a confirmed SSH fault.

## Remote access and recovery

Tailscale runs on OPNsense through the `os-tailscale` plugin. The July access design allowed selected entry points: SSH to Cubi and ZimaBoard, HTTPS to Caddy, DNS to AdGuard, and the OPNsense web interface. The live Tailscale policy was not rechecked during the September documentation review.

Placing remote access on the firewall host keeps it separate from Cubi. If Cubi is down, the network and OPNsense can still be reached, provided the firewall host and WAN are working.

Local administration does not depend on Tailscale at all.

The [August remote VR case study](virtual-desktop-remote-access.md) deliberately opened internet-facing port forwards for one host. It is separate from this private access design; the current status of those forwards was not checked in the September review.

## Diagrams

These earlier sketches explain the layout and design intent, not the current complete policy. In particular, the VLAN image omits the Automation VLAN and simplifies DNS exceptions; use the written rules above for those details.

- [Physical topology](../diagrams/Physical_topology.png)
- [DNS and access paths](../diagrams/ingress-dns-access.png)
- [VLAN policy matrix](../diagrams/vlan-policy-matrix.png)
