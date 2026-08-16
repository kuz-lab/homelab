# Remote Virtual Desktop

Connecting a Meta Quest 3 to Virtual Desktop Streamer on a MacBook from outside the home network through OPNsense port forwarding: the setup, verification procedure, and the three silent failures that made the problem look like a carrier issue.

Verified on 16 August 2026 with OPNsense 26.7, Virtual Desktop Streamer 1.34.18, and macOS 27.0.

## Environment

The public address is shown as `<WAN_IP>` throughout. Read the real value from **Interfaces → Overview** or with:

```sh
ifconfig pppoe0 | grep 'inet '
```

| Component | Configuration |
| --- | --- |
| Computer | MacBook Pro M1 Pro, macOS 27.0, `192.168.10.10` |
| Streamer | Virtual Desktop Streamer 1.34.18 |
| Headset | Meta Quest 3, Virtual Desktop from the Meta store |
| Router | OPNsense 26.7, VM on Proxmox |
| WAN | `pppoe0`, public IPv4, no CGNAT |
| Client segment | `vlan02` — Trusted, gateway `192.168.10.1` |
| Policy | Inter-VLAN default deny, outbound internet allowed |
| Headset network | Phone hotspot on mobile data (carrier CGNAT) |

## How remote mode works

1. The Streamer holds a permanent outbound TCP connection to the Virtual Desktop cloud. Azure address `40.89.161.236` was observed, with source port `38810`.
2. The headset signs in to the same cloud and sees the computer in its list. This works even when no direct path exists, so seeing the computer does not prove that the network path works.
3. On a connection attempt, the cloud tells each side the other's address and TCP hole punching begins: the Mac dials the headset, the headset dials the Mac, and the Streamer opens a `LISTEN` socket on `38810` at the same moment.
4. A headset on mobile data is usually behind symmetric carrier-grade NAT, so the Mac's outbound punch does not land. The surviving path is the headset's inbound connection to the forwarded port.

The public port advertised by the cloud must match the forwarded port. By default, `pf` randomizes the source port during translation; the cloud then advertises a random high port with nothing behind it. Static-port translation is therefore required.

### Ports

| Port | Protocol | Purpose |
| ---: | --- | --- |
| 38810 | TCP | Control channel and entry point during hole punching |
| 38820 | TCP | Required by Virtual Desktop documentation |
| 38830 | TCP | Required by Virtual Desktop documentation |
| 38840 | TCP | Required by Virtual Desktop documentation |
| 38850 | UDP | Observed on macOS Streamer 1.34; absent from the official requirements |

Official documentation lists only the four TCP ports. UDP `38850` was added after observing it on the macOS build, but it was not proven necessary. On a fresh setup, forward TCP only until a demonstrated problem requires UDP.

## Mac setup

- Install Virtual Desktop Streamer and sign in with the same account used on the headset.
- Enable **Allow remote connections**, **Start with macOS**, and **Ask for computer access**. Accept the confirmation dialog on the Mac on the first remote connection, or the connection will drop.
- Disable the macOS Application Firewall or explicitly allow the Streamer.
- Give the Mac a fixed address using a DHCP static mapping in OPNsense. The port forward targets one specific address.
- If **Private Wi-Fi Address** is enabled for this network, set it to **Fixed**. In Rotating mode, the MAC changes and the DHCP reservation no longer matches.

Check the current address:

```sh
ipconfig getifaddr en0
```

## OPNsense configuration

Apply the following subsections in order.

### 1. Host alias

In **Firewall → Aliases**, create a **Host(s)** alias named `HOST_MAC` containing exactly one address: `192.168.10.10`.

With more than one address in the alias, `pf` loads the forward with `round-robin` and distributes connections among the addresses. Some attempts can silently land on a host where nothing is listening.

Verify the loaded alias:

```sh
pfctl -t HOST_MAC -T show
```

Expect exactly one line.

### 2. Source NAT with a static port

Open **Firewall → NAT → Source NAT** (called Outbound in older releases). Select **Hybrid outbound NAT** so the automatic rules remain, then add one rule per port or a single rule for the range.

| Field | Value |
| --- | --- |
| Interface | WAN |
| Protocol | TCP/UDP |
| Source | `HOST_MAC` |
| Source port | 38810, 38820, 38830, 38840, 38850 |
| Destination | any |
| Translation target | Interface address |
| **Static port** | **enabled** |

Verify the generated NAT rule:

```sh
pfctl -sn | grep 38810
```

The output must contain `nat on pppoe0 … port = 38810 … static-port`.

### 3. Destination NAT port forwards

Open **Firewall → NAT → Destination NAT** (the former Port Forward page in OPNsense 26.7). Create one rule per TCP port.

