# Caddy

Caddy gives my web applications readable names and HTTPS. It runs in its own Linux container on Cubi.

[Overview](../README.md) · [Network and access](../docs/network-and-access.md)

## Why I chose it

I bought a domain for the lab and started with Nginx Proxy Manager. I could not get it working the way I wanted, so I tried Caddy using a forum tutorial. Once it worked, I added routes as I needed them.

## What went wrong

My first installation was a native build with the Cloudflare DNS module compiled in. A package upgrade replaced it with a stock build, and the module was gone.

I moved to a Docker image that included it. At first I started that with a long `docker run` command wrapped in a systemd unit. Later I moved the settings into Compose, where they were easier to review and change.

Without a persistent `/data` directory, recreating the container also threw away the certificates and ACME account data. Caddy had to obtain certificates again. The state now lives on the host and survives container recreation.

## Current arrangement

| Host path | Container path | Purpose |
| --- | --- | --- |
| `/etc/caddy/Caddyfile` | `/etc/caddy/Caddyfile` | Routing configuration, mounted read-only |
| `/var/lib/caddy-data` | `/data` | Certificates and ACME account |
| `/var/lib/caddy-config` | `/config` | Runtime configuration |
| `/var/log/caddy` | `/var/log/caddy` | Logs |

Caddy uses Cloudflare's API to create DNS validation records. A certificate authority then issues the certificates; Cloudflare is the DNS provider in this process. This does not require opening inbound ports for certificate validation. [Caddy DNS-01 documentation](https://caddyserver.com/docs/automatic-https#dns-challenge)

## Files here

- [Caddyfile](Caddyfile) — a selection of the service routes.
- [Compose example](docker-compose.yml) — the container definition; it reads its Cloudflare token from a private environment file at `/etc/caddy/caddy.env`.

The public Compose example no longer publishes the admin API port, because it controls Caddy's configuration. This is a repository change, not a change to the running deployment. [Admin API documentation](https://caddyserver.com/docs/api)

Some HTTPS upstreams in the Caddyfile use `tls_insecure_skip_verify` for their local certificates. That skips upstream identity verification; trusting an appropriate certificate authority is the stronger arrangement. The published file records this limitation rather than hiding it.

[More troubleshooting notes](../TROUBLESHOOTING.md)
