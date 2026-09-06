# Home Assistant

Home Assistant runs the home automation and the device dashboards, as VM 202 on Cubi — deliberately on the applications host rather than anywhere near the router.

[Overview](README.md) · [Selected services](docs/services.md) · [Dashboard example](SETUP.md#home-assistant)

## Devices and examples

- **E-paper display:** renders a dashboard image and sleeps between updates, which is what makes battery life usable. [ESPHome example](HomeAssistant/esphome/epaper.yaml)
- **Bluetooth proxies:** ESP32 boards that extend Bluetooth range so sensors in other rooms reach Home Assistant. [ESPHome example](HomeAssistant/esphome/ble-proxy.yaml)
- **Zigbee and Thread:** an SMLIGHT SLZB-MR5U coordinator over PoE, not documented here yet.

Home Assistant is also the recovery path for the modem: when the WAN watchdog cannot fix a drop in software, it triggers a smart plug to power-cycle it. [How that came about](TROUBLESHOOTING.md#backup-uploads-and-internet-drops)

The ESPHome files are specific to my boards and my wiring. Review the pins, addresses and secrets before flashing anything with them.

Automations and dashboard YAML are not published here.
