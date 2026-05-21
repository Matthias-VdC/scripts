#!/usr/bin/env python3

import sys

import hid

VID = 0x3554
PID = 0xF509

DPI_STAGE_TABLE_ADDR = 0x0C
DPI_STEP = 50

SETTING_ADDRS = {
    "lod": 0x0A,
    "debounce": 0xA9,
    "motion-sync": 0xAB,
    "angle-snap": 0xAF,
    "ripple": 0xB1,
}

POLLING_RATES = {
    0x01: 1000,
    0x02: 500,
    0x04: 250,
    0x08: 125,
    0x10: 2000,
    0x20: 4000,
}

SETTING_WRITES = {
    "lod": {1, 2},
    "motion-sync": {0, 1},
    "angle-snap": {0, 1},
    "ripple": {0, 1},
}


def find_dongle():
    for iface in hid.enumerate(VID, PID):
        if iface["interface_number"] == 1:
            return iface["path"]
    return None


def build_packet(opcode, payload=b""):
    # 17 bytes summing to 0x55 (mod 256)
    # last byte is the checksum
    body = bytes([0x08, opcode]) + payload.ljust(14, b"\x00")
    return body + bytes([(0x55 - sum(body)) & 0xFF])


def query(opcode, payload=b"", timeout_ms=50):
    dongle = hid.device()
    dongle.open_path(find_dongle())
    try:
        dongle.write(build_packet(opcode, payload))
        return dongle.read(17, timeout_ms=timeout_ms)
    finally:
        dongle.close()


def flash_read(addr, length):
    payload = b"\x00" + addr.to_bytes(2, "big") + bytes([length])
    return query(0x08, payload)[6 : 6 + length]


def cell_bytes(*values):
    # appends a check byte so the cell sums to 0x55 (mod 256)
    return bytes(values) + bytes([(0x55 - sum(values)) & 0xFF])


def cell_to_dpi(cell):
    # cell layout: [low, low, high * 0x44, check]
    # v = (high << 8) | low
    v = cell[0] | ((cell[2] // 0x44) << 8)
    return (v + 1) * DPI_STEP  # = DPI


def setting_write(setting_id, data):
    payload = bytes([0x00, 0x00, setting_id, len(data)]) + data
    dongle = hid.device()
    dongle.open_path(find_dongle())
    try:
        dongle.write(build_packet(0x03))
        dongle.read(17, timeout_ms=200)
        dongle.write(build_packet(0x07, payload))
        dongle.read(17, timeout_ms=200)
    finally:
        dongle.close()


cmd = sys.argv[1]
if cmd in SETTING_WRITES and len(sys.argv) > 2:
    value = int(sys.argv[2])
    if value not in SETTING_WRITES[cmd]:
        raise ValueError(
            f"unsafe value {value} for {cmd}.\nallowed: {sorted(SETTING_WRITES[cmd])}"
        )
    setting_write(SETTING_ADDRS[cmd], cell_bytes(value))
elif cmd == "battery":
    print(query(0x04)[6])
elif cmd == "dpi":
    if len(sys.argv) > 2:
        value = int(sys.argv[2])
        count = flash_read(0x02, 1)[0]
        if not (0 <= value < count):
            raise ValueError(f"dpi stage {value} out of range.\nvalid: 0..{count - 1}")
        setting_write(0x04, cell_bytes(value))
    else:
        stage = flash_read(0x04, 1)[0]
        cell = flash_read(DPI_STAGE_TABLE_ADDR + stage * 4, 4)
        print(cell_to_dpi(cell))
elif cmd == "dpi-set":
    stage = int(sys.argv[2])
    dpi = int(sys.argv[3])
    count = flash_read(0x02, 1)[0]
    if not (0 <= stage < count):
        raise ValueError(f"stage {stage} out of range.\nvalid: 0..{count - 1}")
    if dpi % 50 != 0 or not (50 <= dpi <= 26000):
        raise ValueError(f"dpi {dpi} must be a multiple of 50, between 50 and 26000")
    v = dpi // 50 - 1
    low = v & 0xFF
    high = (v >> 8) * 0x44
    setting_write(DPI_STAGE_TABLE_ADDR + stage * 4, cell_bytes(low, low, high))
elif cmd == "auto-sleep":
    print(flash_read(0xB7, 1)[0] * 10)
elif cmd == "polling":
    print(POLLING_RATES[flash_read(0x00, 1)[0]])
elif cmd == "dpi-list":
    stage_count = flash_read(0x02, 1)[0]
    for i in range(stage_count):
        cell = flash_read(DPI_STAGE_TABLE_ADDR + i * 4, 4)
        print(cell_to_dpi(cell))
elif cmd in SETTING_ADDRS:
    print(flash_read(SETTING_ADDRS[cmd], 1)[0])
