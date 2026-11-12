# Selected Services

These are the services I use for photos, documents, home automation and the lab itself.

[Overview](../README.md) · [Hardware and setup](../SETUP.md) · [Network](network-and-access.md) · [Backups](backups-and-recovery.md)

## Everyday use

| Service | What I use it for |
| --- | --- |
| Home Assistant | Home automations, heating and device controls. |
| Node-RED | Connecting devices and services into home-automation flows. |
| Immich | My photos and videos. |
| Paperless-ngx | Keeping documents organised and easy to find. |
| Vaultwarden | Passwords across my devices. |
| Actual Budget | My budget and transactions. |
| Finance Hub | Reviewing receipts, spending and subscriptions. |
| Stirling PDF | Everyday PDF tasks. |
| Workbench (AI agent harness) | Working with agents and keeping their results in one place. |

A separate private web application brings together personal dashboards, reports and Workbench conversations. Fredy is also installed for housing searches.

[Home Assistant](../HomeAssistant.md) · [Immich](../Immich/Immich.md) · [Workbench use cases](workbench.md)

## Network and management

| Service | What I use it for |
| --- | --- |
| OPNsense | Routing and firewall rules for the home network. |
| UniFi | Managing the switch and Wi-Fi. |
| Technitium DNS | DNS on Cubi and the Raspberry Pi. |
| Caddy | HTTPS for my web applications. |
| Authentik | One sign-in for the apps I’ve connected to it. |
| Gitea | Keeping my code and configurations. |
| Portainer | Managing the Docker applications. |

[How Caddy is set up](../Caddy/Caddy.md) · [Network design](network-and-access.md)

## Monitoring and dashboards

Homepage is where I open the applications and check the lab at a glance.

| Tool | What I use it for |
| --- | --- |
| Uptime Kuma | Service availability and outage history. |
| Gatus | Checking services from the Pi, independently of Cubi. |
| Healthchecks.io | Getting an alert when my home internet goes down. |
| Beszel | CPU, memory, temperatures and storage across the three hosts. |
| Grafana + InfluxDB 3 | Tracking electricity use and running costs. |
| Wazuh | Reviewing security events and vulnerabilities. |
| PeaNUT | Checking the UPS. |
| Pushover | Receiving alerts on my phone. |

If my home internet goes down, the lab can’t send me an alert. Healthchecks.io notices that the Pi has stopped checking in and sends a Pushover notification from outside my network.

Keeping the lab running costs about €13 a month in electricity, including the UPS. [Here’s October as an example](../SETUP.md#running-cost).

ntfy remains for older integrations. [Homepage screenshot](../SETUP.md#homepage) · [Metrics notes](../Metrics/Metrics.md)

### Wazuh and patching

Wazuh got me looking more closely at updates: a service could be running normally while its packages still needed attention.

Audit collects information about the machines. Scheduled OS maintenance runs on Cubi, checks the results of updates, and feeds fresh findings into Workbench for analysis of the remaining CVEs. [How the update cycle works](workbench-internals.md#audit-updates-and-remaining-cves).

## Configuration and management

I manage the lab from my Mac and keep configurations in a private Gitea repository. Portainer handles the Docker stacks, and I use Ansible for selected administration tasks.

The Compose files here are examples, not copies of the running setup:

[Paperless](../Paperless/docker-compose.yml) · [Actual Budget](../Actual/docker-compose.yml) · [Node-RED](../Node-RED/docker-compose.yml) · [Homepage](../Homepage/docker-compose.yml)

[SSH history and access model](network-and-access.md#administration) · [How Workbench works](workbench-internals.md)
