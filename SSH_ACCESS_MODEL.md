# SSH Access Model

Rebuilt 2026-07-18. The full remediation **including the cubi bastion and Tailscale lockdown is done**; this documents the model as it now runs, plus the remaining roadmap.

---

## The model in one paragraph

Two keys live on the MacBook and nowhere else. `id_ed25519_slava` is the human (Git + interactive SSH), `id_ed25519_ansible` is the automation. Both are passphrase-encrypted at rest and served by the macOS Keychain ssh-agent (passphrase typed once, ever). All fleet SSH goes MacBook → cubi (bastion) → host via ProxyJump — cubi holds no keys, it only relays TCP. Password SSH is disabled fleet-wide; root login is key-only (`prohibit-password`). `~/.ssh/config` maps aliases 1:1 to the Ansible inventory, so `ssh caddy` and `--limit caddy` mean the same host. Remote (Tailscale) enters through the same doors — tailnet ACL grants allow only bastion SSH, Caddy 443, AdGuard DNS, OPNsense GUI. Hosts never SSH to each other — recovery inside Proxmox is `pct enter <id>` / GUI console, not SSH.

## Network path

- **Firewall (Trusted):** MacBook → cubi:22 is the only SSH pass rule toward the fleet ("Trusted: SSH to Proxmox (bastion)"); MacBook → zima:22 is the firewall-host recovery rule. Seq-1307 RFC1918 block stops everything else before the internet-allow rule.
- **Firewall (Management):** "cubi bastion → Servers SSH (ProxyJump relay)" — the second leg of the jump. Added 2026-07-18; without it the Management RFC1918 block correctly kills the relay.
- **ssh config:** `Host <fleet aliases> / 192.168.40.* → ProxyJump cubi`. The IP pattern makes Ansible jump too (it connects by IP) — no inventory changes needed.
- **Tailscale:** subnet router on OPNsense advertises the VLANs, but tailnet ACL grants restrict members to 99.2:22, 99.3:22 (SSH), 40.12:443 (Caddy), 40.11:53 (DNS), 99.1:443 (OPNsense GUI). Policy tests in the tailnet policy file prevent saves that would re-open direct fleet SSH. Verified: with Tailscale on, `ssh caddy` works via the jump; direct `nc` to fleet :22 times out.

## Keys

| Key | Purpose | At rest | Unlock |
|-----|---------|---------|--------|
| `id_ed25519_slava` | GitHub, Gitea, interactive SSH to all hosts | Encrypted (passphrase) | Keychain agent, auto-loads at login |
| `id_ed25519_ansible` | Ansible only | Encrypted (passphrase) | Keychain agent, auto-loads at login |

- Backups: both encrypted private keys + `.pub`s + passphrases in Vaultwarden entries (`ssh id_ed25519_slava`, `ssh id_ed25519_ansible`).
- Retired 2026-07-18: `id_rsa` (legacy RSA), `id_ed25519_github`, `id_ed25519_gitea` — removed from disk and from GitHub/Gitea web UIs. Also deleted an accidental keypair (`yes`/`yes.pub`) from the notes vault.
- Rule: private keys never leave the Mac. No keys on the bastion, no host-to-host SSH.

## Who can log in where

| Target | User | Auth |
|--------|------|------|
| GitHub / Gitea (git ops) | `git` / `gitea` | slava key |
| Proxmox hosts (cubi, zima) | `root` | key only (`prohibit-password`) — PVE tooling assumes root |
| All LXCs | interactive: `slava` · automation: `ansible` — both NOPASSWD sudo | key only, root SSH disabled (`PermitRootLogin no`) |
| Wazuh VM | `ansible` (NOPASSWD sudo) | key only, root SSH disabled |
| HAOS, UniFi OS VMs | — | own mechanisms, outside this model |

Managed by the `common` Ansible role (`roles/common`): creates both users, installs keys, validated NOPASSWD sudoers drop-ins. Inventory connects as `ansible` + become on LXC groups; ssh config sets `User slava` for fleet aliases.

## sshd policy (fleet-wide)

