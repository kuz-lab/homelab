# Troubleshooting Notes

Problems I ran into running this lab: what I saw, what I checked, and what I changed. These are accounts of one setup, not universal fixes.

[Overview](README.md) · [Network](docs/network-and-access.md) · [Changelog](CHANGELOG.md)

## Backup uploads and internet drops

### What happened

The internet dropped a handful of times over about two months. I have a WAN watchdog on OPNsense that restarts the PPPoE connection when it detects a failure, but that was not enough — the DrayTek modem itself was freezing, and I had to power-cycle it by hand.

The DSL line's SNR margin was around 5.7 dB. I was running scheduled rclone backups to Backblaze B2 and had added `--bwlimit 30M` to leave upload capacity available. The drops kept happening anyway.

After the last one I went back to the watchdog log:

```text
2026-05-29 08:14:03 ALL hosts unreachable
```

The backup started at 08:00. The failure came fourteen minutes later, which made the upload worth investigating.

### What I found

I had misread the flag. In rclone, `30M` means 30 **MiB per second**, not 30 megabits — roughly 250 Mbps against an upstream of about 47 Mbps. The limit was above the line's capacity, so it could not reserve any upload bandwidth. [rclone bandwidth documentation](https://rclone.org/docs/#bwlimit-bwtimetable)

### What changed

I set `--bwlimit 3.5M` — about 29 Mbps, roughly 60% of the upstream — and watched the OPNsense traffic graphs through the next backup. Upload stayed near that level. No further drops were recorded during the follow-up described in my original notes.

I also added a recovery path for the times the modem does freeze: the watchdog attempts a software restart first, and if that fails it calls a Home Assistant webhook that power-cycles the modem through a smart plug.

The timing and the ineffective bandwidth limit made upload saturation a useful lead. The improvement after the change supports that explanation, but does not prove why the modem became unresponsive.

What I took from it: check the units before replacing the hardware.

## UniFi adoption across networks

### What happened

My U6 Plus access point died after a power cycle — solid white LED, no ping, no ARP entry, and no response to the reset button after twenty seconds of holding it. I got a refund and replaced it with a U7 Lite.

The UniFi controller runs on the Servers VLAN and the access point sits on Management. In my setup, a replacement device did not have a working way to discover its controller across those networks.

Moving the controller would have meant changing its proxy route, dashboard links and firewall rules. I kept it on Servers and investigated how the access point was looking for it.

### What I found

The U7 Lite came up on PoE, took an address and answered pings. In the controller it appeared as a generic client, not as an access point waiting to be adopted. Ping established basic reachability; it did not test controller discovery or the adoption connection.

I opened a shell on the access point and found it trying to resolve the hostname `unifi`, with no DNS record to answer it. I pointed it at the controller directly:

```sh
set-inform http://192.168.40.18:8080/inform
```

It adopted immediately.

### What changed

I added a DNS override in Unbound for `unifi.localdomain` and set the matching inform-host override in the controller. Devices using that resolver can find the name; routing and firewall rules still control whether they can connect. My documented adoption procedure is to adopt a new device on the controller's VLAN first and move it to Management afterwards.

This was a discovery problem during adoption. It is not evidence that an adopted access point loses its controller on every reboot, and DNS is only part of it — routing and firewall rules still have to allow the connection.

The takeaway: a successful ping was useful evidence, but it was only the first test.

## Caddy configuration and certificate storage

A package upgrade removed the Cloudflare module from my early native installation, and later, recreating the Docker container without persistent storage threw away the certificates and the ACME account data.

The [Caddy notes](Caddy/Caddy.md#what-went-wrong) cover the move to Compose and to host directories that survive the container.

## Remote Virtual Desktop over the internet

A VR connection from outside the house initially looked like a mobile-carrier problem. A WAN packet capture showed the connection attempts arriving. That moved the investigation back to my own NAT and firewall configuration, where I found three contributing faults.

[Read the full case study](docs/virtual-desktop-remote-access.md). It describes a setup with internet-facing port forwards, which is deliberately separate from how the rest of the lab is reached.
