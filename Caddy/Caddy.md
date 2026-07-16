# Caddy

Caddy is the reverse proxy for my homelab. I use it to expose internal services through clean local hostnames (`*.kuzlab.dev`), with HTTPS handled automatically. Certificate validation is done via Cloudflare DNS-01, meaning I don't need to expose my services publicly just to get valid TLS certificates.

It runs in its own LXC on my Cubi host. The container has one simple job: run the proxy and keep its configuration separate from the services behind it.

## Why Caddy?

When I first bought a domain to make my services easier to access, my first attempt at a reverse proxy was Nginx Proxy Manager. I thought a GUI would make things easy, but after a few frustrating and failed attempts, I gave up. I searched for an alternative, found Caddy, followed a basic forum tutorial, and it worked immediately. No fighting a GUI, just simple configuration. Over time, my Caddyfile evolved based on official docs and community forums.

## What broke along the way

My setup evolved through trial and error. The initial installation was native Caddy with the Cloudflare module compiled in. It broke completely after the first `apt upgrade` — the plugin didn't survive. 

To avoid that maintenance headache, I switched to a community Docker image that already bundled the plugin. I initially ran this via a systemd unit with a massive `docker run` command, but that eventually broke after a restart too. On top of that, I learned a hard lesson about data persistence: because I didn't mount a `/data` directory in that early setup, my certificates vanished every time the container was recreated.

That pushed me to rethink the whole approach.

## Current Setup

Today it all runs via Docker Compose using the `ghcr.io/caddybuilds/caddy-cloudflare:latest` image. It's just one `.yml` file — much easier to update and keep in version control.

The key files are:
- [`Caddyfile`](Caddyfile) — reverse proxy rules
- [`docker-compose.yml`](docker-compose.yml) — container definition
- `/etc/caddy/.env` — local environment file for the Cloudflare API token

Persistent data is now safely stored outside the container so certificates and configs survive updates:
- `/var/lib/caddy-data:/data` — certificates and ACME account
- `/var/lib/caddy-config:/config` — runtime config cache

## Repository Scope

This folder contains the clean, public version of my Caddy setup. Secrets are not included — the real Cloudflare API token stays only on the host.

For related incidents and fixes, check out my [Troubleshooting](../TROUBLESHOOTING.md) notes.