Drop-in `/etc/ssh/sshd_config.d/00-kuzlab-hardening.conf` on all 17 hosts
(`00-` prefix wins OpenSSH first-value-wins ordering, incl. over Ubuntu's cloud-init `50-*`):

```
# LXCs + Wazuh:
PasswordAuthentication no
KbdInteractiveAuthentication no
PermitRootLogin no

# Proxmox hosts (cubi, zima):
PasswordAuthentication no
KbdInteractiveAuthentication no
PermitRootLogin prohibit-password
```

Deployed via Ansible ad-hoc, rolled out group by group (native_lxcs → docker_lxcs → wazuh → proxmox_hosts), each group verified: key login works, password login refused (`Permission denied (publickey)`).

## Client config (`~/.ssh/config`)

- `Host *`: `AddKeysToAgent yes`, `UseKeychain yes`, `IdentityFile id_ed25519_slava`, `IdentitiesOnly yes` (never spray keys), `ServerAliveInterval 60`.
- One alias per host, names = Ansible inventory names. Exception: `gitea` = git operations, `gitea-ct` = admin shell on CT 101.
- Fleet user is set in one block — flipping the fleet to non-root later is a one-line change.
- Ansible references its key via `ansible_ssh_private_key_file` in inventory; agent serves the decrypted key.

## Recovery paths (in order)

1. `ssh cubi` / `ssh zima` from the Mac (key).
2. Proxmox GUI console → `pct enter <id>` for any LXC (no SSH, no network needed).
3. Root password on the **console** (still set; useless over SSH by design).
4. Physical break-glass port (VLAN 99, switch port 3).

---

## Roadmap (deliberately not done yet)

1. **YubiKeys for the interactive key** — `ed25519-sk` keypair per YubiKey (have 3; one currently missing), all pubkeys enrolled fleet-wide + GitHub/Gitea; ansible key stays software (touch-per-auth breaks automation). Also use YubiKeys as 2FA for GitHub, Vaultwarden, Proxmox GUI.
2. **Tailnet account hardening** — security keys (YubiKeys, min. 2) on the Apple ID (= tailnet identity via Sign in with Apple; Owner is not transferable on shared-domain tailnets), passkey `@passkey` user as backup Admin, delete stale device `valas-zukni-m1`, evaluate Tailnet Lock later.
3. **known_hosts hygiene** — entries were TOFU via `ssh-keyscan`; optionally re-verify host keys out-of-band (Proxmox console `ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub`) or accept TOFU for a home LAN.

## Done 2026-07-18 (Phase 2)

- `common` Ansible role: `slava` + `ansible` users, keys, validated NOPASSWD sudoers on all 14 LXCs.
- Inventory flipped: LXC groups connect as `ansible` + become; ssh config fleet user = `slava`.
- `PermitRootLogin no` on all LXCs + Wazuh — root SSH exists only on Proxmox hosts (key-only). Verified per host: slava+sudo works, root refused, `ansible all -m ping` 17/17.

## Done 2026-07-18

- Two-key consolidation, passphrases + Keychain agent, Vaultwarden backups, old keys retired (disk + GitHub/Gitea UIs).
- `~/.ssh/config` as UX layer, aliases = inventory names.
- Personal key distributed fleet-wide via Ansible; password SSH disabled on all 17 hosts (verified per group: key works, password refused).
- Bastion live: ProxyJump via cubi for interactive + Ansible + Gitea git ops; Management→Servers relay rule added; verified end-to-end with Tailscale off.
- Tailscale locked down: default allow-all replaced with least-privilege grants + policy tests; verified direct fleet SSH blocked over tailnet.

## Decisions log

- **ProxyJump, not keys-on-bastion** — compromised bastion can't reach the fleet; it only relays TCP.
- **Keychain agent, not Vaultwarden agent, for the working keys** — Vaultwarden runs *on* the fleet (CT 107); using it as the SSH agent creates a circular dependency (fleet down → can't SSH to fix fleet). Vaultwarden's role is encrypted backup + passphrase storage. Also: approval-popup-per-connection doesn't suit Ansible across 17 hosts.
- **Apple Passwords** — no SSH key support (2026); not an option.
- **SSH CA (smallstep/Vault)** — right answer at org scale, overkill for 17 hosts / 1 human; Ansible-managed `authorized_keys` *is* the key management.
- **No host-to-host SSH** — `pct enter` covers the in-Proxmox case; any future cubi→fleet need gets a dedicated restricted key, not a general one.
