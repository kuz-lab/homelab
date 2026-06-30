# Troubleshooting Notes

Two real problems I ran into while running this lab, what I found, and how I fixed them.

---

<details>
<summary><strong>Recurring internet drops — rclone backup was saturating the DSL line</strong></summary>

### The problem

Internet dropped a few times over two months. I have a WAN watchdog on OPNsense that detects failures and restarts the PPPoE connection, but the DrayTek modem itself was freezing — software restart wasn't enough, I had to power-cycle it manually.

My DSL line has a low SNR margin (5.7 dB), so I knew heavy uploads could be a problem. I was running a daily rclone backup to Backblaze B2, and I added `--bwlimit 30M` to the script to limit the bandwidth and avoid stressing the line. The drops kept happening anyway.

### What I found

After the last drop I checked the watchdog log:

```
2026-05-29 08:14:03 ALL hosts unreachable
```

Backup starts at 08:00. Failure 14 minutes later. That timing was suspicious.

I went back to the [rclone docs on bandwidth limiting](https://rclone.org/docs/#bwlimit-bandwidth-spec) and realized the problem — `30M` in rclone means 30 megabytes per second, not 30 megabits. 30 MiB/s is roughly 240 Mbps. My upstream is 47 Mbps. The flag was doing nothing — rclone was still sending at full speed, the line was saturating, DSL was retraining, and the modem was crashing during the retrain.

### What I did

Changed the limit to `--bwlimit 3.5M` (3.5 MiB/s ≈ 29 Mbps, about 60% of upstream). Checked the OPNsense traffic graphs during the next backup — steady ~30 Mbps, no more saturation. No drops since.

I also set up automated recovery for cases when the modem does freeze: the watchdog tries a software restart first, and if that doesn't help, it calls a Home Assistant webhook that power-cycles the modem through a smart plug.

Still on my list: calling the ISP to request a higher SNR target on the line, which would make the connection more stable under load.

</details>

---

<details>
<summary><strong>UniFi AP not showing up after replacement — cross-VLAN adoption</strong></summary>

### The problem

My UniFi U6 Plus AP stopped working after a power cycle. Solid white LED, no ping, no SSH, nothing in the ARP table. Reset button didn't respond either — held it for 10, then 20 seconds, LED didn't change. The AP was dead. Got a refund and ordered a U7 Lite as replacement.

While dealing with this I realized something about my setup that was going to keep causing problems: my UniFi controller runs on VLAN 40 (Servers) and the AP sits on VLAN 99 (Management). They're on different networks. Every time I replace or power-cycle an AP, it has no way to find the controller on its own — it doesn't know where to look.

I checked what other people do in this situation. For simple homelabs, most just keep everything on one VLAN. For setups with VLAN segmentation, the common advice ([Ubiquiti community](https://community.ui.com/), [LazyAdmin](https://lazyadmin.nl/)) is to add a DNS entry so the AP can find the controller by resolving the hostname `unifi`. Moving the controller to the management VLAN would break my reverse proxy, dashboard, and firewall rules — not worth it for this.

### What happened with the replacement

The U7 Lite arrived, got power via PoE, and picked up an IP on the network. I could ping it. But in the UniFi controller it showed up with a laptop icon — as a regular device, not as an access point. The controller didn't recognize it as something to manage.

I SSH'd into the AP to see what's going on. It was trying to resolve the hostname `unifi` and failing — I had no DNS entry for that. So it had no idea where the controller was.

Pointed it to the controller manually:

```bash
set-inform http://192.168.40.18:8080/inform
```

Adopted immediately.

### Permanent fix

Added a DNS override in OPNsense Unbound: `unifi.localdomain` → `192.168.40.18`. Now any UniFi device on any VLAN can find the controller through DNS without manual intervention. Also set the inform host override in the UniFi controller settings to the same IP.

The adoption procedure I settled on: connect new devices on the controller's VLAN first, let them adopt, then move management to VLAN 99 afterward. Trying to adopt across VLANs without DNS was the whole reason this kept being a pain.

</details>
