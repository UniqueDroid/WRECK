"""Watch face files in JieLi's "JL" format (seen on 368x448 watches such as the M78).

Specification: docs/formats/jl-watchface.md. Read and validate only; this module
contains no vendor data.
"""
from __future__ import annotations

import struct

TYPES = {
    0x01: "image", 0x02: "image sequence", 0x03: "style image", 0x05: "rotating image (compass)",
    0x06: "special animation", 0x07: "rotating image (compass)", 0x14: "style colour",
    0x32: "hour", 0x33: "minute", 0x34: "month", 0x35: "day", 0x36: "hour hand", 0x37: "minute hand",
    0x38: "second hand (ticking)", 0x39: "second hand (sweeping)", 0x3A: "hour as image index",
    0x3B: "second", 0x3C: "year", 0x3D: "second hand (fast sweep)", 0x3E: "hour tens",
    0x3F: "hour units", 0x40: "minute tens", 0x41: "minute units", 0x42: "24-hour hand",
    0x44: "day hand", 0x45: "month hand",
    0x63: "weekday", 0x64: "weekday", 0x65: "Bluetooth", 0x66: "battery level image", 0x67: "AM/PM",
    0x68: "battery percent", 0x6A: "weather icon", 0x6B: "temperature", 0x6C: "temperature unit",
    0x6D: "temperature", 0x6E: "cycle phase",
    0x94: "compass degrees", 0x95: "compass direction", 0x96: "steps", 0x97: "calories", 0x98: "heart rate",
    0x99: "distance", 0x9A: "sleep hours", 0x9B: "sleep minutes", 0x9C: "unread notifications",
    0x9D: "heart rate day graph", 0x9E: "blood oxygen", 0x9F: "body temperature (fixed value)",
    0xA0: "steps progress", 0xA1: "calories progress", 0xA2: "distance progress", 0xA3: "heart rate scale",
    0xA4: "blood oxygen scale", 0xA5: "steps per hour",
    0xB4: "tap area", 0xB5: "seconds cut-out",
    0xE6: "tap area (next element)", 0xE7: "selectable area", 0xE8: "selectable area", 0xE9: "selectable area",
    0xEA: "photo background",
}

VISIBILITY = {0: "normal", 1: "skipped", 2: "dimmed AOD only"}
FORMATS = {2: "RGB565 RLE, opaque", 8: "ARGB (A + RGB565), transparent", 5: "unknown (5)", 6: "unknown (6)"}
ELEMENT_SIZE = 24
MAX_ELEMENTS = 88


class FormatError(ValueError):
    pass


def parse(data: bytes) -> dict:
    if len(data) < 4 or data[2:4] != b"JL" or data[1] != 0:
        raise FormatError("Not a JL watch face (expected byte 1 = 0 and bytes 2-3 = 'JL')")
    count = data[0]
    if count == 0 or count > MAX_ELEMENTS:
        raise FormatError(f"Implausible element count {count}")
    end = 4 + count * ELEMENT_SIZE
    if end > len(data):
        raise FormatError("File shorter than its element table")
    elements = []
    warnings = []
    for i in range(count):
        e = data[4 + i * ELEMENT_SIZE: 4 + (i + 1) * ELEMENT_SIZE]
        typ, vis, x, y, nimg, fmt, colour, w, h, b14, b15, off, b20, align, b22, variant = struct.unpack(
            "<BBHHBBHHHBBIBBBB", e)
        el = {
            "index": i, "type": typ, "type_name": TYPES.get(typ, "unknown"),
            "visibility": VISIBILITY.get(vis, vis), "x": x, "y": y, "width": w, "height": h,
            "images": nimg, "image_format": FORMATS.get(fmt, fmt), "colour_or_angle": colour,
            "group_or_end_angle": b14 | (b15 << 8), "data_offset": off,
            "param20": b20, "align": align, "param22": b22, "variant": variant,
        }
        if nimg and not (end <= off < len(data)):
            warnings.append(f"element {i}: image data offset 0x{off:x} outside the file")
        if typ not in TYPES:
            warnings.append(f"element {i}: unknown type 0x{typ:02x}")
        elements.append(el)
    return {"format": "jl-watchface", "elements": count, "size": len(data), "items": elements, "warnings": warnings}
