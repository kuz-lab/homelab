# Selected Services

These are the parts of the lab I use and document here. Locations and runtimes were checked on 6 September 2026; this is a selected inventory, not everything installed.

[Overview](../README.md) · [Network](network-and-access.md) · [Backups](backups-and-recovery.md)

## Everyday use

| Service | Where it runs on Cubi | What I use it for | Notes or example |
| --- | --- | --- | --- |
| Home Assistant | VM 202 | Home automation and device dashboards | [Home Assistant](../HomeAssistant.md) |
| Immich | LXC 106, Docker | Photos and videos | [Setup and data storage](../Immich/Immich.md) |
| Paperless-ngx | LXC 103, Docker | Documents, with IMAP intake | [Compose example](../Paperless/docker-compose.yml) |
| Vaultwarden | LXC 107, Docker | Password management | No configuration published |
| Actual Budget | LXC 105, Docker | Personal finances | [Compose example](../Actual/docker-compose.yml) |
| Node-RED | LXC 104, Docker | Home-automation flows | [Compose example](../Node-RED/docker-compose.yml) |
| Stirling PDF | LXC 115, Docker | PDF tools | No configuration published |

An LXC is a Linux container managed by Proxmox. For the Docker services it gives the application and its supporting containers their own Linux environment, so each one runs its own Docker daemon rather than sharing a single socket across the whole host.

## Network and management

| Service | Location | Runtime | Purpose |
| --- | --- | --- | --- |
| OPNsense | VM 108 on ZimaBoard | — | Router and firewall |
| UniFi OS Server | VM 201 on Cubi | — | Switch and access-point management |
| Wazuh | VM 200 on Cubi | — | Log collection and vulnerability alerts |
| AdGuard Home | LXC 102 | native | Client DNS filtering |
| Caddy | LXC 109 | Docker | HTTPS entry point for the web applications |
| Gitea | LXC 101 | native | Private configuration repository |
| Portainer | LXC 110 | Docker | Managing the Docker environments |
| ntfy | LXC 112 | native | Push notifications |
| Uptime Kuma | LXC 114 | native | Availability monitoring |

[How Caddy is set up](../Caddy/Caddy.md) · [Network design](network-and-access.md)

## Monitoring and dashboards

I run several monitoring tools because each answers a different question, and they overlap less than the list suggests.

| Tool | The question it answers |
| --- | --- |
| Uptime Kuma | Is a host or service reachable? |
| Beszel | What are CPU, memory, storage and temperature doing right now? |
| Grafana + InfluxDB 3 | How have the measurements changed over weeks and months? |
| Wazuh | What needs patching, and what showed up in the logs? |
| PeaNUT | What is the UPS reporting? |
| ntfy | How does any of this reach my phone? |
| Homarr | Where do I see all of it on one page? |

Grafana and InfluxDB 3 run in LXC 100; Beszel's hub and PeaNUT share the Portainer LXC. The Beszel agents run on the Proxmox hosts themselves rather than inside a container, because they need to read real hardware temperatures rather than a value passed through Home Assistant. [Metrics details](../Metrics/Metrics.md)

Homarr is the main dashboard now. Homepage was the first one and still runs; retiring it is on the list, held up by a few monitors and a firewall rule that still point at it. Its [Compose example](../Homepage/docker-compose.yml) is kept for reference.

### Wazuh and patching

I use Wazuh's vulnerability alerts and logs to decide what needs attention. The setup also includes ntfy notifications and a daily CVE digest. Its role here is to support patching and investigation, not to certify that every service is secure.

Learning to use Wazuh and seeing the CVE reports across different services prompted me to look more closely at updates. A service could be running normally while its underlying packages still needed attention. That made vulnerability reports a useful companion to the uptime dashboard.

## Configuration and management

For the Git-backed Portainer stacks, I edit the Compose files in a private Gitea repository, push the changes, then redeploy from Portainer. Credentials are supplied separately through environment settings or private files rather than included in the public examples.

Some dashboard integrations use Docker socket proxies to restrict the API operations they can request. Permissions differ between integrations; the proxies are not a single protection layer for everything. Portainer agents also have direct Docker socket access, which needs to be treated as privileged access to their Docker environments.

The compose files published here are examples. Local paths, secrets and some current settings are not included, so read the service notes before reusing one.

My initial Ansible use was a fleet audit and a few service tasks. The access setup later gained a `common` role for users, SSH keys and sudo. The larger automation environment that developed afterwards is outside the scope of this repository. [SSH history and access model](network-and-access.md#administration)
