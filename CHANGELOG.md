# Lab Changelog

How the lab has changed, month by month. Entries describe what was done at the time.

[Back to the overview](README.md)

## September 2026

- Checked the documentation against the running systems and corrected what had drifted: the Raspberry Pi's actual state, the backup schedules, and the InfluxDB ports in the published Caddy example.
- Reorganised the notes into separate pages for the network, the services and the backups.
- Updated the rack photo, clarified the SSH access history, and separated the planned Pi bastion from the current Cubi setup. Corrected the public configuration examples without deploying changes to the lab.

## August 2026

- Got remote Virtual Desktop access working from a Meta Quest 3 over mobile data, after finding three separate NAT and firewall faults that each looked like a carrier problem. [Case study](docs/virtual-desktop-remote-access.md)

## July 2026

- Developed the earlier manual SSH-key setup into a Cubi bastion with ProxyJump and connection aliases. Added regular-user access and a separate Ansible key. [Access model and later checks](docs/network-and-access.md#administration)
- Upgraded OPNsense from 26.1 to 26.7, with a snapshot for rollback.
- Started using Ansible: a key-based inventory of the fleet and a first audit playbook covering OS version, disk and pending updates in one run.
- Moved Docker services to Portainer stacks backed by a private Gitea repository, with changes pushed to Git and redeployed from Portainer.
- Documented volumes, environment variables and operational notes for each container.
- Added admin authentication to Node-RED, more Uptime Kuma monitors, and a review of what the backups actually covered.

## June 2026

- Moved metrics from InfluxDB 2 to InfluxDB 3 Enterprise and rebuilt the Grafana dashboards on SQL queries, while there was still only a few days of history to lose. [Metrics notes](Metrics/Metrics.md)
- Deployed Wazuh for log collection and vulnerability alerts, with a daily CVE digest through ntfy.

## May 2026

- Split the network into Management, Servers, Trusted, IoT and Guest VLANs with inter-VLAN traffic denied by default.
- Moved OPNsense onto its own ZimaBoard host, so maintenance on the services machine no longer takes the network down with it.
