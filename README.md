# PocketNotifier for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

A Home Assistant custom integration for [PocketNotifier](https://pocketnotifier.vanmo.se),
a push-notification relay where each API key identifies a **channel** that fans
out to the subscribed iOS/Android phones.

Instead of hand-rolling `rest_command` YAML, this integration lets you add
channels through the UI and exposes each one as a native
`notify.<channel_name>` action — usable in automations, scripts, blueprints and
the "Send a notification" UI.

## Features

- **UI configuration** — add one or more channels via **Settings → Devices &
  Services → Add Integration → PocketNotifier**. Each channel is one config
  entry: an API key plus a human-readable name.
- **Native notify action** — every channel shows up as `notify.<channel_name>`.
- **URL passthrough** — send an optional tap-through URL via the standard
  `data` field.

## Installation

### HACS (recommended)

1. In HACS, open the three-dot menu → **Custom repositories**.
2. Add `https://github.com/trdle/Pocket-notifier-ha` with category
   **Integration**.
3. Search for **PocketNotifier**, install it, and restart Home Assistant.

## Configuration

1. Go to **Settings → Devices & Services → Add Integration**.
2. Search for **PocketNotifier**.
3. Enter:
   - **Channel name** — used to build the service name. For example
     `Living Room` becomes `notify.living_room`.
   - **API key** — the PocketNotifier API key for the channel.

> The API key is **not** validated when you add the channel. Any key is
> accepted; delivery failures are logged when a notification is sent.

Repeat to add as many channels as you like.

## Usage

The integration maps the standard notify fields onto the PocketNotifier API:

| Notify field   | Sent to PocketNotifier |
| -------------- | ---------------------- |
| `message`      | `body`                 |
| `title`        | `title`                |
| `data: { url }`| `url` (optional)       |

### Send a simple notification

```yaml
action: notify.living_room
data:
  title: "Front door"
  message: "Motion detected"
```

### Include a tap-through URL

```yaml
action: notify.living_room
data:
  title: "Camera"
  message: "Someone is at the door"
  data:
    url: "https://my.home-assistant.io/lovelace/cameras"
```

### In an automation

```yaml
automation:
  - alias: "Notify on doorbell"
    trigger:
      - platform: state
        entity_id: binary_sensor.doorbell
        to: "on"
    action:
      - action: notify.living_room
        data:
          title: "Doorbell"
          message: "Someone rang the doorbell"
```

## How it works

Under the hood each notification is delivered as:

```http
POST https://pocketnotifier.vanmo.se/api/notify
X-Api-Key: <your channel API key>
Content-Type: application/json

{ "title": "...", "body": "...", "url": "..." }
```

The integration uses Home Assistant's legacy notify platform
(`BaseNotificationService`), the same approach used by Pushover, ntfy, Gotify
and Bark, which gives a clean `data: { url: … }` passthrough.

## License

[MIT](LICENSE)
