import logging

from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC
from homeassistant.helpers.entity import DeviceInfo, Entity, EntityCategory

from .const import DOMAIN
from .ewelink import XDevice, XRegistry

_LOGGER = logging.getLogger(__name__)

ENTITY_CATEGORIES = {
    "battery": EntityCategory.DIAGNOSTIC,
    "battery_voltage": EntityCategory.DIAGNOSTIC,
    "led": EntityCategory.CONFIG,
    "pulse": EntityCategory.CONFIG,
    "pulseWidth": EntityCategory.CONFIG,
    "rssi": EntityCategory.DIAGNOSTIC,
    "sensitivity": EntityCategory.CONFIG,
}

ICONS = {
    "dusty": "mdi:cloud",
    "led": "mdi:led-off",
    "noise": "mdi:bell-ring",
}

NAMES = {
    "led": "LED",
    "rssi": "RSSI",
    "pulse": "INCHING",
    "pulseWidth": "INCHING Duration",
}

def clean_device_name(name: str) -> str:
    """Clean user-defined device name for use in entity IDs.

    - Preserves Turkish characters by mapping them to ASCII equivalents
    - Replaces any non [a-z0-9_] chars with underscore
    - Collapses repeated underscores
    """
    tr_map = str.maketrans(
        {
            "Ü": "U",
            "İ": "I",
            "Ğ": "G",
            "Ş": "S",
            "Ç": "C",
            "Ö": "O",
            "ü": "u",
            "ı": "i",
            "ğ": "g",
            "ş": "s",
            "ç": "c",
            "ö": "o",
        }
    )

    s = (name or "").translate(tr_map).lower()

    out = []
    prev_us = False
    for ch in s:
        ok = ("a" <= ch <= "z") or ("0" <= ch <= "9") or ch == "_"
        if ok:
            if ch == "_":
                if not prev_us:
                    out.append("_")
                prev_us = True
            else:
                out.append(ch)
                prev_us = False
        else:
            if not prev_us:
                out.append("_")
                prev_us = True

    slug = "".join(out).strip("_")
    return slug or "device"

class XEntity(Entity):
    event: bool = False  # if True - skip set_state on entity init
    params: set = {}
    param: str = None
    uid: str = None

    _attr_should_poll = False
    def __setattr__(self, name, value):
        super().__setattr__(name, value)

        # XSwitches overwrites _attr_unique_id after XEntity.__init__ (for channels).
        # Keep entity_id/object_id in sync without touching switch.py.
        if name == "_attr_unique_id":
            try:
                self._apply_friendly_object_id()
            except Exception:
                # don't break entity init on any edge case
                pass

    def _apply_friendly_object_id(self) -> None:
        """Set suggested_object_id and entity_id using friendly device name + eWeLink deviceid.

        Examples:
          - switch.sonoff_salon_lamba_1000xxx
          - switch.sonoff_salon_lamba_1000xxx_1
          - sensor.sonoff_salon_lamba_1000xxx_power
        """
        deviceid = self.device["deviceid"]
        device_slug = clean_device_name(self.device.get("name", ""))

        # Extract suffix from unique_id: 1000xxx_1 -> "1", 1000xxx_power -> "power"
        tail = None
        uid = getattr(self, "_attr_unique_id", None)
        if isinstance(uid, str) and uid.startswith(f"{deviceid}_"):
            tail = uid[len(deviceid) + 1 :]

        object_id = f"sonoff_{device_slug}_{deviceid}"
        if tail:
            object_id = f"{object_id}_{tail}"

        self._attr_suggested_object_id = object_id
        self.entity_id = f"{DOMAIN}.{object_id}"

    def __init__(self, ewelink: XRegistry, device: XDevice) -> None:
        self.ewelink = ewelink
        self.device = device

        if self.param and self.uid is None:
            self.uid = self.param
        if self.param and not self.params:
            self.params = {self.param}

        if self.uid:
            self._attr_unique_id = f"{device['deviceid']}_{self.uid}"

            if not self.uid.isdigit():
                self._attr_entity_category = ENTITY_CATEGORIES.get(self.uid)
                self._attr_icon = ICONS.get(self.uid)

                s = NAMES.get(self.uid) or self.uid.title().replace("_", " ")
                self._attr_name = f"{device['name']} {s}"
            else:
                self._attr_name = device["name"]

        else:
            self._attr_name = device["name"]
            self._attr_unique_id = device["deviceid"]

        # For new installs / newly added devices: use friendly name + deviceid (+ tail like _1/_power)
        # NOTE: unique_id stays unchanged for backward compatibility.
        self._apply_friendly_object_id()

        deviceid: str = device["deviceid"]
        params: dict = device["params"]

        connections = (
            {(CONNECTION_NETWORK_MAC, params["staMac"])} if "staMac" in params else None
        )

        self._attr_device_info = DeviceInfo(
            connections=connections,
            identifiers={(DOMAIN, deviceid)},
            manufacturer=device.get("brandName"),
            model=device.get("productModel"),
            name=device["name"],
            sw_version=params.get("fwVersion"),
        )

        try:
            self.internal_update(None if self.event else params)
        except Exception as e:
            _LOGGER.error(f"Can't init device: {device}", exc_info=e)

        ewelink.dispatcher_connect(deviceid, self.internal_update)

        if parent := device.get("parent"):
            ewelink.dispatcher_connect(parent["deviceid"], self.internal_parent_update)

    def set_state(self, params: dict):
        pass

    def internal_available(self) -> bool:
        ok = self.ewelink.can_cloud(self.device) or self.ewelink.can_local(self.device)
        return ok

    def internal_update(self, params: dict = None):
        available = self.internal_available()
        change = False

        if self._attr_available != available:
            self._attr_available = available
            change = True

        if params and params.keys() & self.params:
            self.set_state(params)
            change = True

        if change and self.hass:
            self._async_write_ha_state()

    def internal_parent_update(self, params: dict = None):
        self.internal_update(None)

    async def async_update(self):
        if led := self.device["params"].get("sledOnline"):
            # device response with current status if we change any param
            await self.ewelink.send(
                self.device, params_lan={"sledOnline": led}, cmd_lan="sledonline"
            )
        else:
            await self.ewelink.send(self.device)