| Field | Value |
| --- | --- |
| **Interface** | **WAN** — do not leave empty |
| Version | IPv4 |
| Protocol | TCP |
| Source / Source port | any |
| Destination Address | WAN address |
| Destination Port | 38810 / 38820 / 38830 / 38840 |
| Redirect Target IP | `HOST_MAC` |
| Redirect Target Port | same port — preserved |
| **Firewall rule** | **Register rule** |

Press **Apply** after saving all rules.

The **Firewall rule** option matters:

- `Manual` creates no pass rule. The forward exists, but the default-deny policy drops the translated packet.
- `Pass` works through `rdr-pass`, bypassing the filter rules. It is not visible under **Firewall → Rules**, is not logged, and ignores rule ordering.
- `Register rule` creates a linked, logged rule under **Firewall → Rules → WAN**. This is the recommended option.

Verify the generated pass rules:

```sh
pfctl -sr | grep 388
```

Expect one line per port, similar to:

```text
pass in quick on pppoe0 reply-to (pppoe0 <GW>) inet proto tcp \
  from any to 192.168.10.10 port = 38810 flags S/SA keep state
```

The `reply-to` clause is essential on PPPoE because it ensures that the reply leaves through the same interface. If no lines appear after **Apply**, stop and fix the rules before continuing.

## Verification

Test the transport separately from Virtual Desktop so a network fault can be distinguished from an application fault.

### Invalid test conditions

- Do not test `<WAN_IP>` from inside the home network. That is a hairpin request and requires NAT reflection.
- Ensure the phone is on mobile data. Turn Wi-Fi off in Settings rather than Control Center, then open `https://ifconfig.me`; it must show a carrier address.
- Do not run the Streamer and a test server together. They compete for port `38810`.

### Transport test

On the Mac, start a temporary HTTP server from an empty directory. The command publishes the current directory to the internet:

```sh
mkdir -p /tmp/vdtest
cd /tmp/vdtest
python3 -m http.server 38810 --bind 0.0.0.0
```

From the phone on mobile data, open `http://<WAN_IP>:38810`. A successful request produces output like:

```text
<CARRIER_IP> - - [16/Aug/2026 05:09:45] "GET / HTTP/1.1" 200 -
```

This proves the full path: internet → `pppoe0` → DNAT → pass rule → `vlan02` → Mac. Stop the server and remove the temporary directory afterwards.

### Live test

1. Start Virtual Desktop Streamer.
2. Confirm it owns the ports with `lsof -nP -iTCP | grep 388`. Expect the cloud connection plus bindings on `38820`, `38830`, and `38840`.
3. Put the headset on an outside network and connect.

## Diagnostics

### Locate the failure

Check the path in order:

1. Is the Streamer listening? Use `lsof` on the Mac. If not, the fault is in the application.
2. Does the Mac address match the alias? Compare `ipconfig getifaddr en0` with `pfctl -t HOST_MAC -T show`.
3. Has the public address changed after a PPPoE reconnect? If it changes, configure dynamic DNS.
4. Does the packet reach the WAN? Capture on `pppoe0` during an attempt. If not, the fault is in the outside network or carrier.
5. Does it reach the inside interface? Capture on `vlan02`. If it appears on WAN but not here, a filter is dropping it or the alias is wrong.
6. Does the Mac reply? Capture on the Mac. A SYN arriving with no SYN-ACK leaving indicates host-side blocking.

### OPNsense commands

| Goal | Command |
| --- | --- |
| Find the WAN interface | `netstat -rn -f inet \| head -5` |
| Find the inside interface | `netstat -rn -f inet \| grep 192.168.10` |
| Read the current public address | `ifconfig pppoe0 \| grep 'inet '` |
| Show the loaded alias | `pfctl -t HOST_MAC -T show` |
| Show NAT rules | `pfctl -sn \| grep 388` |
| Show filter rules | `pfctl -sr \| grep 388` |
| Show live states | `pfctl -ss \| grep 3881` |
| Flush states to an address | `pfctl -k <IP>` |
| Capture on WAN, excluding the cloud | `tcpdump -ni pppoe0 'portrange 38810-38850 and not host 40.89.161.236'` |
| Capture on the inside interface | `tcpdump -ni vlan02 'tcp port 38810 and host 192.168.10.10'` |

GUI equivalents are **Interfaces → Diagnostics → Packet Capture** and **Firewall → Log Files → Live View**. Filtering Live View by destination port shows which rule passed or blocked a packet. Use SSH for output longer than one screen because the Proxmox console does not scroll.

### macOS commands

| Goal | Command |
| --- | --- |
| Show Streamer listening sockets | `lsof -nP -iTCP -sTCP:LISTEN \| grep 388` |
| Show all Streamer sockets | `sudo lsof -nP -i \| grep -iE 'streamer\|virtual'` |
| Watch sockets over time | `while true; do date '+%T'; lsof -nP -i \| grep -E '388[0-9]0'; sleep 1; done` |
| Show the Mac address on the LAN | `ipconfig getifaddr en0` |
| Check the default route and VPN path | `netstat -rn -f inet \| head -8` |
| Capture on the Mac | `sudo tcpdump -ni en0 'tcp port 38810'` |

