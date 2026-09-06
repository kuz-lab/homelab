# Remote Virtual Desktop

Connecting a Meta Quest 3 to Virtual Desktop Streamer on a MacBook from outside the home network through OPNsense port forwarding: the setup, verification procedure, and the three silent failures that made the problem look like a carrier issue.

Verified on 16 August 2026 with OPNsense 26.7, Virtual Desktop Streamer 1.34.18, and macOS 27.0.

This is an account of one investigation in August 2026, not a specification for every Streamer version or mobile network. It concerns viewing the Mac desktop from a headset, not PCVR game streaming. The setup deliberately opens ports to the internet; the current status of those forwards was not checked during the September documentation review.

[Overview](../README.md) · [Troubleshooting](../TROUBLESHOOTING.md) · [Current network notes](network-and-access.md)

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

## What I observed

The headset could list the Mac even when it could not connect. The Streamer had an outbound connection to `40.89.161.236` from local port `38810`, and connection attempts from the mobile network reached OPNsense's WAN interface.

The state table showed that source NAT had changed `38810` to a different outside port. Preserving that port was one of the changes in the working configuration. My explanation was that the translated port interfered with rendezvous or hole punching, but the captures did not establish the cloud's internal signalling or the carrier's exact NAT behaviour.

The useful distinction was simpler: listing the computer worked; establishing the actual connection did not.

### Ports

| Port | Protocol | Purpose |
| ---: | --- | --- |
| 38810 | TCP | Control channel and entry point during hole punching |
| 38820 | TCP | Required by Virtual Desktop documentation |
| 38830 | TCP | Required by Virtual Desktop documentation |
| 38840 | TCP | Required by Virtual Desktop documentation |
| 38850 | UDP | Observed on macOS Streamer 1.34; absent from the official requirements |

