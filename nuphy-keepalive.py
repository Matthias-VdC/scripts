import os
import time
import glob
import sys

# This script emulates the keepalive code which is being sent by the drive.nuphy.io website.
# Otherwise my keyboard kept disconnecting and reconnecting.
# This is only tested and working on my keyboard, the Nuphy Air 75HE, and OS, CachyOS using Niri.
# If this script fixes your issue I recommend creating a systemd service for it instead of manually running it every time.

VENDOR_ID = "19f5"
PRODUCT_ID = "6120"

# Copied packet from website, captured through tshark
PACKET = bytes.fromhex("55 03 00 00 00 00 00 00 00 00 00 00 00 00 00 00" + (" 00" * 48))

def find_nuphy_device():
    # Finds the correct /dev/hidraw path.
    for path in glob.glob("/sys/class/hidraw/hidraw*"):
        try:
            with open(os.path.join(path, "device/uevent"), "r") as f:
                uevent = f.read()
                if f"HID_ID=0003:{VENDOR_ID.upper().zfill(8)}:{PRODUCT_ID.upper().zfill(8)}" in uevent:
                    return os.path.join("/dev", os.path.basename(path))
        except Exception:
            continue
    return None

def main():
    dev_path = find_nuphy_device()
    if not dev_path:
        print("NuPhy keyboard not found.")
        sys.exit(1)

    print(f"Opening device: {dev_path}")
    print("Holding connection open to prevent sleep...")

    try:
        # Open the device and keep it open, like the website does
        fd = os.open(dev_path, os.O_RDWR)

        # Send the init packet once
        os.write(fd, PACKET)
        print("Initialization packet sent.")

        # Infinite loop to keep the script (and file handle) alive
        while True:
            time.sleep(60)

    except OSError as e:
        print(f"Error: {e}")
    finally:
        # This only runs if the script is killed
        if 'fd' in locals():
            os.close(fd)

if __name__ == "__main__":
    main()
