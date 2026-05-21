#!/usr/bin/env python3

import sys
import hid

VID = 0x3554
PID = 0xF509


def find_dongle():
    for iface in hid.enumerate(VID, PID):
        if iface["interface_number"] == 1:
            return iface["path"]
    return None


def build_packet(opcode, payload=b""):
    # 17 bytes summing to 0x55 (mod 256); last byte is the checksum
    body = bytes([0x08, opcode]) + payload.ljust(14, b"\x00")
    return body + bytes([(0x55 - sum(body)) & 0xff])


def query(opcode, payload=b"", timeout_ms=50):
    dongle = hid.device()
    dongle.open_path(find_dongle())
    try:
        dongle.write(build_packet(opcode, payload))
        return dongle.read(17, timeout_ms=timeout_ms)
    finally:
        dongle.close()


if sys.argv[1] == "battery":
    print(query(0x04)[6])