The [Virtual Desktop FAQ](https://www.vrdesktop.net/) lists the four TCP ports. UDP `38850` was observed on the macOS build, but was not proven necessary for this connection. Its appearance in a capture alone is not a reason to open another port.

## Mac setup

- Install Virtual Desktop Streamer and sign in with the same account used on the headset.
- Enable **Allow remote connections**, **Start with macOS**, and **Ask for computer access**. Accept the confirmation dialog on the Mac on the first remote connection, or the connection will drop.
- Keep the macOS Application Firewall enabled and explicitly allow the Streamer. [Apple's application-firewall settings](https://support.apple.com/guide/mac-help/block-connections-to-your-mac-with-a-firewall-mh34041/mac)
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

The lab used Hybrid outbound NAT with a static-port rule. OPNsense has both Outbound NAT settings and a newer Source NAT interface; their controls are not interchangeable. The automatic/Hybrid mode is configured under Outbound, while the newer interface has a separate rule view. Check the installed version's [NAT documentation](https://docs.opnsense.org/manual/nat.html) before recreating this setup.

| Field | Value |
| --- | --- |
| Interface | WAN |
| Protocol | TCP for the documented forwarding path |
| Source | `HOST_MAC` |
| Source port | Match the Streamer's observed source ports; `38810` was the relevant one in this test |
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

- `Manual` creates no linked pass rule; a separate matching firewall rule is needed. That separate rule was missing here.
- `Pass` accepts traffic through the NAT rule rather than a separately visible rule in the rules tab.
- `Register rule`, used in this case, generates a linked filter rule. Check the generated rules and logging settings instead of assuming the NAT entry alone proves traffic is allowed. [OPNsense filter-rule association](https://docs.opnsense.org/manual/nat.html#filter-rule-association)

Verify the generated pass rules:

```sh
pfctl -sr | grep 388
```

Expect one line per port, similar to:

```text
pass in quick on pppoe0 reply-to (pppoe0 <GW>) inet proto tcp \
  from any to 192.168.10.10 port = 38810 flags S/SA keep state
```

The `reply-to` clause was present in this installation and directs replies through the specified interface and gateway. If no matching pass rule appears after **Apply**, investigate before continuing.

## Verification

Test the transport separately from Virtual Desktop so a network fault can be distinguished from an application fault.

### Invalid test conditions

- Do not test `<WAN_IP>` from inside the home network. That is a hairpin request and requires NAT reflection.
- Ensure the phone is on mobile data. Turn Wi-Fi off in Settings rather than Control Center, then open `https://ifconfig.me`; it must show a carrier address.
- Do not run the Streamer and a test server together. They compete for port `38810`.

### Transport test

On the Mac, start a temporary HTTP server from an empty directory. The command publishes the current directory to the internet:

```sh
vd_test_dir=$(mktemp -d /tmp/vdtest.XXXXXX)
cd "$vd_test_dir"
python3 -m http.server 38810 --bind 0.0.0.0
```

From the phone on mobile data, open `http://<WAN_IP>:38810`. A successful request produces output like:

```text
<CARRIER_IP> - - [16/Aug/2026 05:09:45] "GET / HTTP/1.1" 200 -
```

This verifies inbound HTTP connectivity through the forwarding path, not Virtual Desktop itself. Stop the server with Ctrl-C immediately after the test. The temporary directory was created empty so the test does not expose personal files.

### Live test

1. Start Virtual Desktop Streamer.
2. Confirm it owns the ports with `lsof -nP -iTCP | grep 388`. Expect the cloud connection plus bindings on `38820`, `38830`, and `38840`.
3. Put the headset on an outside network and connect.

## Diagnostics

### Locate the failure

Check the path in order:

1. Is the Streamer listening? Use `lsof` on the Mac. If not, the fault is in the application.
2. Does the Mac address match the alias? Compare `ipconfig getifaddr en0` with `pfctl -t HOST_MAC -T show`.
3. Has the public address changed after a PPPoE reconnect? Make sure the test targets the current address.
4. Does the packet reach the WAN? Capture on `pppoe0` during an attempt. If not, check the test address, capture filter and outside path before attributing it to the carrier.
5. Does it reach the inside interface? Capture on `vlan02`. If it appears only on WAN, inspect filtering, NAT and the target alias.
6. Does the Mac reply? A SYN without a SYN-ACK warrants checking the listener, host firewall and return route.

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

| Symptom | Possible cause | Check | Action to consider |
| --- | --- | --- | --- |
| “Computer is unreachable”; SYNs reach WAN but never the inside interface | No pass rule for the forward | `pfctl -sr \| grep 388` is empty | Set Firewall rule to `Register rule`, Interface to WAN, then Apply |
| Same symptom, but pass rules exist | Multiple addresses in the alias; `rdr` uses round-robin | `pfctl -t HOST_MAC -T show` | Reduce the alias to one address |
| Computer is visible but connection never establishes; the outside state-table port is not 38810 | Source-port randomization in Source NAT | `pfctl -ss \| grep 3881` | Enable Static port, then restart the Streamer |
| External test fails although everything is configured | Test ran from inside, or the phone was on home Wi-Fi | Capture shows a `192.168.10.x` source | Test from mobile data with Wi-Fi disabled in Settings |
| Test server answers but the headset still fails | Test server owns port 38810, preventing Streamer from binding it | `lsof -nP -iTCP \| grep 388` | Stop the server and restart the Streamer |
| It worked before but failed after a reboot | Mac address changed | Compare `ipconfig getifaddr en0` with the alias | Add a DHCP static mapping and set Private Wi-Fi Address to Fixed |
| It worked before but failed without a Mac change | Test is targeting an old public address | `ifconfig pppoe0 \| grep 'inet '` | Repeat the test against the current address |
| It connects but stutters or shows no image | Transport or application issue; cause not established here | Capture `portrange 38810-38850` during a session | Check current application requirements before opening additional ports |
| Mac replies leave by the wrong path | A VPN exit node is active on the Mac | Check `netstat -rn -f inet \| head -8` and the `default` route Netif | Disable the exit node |

## The three faults found in this installation

Three configuration issues were corrected before the successful test; they were not separately reproduced in controlled isolation:

1. **Source-port randomization in Source NAT.** The Streamer used local port `38810`, but the router translated it to `46677`. I enabled **Static port**. The proposed effect on connection negotiation is explained above as an inference.
2. **The alias contained two addresses.** It held `192.168.10.10` and `192.168.10.11`, so the `rdr` rule loaded with `round-robin` and sent some connections to a nonexistent host. Fix: keep exactly one address in the alias.
3. **No pass rules existed.** Every Destination NAT entry used `Manual`, so the forwards looked configured while default-deny silently discarded translated packets. Fix: choose **Register rule** and WAN as the interface.

Carrier NAT was initially suspected. A capture on `pppoe0`, however, showed SYNs arriving before any fix was applied. This did not prove every aspect of the carrier's network was irrelevant, but it gave me a concrete path to investigate inside the lab.

## Security and alternatives

The tested setup exposed four TCP ports of the Streamer to the internet. The rules targeted one host, but that still left the application's network-facing code reachable without VPN authentication. Application-level access controls and updates remain important; VLAN separation does not remove that exposure.

An authenticated VPN path is an alternative to evaluate, including headset support and latency. It was not validated as a replacement in this case study. Port forwards should be disabled when they are no longer needed.

Maintenance requirements:

- Keep a DHCP static mapping for the Mac.
- Check the current public address when repeating external tests.
- Re-check the port requirements after Streamer updates; distinguish observed traffic from proven forwarding requirements.

## Checklist

- [ ] Mac has a fixed address and Private Wi-Fi Address is set to Fixed.
- [ ] Streamer has Allow remote connections, Start with macOS, and Ask for computer access enabled.
- [ ] `HOST_MAC` contains exactly one address.
- [ ] The intended static-port rule is loaded for the source traffic observed in this setup.
- [ ] Four Destination NAT rules use Interface = WAN and Firewall rule = Register rule.
- [ ] Four pass rules are loaded: `pfctl -sr | grep 388`.
- [ ] A transport test from mobile data returns `GET /`.
- [ ] The test server is stopped and the Streamer restarted.
- [ ] The headset connects from an outside network.
