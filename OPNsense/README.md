# Earlier firewall exports

These files preserve parts of an earlier firewall configuration. They are not the current policy or a complete backup for importing or restoring OPNsense. Their export dates were not recorded.

- [firewall-rules.csv](firewall-rules.csv) is a compact summary.
- [firewall-rules-recovery.csv](firewall-rules-recovery.csv) contains more fields, but its name does not make it a recovery backup.

The files also differ in their rules. For rule 1257, the summary limits SSH access to one host alias; the recovery-named file allows the Trusted network. Rule 4522 has broader protocol and port matching in the latter, which also omits rules 1269 and 1275 from the summary. Both files retain the earlier DNS setup.

I keep them as historical examples. The [Network and Access page](../docs/network-and-access.md) describes the current design.

[Back to the overview](../README.md)
