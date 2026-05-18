# Verify if HID interfaces expose battery

import sys

import hid

VID = 0x3554
PID = 0xF509

interfaces = [i for i in hid.enumerate(VID, PID)]

for iface in interfaces:
    page = iface["usage_page"]
    usage = iface["usage"]
    is_battery = page == 0x0006 and usage == 0x0020
    flag = "  <- BATTERY!!!" if is_battery else ""
    print(
        f"IF{iface['interface_number']}",
        f"page=0x{page:04x}",
        f"usage=0x{usage:04x}{flag}",
        sep="  ",
    )
