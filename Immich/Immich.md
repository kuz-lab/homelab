# Immich

Immich is my replacement for cloud photo backup. It runs in a Linux container on Cubi, with Docker containers for the application, its machine-learning component, the database and the cache.

[Overview](../README.md) · [Backups and recovery](../docs/backups-and-recovery.md)

## Data storage

The library lives on Cubi's second SSD and is mounted into the LXC:

`/mnt/pve/data1/immich` → `/mnt/immich-media`

Keeping it out of the container's root filesystem means the container can be rebuilt without touching the photos. It also means the photos are not in the container's backup — which is the part worth knowing about.

The database sits at `/opt/immich/postgres` inside the LXC, and Caddy forwards the web interface to port 2283.

## Backups

The Proxmox backup log excludes the media bind mount, so the library has its own transfer to Backblaze B2 alongside the LXC archive.

A usable restore needs both: the media and the database. Photos alone lose the albums, the metadata and the face recognition. I have copies of both; I have not yet rebuilt the service from them, so I would not call it a tested recovery. [Official backup guidance](https://docs.immich.app/administration/backup-and-restore/)

The [lab backup notes](../docs/backups-and-recovery.md) have the schedule.

## Compose example

The [published Compose file](docker-compose.yml) uses variables for the storage paths, the database credentials and the Immich version. It is a reference rather than an export of the running deployment.

One thing to change before using it: the version variable has a moving default, so the file on its own does not pin a release. Immich moves fast and its database migrations are one-way — pick a version deliberately and read its release notes.
