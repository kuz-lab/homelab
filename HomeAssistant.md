# Home Assistant

Home Assistant OS runs as VM 202 on Cubi (192.168.40.10), handling automations, dashboards, and the ESPHome-flashed devices on the IoT VLAN.

## Devices

- **E-paper display** — glanceable readiness dashboard, ESPHome config: [HomeAssistant/esphome/epaper.yaml](HomeAssistant/esphome/epaper.yaml)
- **BLE proxies** (bedroom + backroom) — extend Bluetooth range for HA integrations, shared config: [HomeAssistant/esphome/ble-proxy.yaml](HomeAssistant/esphome/ble-proxy.yaml)

## Roadmap

- Document Zigbee2MQTT / Thread setup (SLZB-MR5U coordinator)
- Automations writeup
- Dashboard card examples — YAML snippets (button-card, bubble-card, mini-graph-card, apexcharts) with short explanations of what each does and why
