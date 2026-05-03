# Slava's Homelab

Hi, I'm **Viacheslav Kuzin** (Slava). I work as an Amazon Robotics FC associate and run a homelab that started with a Raspberry Pi 5 and Home Assistant — and gradually grew into a full self-hosted infrastructure stack with segmented networking, a SIEM, reverse proxy, and services I rely on daily.

---

## Hardware

### Main Node — MSI Cubi NUC 1MG

| Component | Spec |
|-----------|------|
| CPU | Intel i5-120U |
| RAM | 40 GB DDR5-5200 |
| NVMe | 1× 512 GB |
| SSD | 1× 1 TB |
| NIC | 2× 2.5 GbE |

### Backup Node *(in progress)*

- Raspberry Pi 5 — 8 GB RAM

### Network Gear

| Device | Role |
|--------|------|
| DrayTek Vigor 167 | Modem (bridge mode) |
| TP-Link TL-SG105PE | Managed switch (PoE, VLAN) |
| UniFi U6+ | Wireless AP |
| Eaton Ellipse 650 Pro | UPS |

---

## Software

- **Hypervisor:** Proxmox VE 9.1.7
- **Guest OS:** Debian 12/13 (VMs and LXCs)
- **Provisioning:** Manual + [community scripts](https://community-scripts.github.io/ProxmoxVE/) for some LXCs

---

## Network Architecture

![Physical Topology](physical-topology.jpg)

### VLANs

| VLAN | ID | Purpose |
|------|----|---------|
| Trusted | 10 | Personal devices |
| IoT | 20 | Smart home devices (isolated) |
| Guest | 30 | Guest Wi-Fi |
| Servers | 40 | All VMs and containers |
| Management | 99 | Infrastructure access |

### DNS Chain

```
Clients → AdGuard Home (filtering) → Unbound (recursive) → Root servers
```

Wildcard DNS (`*.kuzlab.dev`) points to Caddy for reverse proxy routing with valid TLS via Cloudflare DNS-01 challenge.

---

## Services

| Service | Role |
|---------|------|
| [OPNsense](https://opnsense.org/) | Router / firewall (VLAN routing, NAT, Unbound) |
| [Home Assistant](https://www.home-assistant.io/) | Home automation, BLE presence tracking, dashboards |
| [Caddy](https://caddyserver.com/) | Reverse proxy with automatic HTTPS (Cloudflare DNS-01) |
| [AdGuard Home](https://adguard.com/en/adguard-home/overview.html) | Network-wide DNS filtering |
| [Wazuh](https://wazuh.com/) | SIEM — vulnerability detection, security monitoring |
| [Vaultwarden](https://github.com/dani-garcia/vaultwarden) | Self-hosted Bitwarden-compatible password manager |
| [Gitea](https://gitea.io/) | Self-hosted Git (also used for Obsidian vault sync) |
| [Paperless-ngx](https://docs.paperless-ngx.com/) | Document management system |
| [Uptime Kuma](https://github.com/louislam/uptime-kuma) | Service monitoring and status page |
| [NTFY](https://ntfy.sh/) | Push notifications |
| [Homepage](https://gethomepage.dev/) | Dashboard |
| [UniFi OS Server](https://ui.com/) | Network controller for UniFi AP |

---

## What I'm Working On

- Finishing **Cisco NetAcad Network Technician** career path
- Preparing for **CompTIA Security+ (SY0-701)**
- Adding a second Proxmox node (Pi 5) for backup services
- Documenting everything properly here

---

## Contact

- LinkedIn: [kuzin-viacheslav](https://linkedin.com/in/kuzin-viacheslav)
