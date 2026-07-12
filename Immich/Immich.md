# Immich

Immich is my self-hosted replacement for cloud photo backup. It runs in its own LXC (CT 106) on Cubi, deployed with Docker Compose using the official Immich method. I get a phone app and a web UI for photos and videos, without handing my library to a third party.

## Why self-host it

Photos are the one thing I really didn't want living only on someone else's servers. Immich gives me the parts I actually used a cloud service for — automatic phone backup, browsing, search — while keeping the whole library on my own hardware and inside my own backup routine.

## Current setup

- Deployed with the **official Docker Compose** method on Debian 13.
- The photo and video library is **bind-mounted from the Cubi SSD** (`/mnt/pve/data1/immich` → `/mnt/immich-media`) rather than living inside the container, so the media is easy to back up and independent of the container lifecycle.
- Accessible at `immich.kuzlab.dev`, proxied by Caddy to the container on port `2283`.

The key file:

- [`docker-compose.yml`](docker-compose.yml) — Immich server, machine-learning, Redis, and Postgres services

Updates are pinned to a release tag and applied deliberately after a changelog review — Immich moves fast and I'd rather not get surprised by a breaking database migration.

## Backups

The media library is included in my offsite Backblaze B2 sync via a dedicated `rclone sync` block, so photos follow the same 3-2-1 rule as everything else in the lab: local vzdump of the container, plus the media synced offsite.

## Repository Scope

This folder contains the clean, public version of the setup. Secrets — database passwords and any API keys — live in a local environment file that is not committed.

For related incidents and fixes, check out my [Troubleshooting](../TROUBLESHOOTING.md) notes.
