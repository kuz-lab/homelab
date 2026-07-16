# Metrics (Grafana + InfluxDB 3)

This is my metrics stack — Grafana for the dashboards and InfluxDB 3 Enterprise for the time-series data behind them. It runs in its own LXC (CT 100) on Cubi with Docker Compose. Wazuh tells me when something is insecure or broken; this tells me how everything is behaving over time.

## The 2.x → 3 story

I started on InfluxDB 2.9.1 and moved to InfluxDB 3 Enterprise a few days later, while I still only had about five days of data. Because there was nothing worth keeping yet (no weekly trends, no monthly comparisons), I did a clean cutover instead of running both side by side — pulled Home Assistant off v2, pointed it at v3, and repointed the Proxmox metric servers.

The main thing to know about v3: it dropped the built-in task engine that v2 had for downsampling. So if I want long-term rollups later, I'll need an external scheduler to do it. For now the raw data is fine.

The old v2 stack is stopped but still on the host as a fallback reference until the v3 setup has proven itself over a longer stretch.

## What it collects

- **Home Assistant** — ~55 entities: energy (homelab total, DrayTek, UPS, workspace, kitchen), climate (room temps, Eve TRV valve positions), window contacts, weather, air quality, and infrastructure health like CPU and rack temperatures.
- **Proxmox** — both hosts (Cubi and ZimaBoard) report in via the built-in metric server.

There are two databases, `haos` and `proxmox`, kept separate. Grafana reads them over SQL (Flight SQL / gRPC) rather than the old Flux queries — the visual query builder in Grafana works with SQL, which makes building panels a lot less fiddly.

There's also InfluxDB Explorer running at `explorer.kuzlab.dev` for poking at the data directly.

## Current setup

Two stacks, deployed two different ways:

- **Grafana** lives in a Compose file at `/etc/metrics/` (alongside the stopped legacy v2 container).
- **InfluxDB 3 Enterprise** runs as a Portainer stack rather than an `/etc` file, since I moved container management onto Portainer around the same time.

The files here:

- [`docker-compose.yml`](docker-compose.yml) — the Grafana / legacy-v2 stack (`/etc/metrics/`)
- [`influxdb3-compose.yml`](influxdb3-compose.yml) — the InfluxDB 3 Enterprise stack (Portainer)

Updates follow the same workflow as the rest of my Docker services: `docker compose pull && docker compose up -d`.

## One gotcha worth noting

Scoped resource tokens return a 403 on InfluxDB 3 Enterprise's v2 write-compatibility API — a known behavior. So the Proxmox metric servers use an admin token, while Home Assistant writes with a scoped `ha-writer` token. Grafana's service account also needs the `server.stats:read` permission, which is new in Grafana v13.

## Repository Scope

This folder is the clean, public version. Secrets — admin and scoped tokens, Grafana credentials — stay on the host in the local environment files and are never committed.

For related incidents and fixes, check out my [Troubleshooting](../TROUBLESHOOTING.md) notes.