## Symptom table

| Symptom | Cause | Check | Fix |
| --- | --- | --- | --- |
| “Computer is unreachable”; SYNs reach WAN but never the inside interface | No pass rule for the forward | `pfctl -sr \| grep 388` is empty | Set Firewall rule to `Register rule`, Interface to WAN, then Apply |
| Same symptom, but pass rules exist | Multiple addresses in the alias; `rdr` uses round-robin | `pfctl -t HOST_MAC -T show` | Reduce the alias to one address |
| Computer is visible but connection never establishes; the outside state-table port is not 38810 | Source-port randomization in Source NAT | `pfctl -ss \| grep 3881` | Enable Static port, then restart the Streamer |
| External test fails although everything is configured | Test ran from inside, or the phone was on home Wi-Fi | Capture shows a `192.168.10.x` source | Test from mobile data with Wi-Fi disabled in Settings |
| Test server answers but the headset still fails | Test server owns port 38810, preventing Streamer from binding it | `lsof -nP -iTCP \| grep 388` | Stop the server and restart the Streamer |
| It worked before but failed after a reboot | Mac address changed | Compare `ipconfig getifaddr en0` with the alias | Add a DHCP static mapping and set Private Wi-Fi Address to Fixed |
| It worked before but failed without a Mac change | Public address changed after PPPoE reconnect | `ifconfig pppoe0 \| grep 'inet '` | Configure dynamic DNS |
| It connects but stutters or shows no image | UDP 38850 may be needed | Capture `portrange 38810-38850` during a session | Forward UDP 38850 in the same way |
| Mac replies leave by the wrong path | A VPN exit node is active on the Mac | Check `netstat -rn -f inet \| head -8` and the `default` route Netif | Disable the exit node |

## The three faults found in this installation

Each fault was independently sufficient to break the connection:

1. **Source-port randomization in Source NAT.** The Streamer contacted the cloud from port `38810`, but the router translated it to `46677`. The cloud advertised `46677` to the headset even though nothing was forwarded behind it. Fix: enable **Static port**.
2. **The alias contained two addresses.** It held `192.168.10.10` and `192.168.10.11`, so the `rdr` rule loaded with `round-robin` and sent some connections to a nonexistent host. Fix: keep exactly one address in the alias.
3. **No pass rules existed.** Every Destination NAT entry used `Manual`, so the forwards looked configured while default-deny silently discarded translated packets. Fix: choose **Register rule** and WAN as the interface.

Symmetric carrier NAT was initially suspected because it can block hole punching from the Mac side. A capture on `pppoe0`, however, showed SYNs arriving from the carrier before any fix was applied. The traffic was reaching the WAN; the faults were inside the perimeter. Capture on the WAN before blaming a system outside your control.

## Security and alternatives

This setup exposes four TCP ports of a proprietary service to the entire internet. The rules target one host, are visible and logged because they use `Register rule`, and the Mac is in a Trusted VLAN behind an inter-VLAN default-deny policy. The remaining risk is that a flaw in the Streamer's network code is directly reachable without perimeter authentication.

For travel, installing Tailscale on the Quest from the official Android APK requires headset developer mode but offers a safer path:

- no open WAN ports;
- WireGuard authentication and tailnet identity;
- independence from the remote network's NAT type; when no direct path exists, DERP relay fallback remains usable for desktop work, though its latency is unsuitable for VR;
- captive portals remain only partly solved and may require a travel router running Tailscale.

A practical end state is to keep direct forwarding as a fast path for networks without symmetric NAT and use the VPN by default while travelling.

Maintenance requirements:

- Keep a DHCP static mapping for the Mac.
- Configure dynamic DNS on OPNsense if the public address is dynamic.
- Re-check the port set after Streamer updates. The macOS build changed in the 1.34 branch and its observed behavior already differs from the documentation.

## Checklist

- [ ] Mac has a fixed address and Private Wi-Fi Address is set to Fixed.
- [ ] Streamer has Allow remote connections, Start with macOS, and Ask for computer access enabled.
- [ ] `HOST_MAC` contains exactly one address.
- [ ] Source NAT with Static port covers ports 38810–38850.
- [ ] Four Destination NAT rules use Interface = WAN and Firewall rule = Register rule.
- [ ] Four pass rules are loaded: `pfctl -sr | grep 388`.
- [ ] A transport test from mobile data returns `GET /`.
- [ ] The test server is stopped and the Streamer restarted.
- [ ] The headset connects from an outside network.
