#!/usr/bin/env python3
import csv

with open("OPNsense/download_rules.csv") as f:
    rows = [r for r in csv.reader(f, delimiter=";") if len(r) > 19]

data = sorted(rows[1:], key=lambda r: int(r[4]) if r[4].isdigit() else 0)

with open("OPNsense/firewall-rules.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["Seq","Action","Interface","Protocol","Source","Destination","Port","Log","Description"])
    for r in data:
        w.writerow([r[4], r[5], r[8], r[11], r[14], r[17], r[19], r[24], r[-1]])
