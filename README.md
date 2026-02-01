
# Sonoff LAN Friendly Entity IDs (Fork)

>This is a fork of the original [AlexxIT/SonoffLAN](https://github.com/AlexxIT/SonoffLAN) integration.

The purpose of this fork is to improve entity_id readability in Home Assistant by adding the device friendly name into the generated entity IDs.

---

## ✨ What This Fork Changes

The original SonoffLAN integration creates entity IDs using only the device ID:

- `switch.sonoff_1000xxxx_1`

With many devices, this becomes difficult to manage.

This fork generates entity IDs that include the user-defined device name from the eWeLink/Sonoff app:

- `switch.sonoff_salon_lamba_1000xxxx_1`

---

## ✅ Features

- Friendly and readable entity IDs
- Multi-channel device support (`_1`, `_2`, `_3`, `_4`)
- Turkish character support (ı, İ, ğ, ş, ç, ö, ü)
- Works across all entity types:
  - switch, sensor, light, cover, climate, remote, binary_sensor
- Backward compatible:
  - Existing installations are not renamed automatically
  - New installations and newly added devices use the new format

---

## 📋 Examples

| Original Entity ID | New Entity ID |
|-------------------|--------------|
| `switch.sonoff_1000xxxx_1` | `switch.sonoff_salon_lamba_1000xxxx_1` |
| `sensor.sonoff_1000xxxx_power` | `sensor.sonoff_salon_lamba_1000xxxx_power` |
| `light.sonoff_1000xxxx` | `light.sonoff_salon_lamba_1000xxxx` |
| `cover.sonoff_1000xxxx` | `cover.sonoff_perde_1000xxxx` |

---

## 🚀 Installation (HACS Custom Repository)

1. Open **HACS → Integrations**
2. Click the menu (⋮) → **Custom repositories**
3. Add this repository URL:

```

[https://github.com/levonisyas/SonoffLAN-friendly-entity-ids](https://github.com/levonisyas/SonoffLAN-friendly-entity-ids)

```

4. Select category: **Integration**
5. Search for:

**Sonoff LAN Friendly Entity IDs**

6. Install and restart Home Assistant

---

## 🔗 Links

- Original Integration:  
https://github.com/AlexxIT/SonoffLAN

- Related Pull Request:  
https://github.com/AlexxIT/SonoffLAN/pull/1693

---

## 🙏 Credits

All credits for the original integration belong to **AlexxIT** and contributors.

This fork only adds improved entity_id naming support.


