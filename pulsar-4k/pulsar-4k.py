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


cmd = sys.argv[1]
if cmd == "battery":
    print(query(0x04)[6])
elif cmd == "dpi":
    stage = flash_read(0x04, 1)[0]
    cell = flash_read(DPI_STAGE_TABLE_ADDR + stage * 4, 4)
    print((cell[0] + 1) * DPI_STEP)
elif cmd == "auto-sleep":
    print(flash_read(0xB7, 1)[0] * 10)
elif cmd == "polling":
    print(POLLING_RATES[flash_read(0x00, 1)[0]])
elif cmd in SETTING_ADDRS:
    print(flash_read(SETTING_ADDRS[cmd], 1)[0])
