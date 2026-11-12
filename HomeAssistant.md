# Home Assistant

Home Assistant handles heating, lighting and everyday reminders at home. It runs as a VM on Cubi, separate from the router.

[Overview](README.md) · [Services](docs/services.md) · [Backups and Recovery](docs/backups-and-recovery.md)

## Everyday use

### Heating

Heating follows working days and days off from my calendar. I edit the calendar on my phone, and the automations use it to choose the day’s heating mode.

It also handles ventilation and temporary warming. If I manually turn a room’s heating off, the automation respects that.

### Lighting

Motion turns the bathroom lights on, and presence sensors help keep them on while someone is still there.

Physical controls are part of the setup too: buttons for switching lights, changing scenes and adjusting brightness.

### Reminders

I added a reminder for open windows: opening the entrance door while a window is still open triggers a phone notification listing the open windows.

There are also notifications for low batteries and unavailable battery-powered sensors. The air purifier follows a daily schedule, with manual control between scheduled changes.

## How it fits together

Home Assistant connects the devices and provides the controls and dashboards. Some automations run directly in Home Assistant; others run in Node-RED.

Devices connect over Zigbee, Thread, Wi-Fi and Bluetooth. ESPHome handles the [e-paper display](HomeAssistant/esphome/epaper.yaml) and [Bluetooth proxies](HomeAssistant/esphome/ble-proxy.yaml).

[Workbench (AI Agent harness)](docs/workbench.md) can inspect device availability through HA Observer and help investigate problems. The observer collects status and sends notifications on its own. Agents can read those observations, but changes remain a separate step.

The dashboards include a 3D view of the apartment with device status. An [earlier dashboard screenshot](screenshots/HAOS.png) shows a previous version of the interface.

## When the modem stopped responding

A few internet outages needed more than restarting the connection: the modem had frozen, and I had to power-cycle it manually.

I added a recovery step to the WAN watchdog. It tries a software restart first. If that fails, it asks Home Assistant to cycle the modem’s power through a smart plug.

Investigating those outages also led me to a mistake in the backup upload limit: I had mixed up megabytes and megabits.

[The full story](TROUBLESHOOTING.md#backup-uploads-and-internet-drops)

## Backups and recovery

Home Assistant is included in the full VM backups on Cubi, with a verified copy in Backblaze B2.

I previously restored it into a different VM ID, and it came back. That was a useful recovery test for the setup at the time.

[How backups and recovery work](docs/backups-and-recovery.md)
