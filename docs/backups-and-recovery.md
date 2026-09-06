# Backups and Recovery

Local Proxmox backups to a separate SSD, with selected copies going off-site to Backblaze B2. The part that matters is not having archives — it is knowing whether they contain everything needed to bring a service back.

[Overview](../README.md) · [Services](services.md) · [Troubleshooting](../TROUBLESHOOTING.md)

## What is stored where

| Data | Local | Off-site |
| --- | --- | --- |
| VM and LXC backups | Proxmox vzdump archives on Cubi's separate SSD | Selected archives copied to B2 |
| OPNsense VM | Backed up from ZimaBoard to Cubi over NFS | Included in the archive transfer |
| Immich media | The original library on Cubi's SSD, outside the LXC root filesystem | Its own separate transfer to B2 |
| Application state | Service-state archives | Encrypted transfer, only if the local state run succeeded |

The media folder is the working library, not a second local copy. The photo backup design therefore has two locations — local media and B2 — rather than a full three-copy arrangement.

## Schedule

Times are local.

| Job | Schedule |
| --- | --- |
| OPNsense VM | Mon, Wed, Fri at 03:00 |
| Critical services — Gitea, Paperless, Vaultwarden, Immich | Mon, Wed, Fri at 03:30 |
| Supporting services — metrics, Caddy, dashboards | Mon and Wed at 04:00 |
| Application state | Mon, Wed, Fri at 05:00 |
| Transfer to B2 | Mon, Wed, Fri at 08:00 |
| Windows VM | Monthly |

Some of these use stop mode, which interrupts the guest for the duration. They are scheduled maintenance windows, not zero-downtime backups.

## The thing a Proxmox archive does not include

A vzdump archive does not necessarily contain directories mounted in from the host. The Immich backup log excludes its media bind mount explicitly — which is correct behaviour, and also exactly the kind of detail that turns a backup into a false sense of security. That media needs its own path off the machine, which is why it has a separate B2 transfer.

Immich also needs its database; a copy of the photos alone does not preserve albums, faces or metadata. [Immich's own backup guidance](https://docs.immich.app/administration/backup-and-restore/)

Synchronising off-site is also not the same as keeping history. Retention and recovery from an accidental deletion are a separate question from "the file is in the bucket".

## Known gap

The 6 September review found that the last overall success marker for the application-state job was **23 August**. The 4 September run failed, and the B2 state-transfer step skipped the stale state archive. The marker does not establish when the first failure happened. Repairing this job is still open.

Local logs reported successful Proxmox-archive and Immich-media transfer steps on 4 September, but the combined B2 job was not fully successful because its state step was skipped. Remote objects and a restore from B2 were not verified in that review.

## Restore experience

I have restored Home Assistant into a different VM ID as a drill, and it came back. That is one service, once — evidence that the chain works for that case, not that every service is currently recoverable.

A further service restore drill is the next step. It needs to establish:

- which archive, database and media pieces a given service actually needs;
- whether the credentials and settings can be recovered securely;
- whether the restored application can open its own data;
- whether the whole thing can run without touching the working service.

## Power and internet failures

An Eaton Ellipse PRO 650 carries the lab. Cubi is the NUT master and ZimaBoard is a network slave. On low battery, ZimaBoard goes down first — taking the network with it — and Cubi then shuts its guests down in tiers before the UPS cuts power. I tested that sequence and the automatic recovery when it was built; I have not repeated it since.

The [earlier power and WAN recovery diagram](../diagrams/power-wan-recovery.png) records that design, including the timings used at the time.

For internet failures the path is a software recovery attempt first, then a modem power cycle through a Home Assistant-controlled smart plug. [The upload-bandwidth incident](../TROUBLESHOOTING.md#backup-uploads-and-internet-drops) is why that exists.

Appliance backups, passwords and recovery keys are not published here.
