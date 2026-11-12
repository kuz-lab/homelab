# Caddy

[Overview](../README.md) · [Network and access](../docs/network-and-access.md) · [Backups and recovery](../docs/backups-and-recovery.md)

## Why Caddy

I bought a domain so I could open my services by name instead of remembering IP addresses and ports.

I started with Nginx Proxy Manager, but could not get it working the way I wanted. Then I found a Caddy tutorial on a forum, tried it, and got a working setup. From there, I added services as I needed them.

## What went wrong

My first installation was a native Caddy build with the Cloudflare DNS module compiled in. A package upgrade replaced it with a standard build, and the module disappeared.

I switched to a Docker image that already included it. At first, I used a long `docker run` command inside a systemd unit. Later I moved the settings into Compose, which made them easier to read and maintain.

I also learned why Caddy needs persistent storage. Without a saved `/data` directory, recreating the container threw away its certificates and certificate account data. Caddy then had to request certificates again.

Those experiences shaped the setup I use now.

## How I use it now

Caddy runs through Docker Compose in its own Linux container on Cubi. It provides HTTPS and sends requests to the right application.

It also serves my private website and routes requests to the services behind it, including the Workbench interface (AI agent harness).

These services are normally reached from my home network or through Tailscale. Authentik handles shared sign-in for the applications connected to it; Caddy handles their HTTPS addresses and routing.

## Certificates and backups

Caddy uses Cloudflare to create the DNS records needed to prove that I control the domain. The certificates are issued by a certificate authority. This lets me use valid HTTPS certificates without opening inbound ports just for certificate validation.

A later issue involved the lab’s internal DNS. It could hide the public records used for certificate checks, so I configured Caddy to use external DNS servers for that step.

The routing configuration, certificates and saved Caddy state live outside the Docker container, inside the Caddy LXC. They survive Docker container recreation and are included in the full LXC backup.

The [backup page](../docs/backups-and-recovery.md) explains where those copies go and how they are checked.

## Example files

- [Caddyfile](Caddyfile) — a selection of service routes.
- [Compose example](docker-compose.yml) — the Docker setup with persistent storage.

These are reference examples, not a complete copy of my private configuration. The running installation uses a pinned image, and the Cloudflare credential stays outside Git.

The Compose example does not publish Caddy’s management port. Some routes in the example still skip certificate verification when connecting to an internal HTTPS service; that is a limitation of those routes.

[More troubleshooting notes](../TROUBLESHOOTING.md)
