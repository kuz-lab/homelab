# Lab Changelog

How the lab has changed, month by month. Entries describe what was done at the time.

[Back to the overview](README.md)

## November 2026

- Added a server-side task queue to Workbench (AI agent harness), with priorities and scheduled starts. Larger assignments can now use a small team of agents, with planning, separate tasks and a combined result. The private website brings assignments, chats, history and automation runs together. [How Workbench works](docs/workbench-internals.md)
- Added automatic checks and corrections for selected project documentation. One agent prepares a change, another reviews it, and the integration checks the files before saving it.
- Extended Finance Hub with automatic expense categorisation under the rules I enabled. Budget reviews now run weekly and when significant changes need another look.
- Added saved Zenarmor observations and daily Workbench analysis, with explanations on the private dashboard.
- Set up a daily maintenance cycle on Cubi: collect an Audit report, apply permitted system updates, check the services and vulnerabilities again, then send the remaining findings to Workbench for analysis. [The update cycle](docs/workbench-internals.md#audit-updates-and-remaining-cves)
- Closed the gaps in cloud-backup coverage. All 23 Proxmox guests and the Raspberry Pi now have at least one verified copy in Backblaze B2. The four missing guest backups were uploaded with encryption and checked by downloading them again. The upload job now skips copies it has already verified. [Backups and recovery](docs/backups-and-recovery.md)
- Reworked the Grafana energy view around electricity use and running costs. October provides a monthly example: about €13 for the whole homelab, including the UPS. [Running cost](SETUP.md#running-cost)
- Updated the 3D apartment dashboard in Home Assistant and on the private website, and added a phone reminder for windows left open when the entrance door opens.
- Updated the public portfolio with current photos, service placement, network details, backups and Workbench examples.

## October 2026

- Built a personal console for Codex and Claude, then connected conversations to the private website. I could continue work from a browser and return to saved conversations.
- Added daily document review in Paperless. Workbench suggests titles, tags and document types; clear cases can be applied through the integration, while uncertain ones stay for review.
- Connected receipt review with Actual Budget. Codex and Claude read the receipt text independently, and the integration compares their answers and looks for matching transactions.
- Expanded recurring research for career planning, product choices and price comparisons, with dated results kept on the private website. [Workbench use cases](docs/workbench.md)
- Replaced the two AdGuard DNS instances with Technitium on Cubi and the Raspberry Pi, keeping the existing resolver addresses.
- Deployed Authentik and started connecting applications to a shared sign-in service, including passkey login.
- Reworked the Home Assistant heating automations so schedules, ventilation and manual controls work together. Connected the work calendar I edit on my phone.
- Added HA Observer, giving Workbench read-only access to selected device states and a separate notification process for new availability problems. [Home Assistant](HomeAssistant.md)
- Added scheduled Raspberry Pi system backups to Cubi and verified off-site copies in Backblaze B2.

## September 2026

- Moved application data back inside eight existing LXC containers, so native Proxmox backups include each container’s data and settings together.
- Connected Wazuh to Workbench for automatic analysis of vulnerability findings, with the results available on the private dashboard.
- Put the Raspberry Pi to work as a second DNS server and a separate monitoring node. Added an external Healthchecks.io heartbeat so an alert can still reach me when the home internet connection goes down.
- Deployed Finance Hub behind private HTTPS, with scheduled data refreshes and a full-container backup.
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

- Moved metrics from InfluxDB 2 to InfluxDB 3 Enterprise and rebuilt the Grafana dashboards on SQL queries, while there were still only a few days of history to lose. [Metrics notes](Metrics/Metrics.md)
- Deployed Wazuh for log collection and vulnerability alerts, with a daily CVE digest through ntfy.

## May 2026

- Split the network into Management, Servers, Trusted, IoT and Guest VLANs with inter-VLAN traffic denied by default.
- Moved OPNsense onto its own ZimaBoard host, so maintenance on the services machine no longer takes the network down with it.
