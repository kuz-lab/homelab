# Ansible Adoption Plan

Goal: move from manual + community-script provisioning to codified automation, at a slow sustainable pace (~2–4 h/week). Each phase ends with something working and committed to Gitea. Nothing existing gets touched until Phase 2.

Scope note: OPNsense, HAOS, and UniFi OS stay out of scope — they're appliances with their own config management. Targets are the Debian/Ubuntu LXCs and VMs, and later the Proxmox hosts themselves.

---

## Phase 0 — Control node + inventory (week 1)

Setup only. Zero risk.

- [ ] Install on MacBook: `brew install ansible ansible-lint`
- [ ] Create repo `ansible` in Gitea (private — inventory contains internal IPs)
- [ ] Layout:
  ```
  ansible/
  ├── ansible.cfg
  ├── inventory/
  │   └── hosts.yml
  ├── playbooks/
  ├── roles/
  └── group_vars/
  ```
- [ ] Inventory groups matching reality:
  - `proxmox_hosts` — cubi, zima
  - `docker_lxcs` — metrics, paperless, nodered, actual, immich, vaultwarden, caddy, portainer, homarr, homepage
  - `native_lxcs` — gitea, adguard, ntfy, uptimekuma
  - `vms` — wazuh
- [ ] Dedicated `ansible` SSH key; distribute with `ssh-copy-id` (later: manage authorized_keys via Ansible itself)
- [ ] `ansible.cfg`: point at inventory, `interpreter_python = auto_silent`

**Done when:** `ansible all -m ping` is green for every host.

## Phase 1 — Read-only reconnaissance (week 1–2)

Learn ad-hoc commands and facts. Still zero risk.

- [ ] `ansible all -m setup` — browse facts
- [ ] Ad-hoc: uptime, disk usage (`df -h`), pending apt updates across all hosts at once
- [ ] First playbook `playbooks/audit.yml`: gather OS version, kernel, disk free, pending updates → write a summary to a local file
- [ ] Commit. This playbook alone is already portfolio material ("fleet audit in one command")

**Done when:** one command tells you the patch state of the whole lab.

## Phase 2 — Baseline role (week 2–4)

First changes. Test on ONE expendable container first (homepage — it's being retired anyway, perfect guinea pig).

- [ ] Role `common`:
  - standard packages (htop, curl, vim, tmux…)
  - timezone + NTP
  - ansible SSH key in authorized_keys (from now on Ansible manages its own access)
  - SSH hardening drop-in (no root password auth)
- [ ] Apply to homepage CT only → verify → roll out group by group (`--limit`)
- [ ] Add `unattended-upgrades` config to the role — this closes the roadmap item "unattended-upgrades for OS patches"

**Done when:** every Debian guest converges cleanly and a second run reports zero changes (idempotence).

## Phase 3 — Patching playbook (week 4–5)

Turns the Wazuh CVE workflow into one command.

- [ ] `playbooks/patch.yml`: apt update/upgrade, `serial: 2`, detect reboot-required, reboot with `reboot` module (exclude critical hosts behind a flag)
- [ ] Use it for the next real maintenance window triggered by a Wazuh CVE digest
- [ ] Document the loop in the repo: Wazuh flags CVE → `ansible-playbook patch.yml --limit affected` → verify

**Done when:** one real patch cycle done via Ansible instead of SSH-hopping.

## Phase 4 — Service deployment (week 5–7)

Deploy something NEW with Ansible end-to-end. Candidate from the roadmap: **Stirling-PDF**.

- [ ] Role `docker_host`: install Docker + socket-proxy the way the other LXCs have it
- [ ] Deploy compose via `community.docker.docker_compose_v2` (compose file still lives in the Gitea stacks repo — Ansible references it, doesn't fork it; decide then whether Portainer or Ansible owns runtime)
- [ ] Secrets via `ansible-vault`, vault password NOT in the repo

**Done when:** Stirling-PDF runs and was never touched by hand.

## Phase 5 — Full provisioning: the portfolio money shot (week 7–9)

- [ ] `community.general.proxmox` module against the Proxmox API (token, not root password)
- [ ] `playbooks/new-lxc.yml`: create CT from template → wait for SSH → apply `common` → apply `docker_host` → deploy service
- [ ] Use it for real when the Raspberry Pi 5 / next service arrives
- [ ] Prove it: destroy the test CT and recreate identical in minutes

**Done when:** empty CT ID → running documented service, one command.

## Phase 6 — Make it visible (week 9+)

- [ ] Sanitized mirror of the ansible repo (or selected roles) into the public portfolio repo
- [ ] README section "Automation": before/after — what used to be manual clicks, screenshots of a patch run
- [ ] Update Lab Journal + roadmap

---

## Rules for the whole journey

1. `--check --diff` before every first real run.
2. Never test on Vaultwarden, Gitea, or AdGuard — always on homepage/test CT first.
3. Idempotence is the bar: second run = 0 changes, or the role isn't done.
4. Secrets: ansible-vault only, same discipline as Portainer env vars.
5. `ansible-lint` clean before commit.
6. One phase at a time — a half-finished Phase 4 is worth less than a solid Phase 3.
