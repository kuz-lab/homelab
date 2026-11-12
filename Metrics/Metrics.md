# Metrics: Grafana and InfluxDB

Grafana shows how power use, temperatures and system resources change over time. InfluxDB stores the measurements behind the charts.

[Overview](../README.md) · [Services](../docs/services.md) · [Earlier dashboard screenshot](../screenshots/Grafana_Proxmox.png)

## What the charts are for

Home Assistant pushes measurements from the house and the lab — energy, climate, valve positions, air quality — and both Proxmox hosts report their own system metrics, into separate `haos` and `proxmox` databases that Grafana queries over SQL.

The questions are simple ones: how much power is the lab drawing, when does it spike, and did a maintenance change move anything.

## Moving from version 2 to version 3

I started on InfluxDB 2 and switched to 3 Enterprise about five days later, while there was almost no history to lose. That made it a clean cutover — change the writers, rebuild the dashboards — instead of a migration.

Long-term downsampling is still on the list. InfluxDB 3 Enterprise supports scheduled processing, including a [Downsampler plugin](https://docs.influxdata.com/influxdb3/enterprise/plugins/library/official/downsampler/); an external scheduler is not the only option. I have not set up that workflow here yet.

## September deployment snapshot

Observed during the 6 September 2026 check:

| Container | Image | Port |
| --- | --- | --- |
| Grafana | `grafana/grafana:13.1.0` | 3000 |
| InfluxDB 3 | `influxdb:3-enterprise` | 8181 |
| InfluxDB Explorer | `influxdata/influxdb3-ui:1.9.0` | 8888 |

## Files here

- [Grafana Compose example](docker-compose.yml) — Grafana only, without the old InfluxDB 2 service or dependency. Configure the data source separately.
- [InfluxDB 3 Compose example](influxdb3-compose.yml) — the database as a separate stack. The Explorer container is not included in this example.

The old combined file would have started InfluxDB 2 through Grafana's `depends_on`, even though that database was no longer deployed. It remains in Git history, not in the current example. [Compose dependency behaviour](https://docs.docker.com/compose/how-tos/startup-order/)

The public Grafana example now requires login; some earlier embedded dashboards used anonymous viewing. Review credentials, storage paths and port exposure before deployment. These repository changes have not been applied to the running lab.
