#!/usr/bin/env python3
# print battery % of pulsar mouse

import hid

VID = 0x3554
PID = 0xF509

# all 17 bytes combined = 0x55
# the last byte is the checksum
QUERY = bytes.fromhex("0804" + "00" * 14 + "49")

path = next(i["path"] for i in hid.enumerate(VID, PID) if i["interface_number"] == 1)

h = hid.device()
try:
    h.open_path(path)
    h.write(QUERY)
    reply = h.read(17, timeout_ms=50)
finally:
    h.close()

print(reply[6])
