# Sorgenia

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![hacs][hacsbadge]][hacs]
![Project Maintenance][maintenance-shield]

Home Assistant custom integration for reading electricity consumption and cost from a Sorgenia account.

> [!WARNING]
> This is an unofficial integration. It relies on Sorgenia and Bidgely web APIs, which may change without notice.

## Features

- Configuration entirely through the Home Assistant UI.
- Sign in with username/password and OTP, when Sorgenia requests it.
- Alternative setup with an existing access token and refresh token, without requesting OTP.
- Safe refresh-token rotation: the new token pair is persisted immediately.
- Daily polling by default; configurable between 1 and 24 hours.
- Monthly consumption and cost sensors with long-term statistics.

## Entities

| Entity      | Unit | Meaning                                                                                        |
| ----------- | ---- | ---------------------------------------------------------------------------------------------- |
| Consumption | kWh  | Energy consumed in the current Sorgenia billing cycle. Suitable as an Energy Dashboard source. |
| Cost        | €    | Total cost currently reported for the billing cycle.                                           |

Both entities use the billing-cycle start returned by Sorgenia as their reset point. This lets Home Assistant handle a new month and eventual billing corrections correctly.

> [!NOTE]
> The cost sensor is a total cost, not an energy-price sensor in €/kWh. Do not select it as the Energy Dashboard price source.

## Installation

Install through [HACS](https://hacs.xyz/):

1. Add `petretiandrea/hass-sorgenia` as a custom integration repository.
2. Download **Sorgenia**.
3. Restart Home Assistant.
4. Go to **Settings** → **Devices & services** → **Add integration** and search for **Sorgenia**.

For a manual installation, copy `custom_components/sorgenia/` into your Home Assistant `custom_components` directory and restart Home Assistant.

## Configuration

The setup wizard offers two methods.

### Username, password and OTP

Use this for a normal first setup:

1. Choose **Sign in with username and password**.
2. Enter your Sorgenia username, password, client code and POD.
3. If requested, enter the OTP sent by Sorgenia.

The password is used only for authentication and is not stored. Home Assistant stores the tokens needed for later refreshes.

### Existing session tokens

Use this when you already have a valid Sorgenia access token and refresh token and want to avoid consuming an OTP:

1. Choose **Use existing session tokens**.
2. Enter username, client code, POD, access token and refresh token.
3. The integration validates the pair against Sorgenia. If the access token has expired, it refreshes it and stores the rotated pair.

The username is needed for future refreshes; client code and POD identify the electricity supply.

## Options

After setup, open **Configure** on the Sorgenia integration to set the update interval. The default is 24 hours. More frequent polling is generally unnecessary because Sorgenia reports billing-cycle aggregates rather than live meter readings.

## Service action

`sorgenia.refresh_data` forces an immediate update for one config entry.

```yaml
service: sorgenia.refresh_data
data:
  config_entry_id: YOUR_CONFIG_ENTRY_ID
```

The action returns the refresh timestamp and whether the update succeeded.

## Troubleshooting

- **Authentication failed:** reconfigure the integration with a new username/password, or remove and add it again using current tokens.
- **No current billing interval:** Sorgenia may not yet have published the current-cycle aggregate. Try again later.
- **OTP limit reached:** use the existing-token setup method whenever a valid token pair is available.

To enable debug logging:

```yaml
logger:
  logs:
    custom_components.sorgenia: debug
```

## Contributing

Contributions and bug reports are welcome. Please include Home Assistant version, integration logs with secrets removed, and a redacted API response when reporting a data-parsing issue.

[releases-shield]: https://img.shields.io/github/release/petretiandrea/hass-sorgenia.svg?style=for-the-badge
[releases]: https://github.com/petretiandrea/hass-sorgenia/releases
[commits-shield]: https://img.shields.io/github/commit-activity/y/petretiandrea/hass-sorgenia.svg?style=for-the-badge
[commits]: https://github.com/petretiandrea/hass-sorgenia/commits/main
[license-shield]: https://img.shields.io/github/license/petretiandrea/hass-sorgenia.svg?style=for-the-badge
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[hacs]: https://github.com/hacs/integration
[maintenance-shield]: https://img.shields.io/maintenance/yes/2026.svg?style=for-the-badge
