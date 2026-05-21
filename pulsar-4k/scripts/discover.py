# Verify if HID interfaces expose battery via the standard usage.

import hid

VID = 0x3554
PID = 0xf509

for iface in hid.enumerate(VID, PID):
    page = iface["usage_page"]
    usage = iface["usage"]
    # HID Generic Device page 0x06, usage 0x20 = Battery Strength
    is_battery = page == 0x0006 and usage == 0x0020
    flag = "  <- BATTERY!!!" if is_battery else ""
    print(
        f"IF{iface['interface_number']}",
        f"page=0x{page:04x}",
        f"usage=0x{usage:04x}{flag}",
        sep="  ",
    )
