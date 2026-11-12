# Immich

[Overview](../README.md) · [Backups and recovery](../docs/backups-and-recovery.md)

## Why I use Immich

I use Immich for my photos and videos. It gives me automatic backup from my phone, a web gallery and search, while keeping the main library on my own hardware.

It is one of the services I built the lab around: somewhere to keep my photos, browse them and have them included in my backup routine.

## How it runs

Immich runs in a Linux container on Cubi, with Docker Compose managing the application and its supporting services.

Caddy provides HTTPS, and I use Authentik to sign in. That also works from the Immich app on my iPhone.

## Storage and backups

I used to keep the photo library outside the container, which meant backing it up separately. Now the photos, database and settings all live inside the Immich container and are included in its full Proxmox backup.

A local copy goes to the backup SSD on Cubi, and a copy is kept in Backblaze B2.

Keeping the database with the photos matters: the files alone do not preserve albums, recognised faces and the rest of the library information.

The archive and its cloud copy have been checked. I have not yet restored the current Immich setup from that backup and checked it through the application.

The [backup page](../docs/backups-and-recovery.md) covers the schedule and cloud checks.

## Compose example

The [Compose file in this repository](docker-compose.yml) is a reference example, with variables for storage paths, credentials and the Immich version.

My running installation uses specific pinned releases. I review the release notes before updating, especially when an update changes the database.

Photos, database contents and credentials are not included in this repository.
