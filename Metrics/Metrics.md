# Metrics (Grafana + InfluxDB)

This is my observability stack — Grafana for dashboards and InfluxDB for the time-series data behind them. It runs in its own LXC (CT 100) on Cubi, deployed with Docker Compose. Wazuh already tells me when something is insecure or broken; this stack tells me how everything is *behaving* over time.

## Why InfluxDB 2.x (and not v3)

I looked at InfluxDB v3 but deliberately stayed on 2.x. The 2.x line has the complete Flux ecosystem and a built-in task engine for downsampling, which is exactly what I need for keeping long-term history without letting the database grow forever. v3 dropped the built-in downsampling task engine, so for a small always-on homelab it was the wrong trade. My whole pipeline — Home Assistant → InfluxDB → Grafana, plus Proxmox metrics — is built around Flux, and it works.

## What it collects

- **Home Assistant** pushes ~55 entities into InfluxDB: energy and power (watts), climate, TRV valve positions, temperatures, weather, air quality, and general infrastructure health.
- **Proxmox** — both hosts (Cubi and ZimaBoard) report their own metrics into a separate `proxmox` bucket, kept apart from the Home Assistant data.

Grafana renders all of it with Flux queries. For power I use `_measurement = W` for watts with `entity_id` as a tag, which keeps the dashboards easy to build.

## Current setup

Everything lives under `/etc/metrics/` on the host and runs via Docker Compose:

- [`docker-compose.yml`](docker-compose.yml) — InfluxDB + Grafana container definitions

Persistent data (InfluxDB buckets, Grafana dashboards, and settings) is stored on host volumes so it survives container recreation and updates. Updates follow the same workflow as the rest of my Docker services: `docker compose pull && docker compose up -d`.

## Repository Scope

This folder contains the clean, public version of the setup. Secrets — admin tokens and API credentials — are not included; they stay only on the host in the local environment file.

For related incidents and fixes, check out my [Troubleshooting](../TROUBLESHOOTING.md) notes.
