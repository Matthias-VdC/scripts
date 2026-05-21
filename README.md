# Scripts Overview

| Script Name | Language | Description | Tools |
| :--- | :--- | :--- | :--- |
| [**`nuphy-keepalive`**](#1-nuphy-keep-alive-rust--python) | Rust / Python | Prevents NuPhy Air75 HE (and similar) keyboards from continuously reconnecting/sleeping. Rust version is recommended for lower resource usage. | `hidraw`, `udev` |
| [**`undervolt.sh`**](#2-undervolt-amd-cpu-undervoltsh) | Bash | Automates Ryzen CPU undervolting. Applies Curve Optimizer offsets and runs stress tests to verify stability. | `ryzenadj`, `mprime`, `7zip` |
| [**`pulsar-4k`**](#3-pulsar-4k-dongle-pulsar-4kpy) | Python | A Linux CLI for the Pulsar 4K Dongle (`3554:f509`). Pulsar's own software (Fusion) is Windows only. Reads several mouse settings (battery, DPI, LOD, debounce, etc.). Should work with any mouse that uses this dongle (X2H, X2V2, X2A). | `hidapi` |

---

## 1. NuPhy Keep-Alive (Rust & Python)

Fixes the issue where NuPhy keyboards (specifically the Air75 HE) disconnect or go to sleep aggressively on Linux. It works by scanning for the device ID `19f5:6120` (specifically the vendor interface) and sending a specific 64-byte initialization packet every 60 seconds.

### Option A: Rust Version (Recommended)
**File:** [`nuphy-keepalive/rust/src/main.rs`](./nuphy-keepalive/rust/src/main.rs)

A compiled binary that is lighter on resources and handles device reconnection automatically.

**Build & Install:**
```bash
cd nuphy-keepalive/rust
cargo build --release
sudo cp target/release/nuphy-keepalive-rust /usr/local/bin/nuphy-keepalive-rust
```

**Run:**   
add this systemd service:

```bash
sudo nano /etc/systemd/system/nuphy-keepalive.service
```

```service
[Unit]
Description=NuPhy Air75 HE Keep-Alive Daemon (Rust)
After=network.target

[Service]
ExecStart=/usr/local/bin/nuphy-keepalive-rust
Restart=always
User=root

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now nuphy-keepalive
sudo systemctl status nuphy-keepalive
```

### Option B: Python Version
**File:** [`nuphy-keepalive/nuphy-keepalive.py`](./nuphy-keepalive/nuphy-keepalive.py)

Useful for quick editing or if you do not have a Rust toolchain installed. Requires a Systemd service to handle restarts if the device disconnects.

---

## 2. Undervolt AMD CPU (`undervolt.sh`)

**File:** [`undervolt/undervolt.sh`](./undervolt/undervolt.sh)

Automatically undervolts and stress tests / performance tests the applied undervolt using 7Zip and mprime. The undervolt is done using ryzenadj.

---

## 3. Pulsar 4K Dongle (`pulsar-4k.py`)

A Linux CLI for the Pulsar 4K Wireless Dongle (VID:PID `3554:f509`). Pulsar's own configuration software, [Fusion](https://pulsar.gg/pages/download), only runs on Windows. This tool talks directly to the dongle over its vendor HID interface. Should work with any Pulsar wireless mouse that uses the 4K dongle (X2H, X2V2, X2A).

**File:** [`pulsar-4k/pulsar-4k.py`](./pulsar-4k/pulsar-4k.py)

**Requirements:** `pip install hidapi`

**Reads:**
```bash
sudo pulsar-4k/pulsar-4k.py [read]
                            battery       # battery percentage (0-100)
                            dpi           # active DPI value
                            dpi-list      # DPI value of each configured stage (one per line)
                            lod           # lift-off distance in mm (1 or 2)
                            debounce      # debounce time in ms
                            motion-sync   # 0 = off, 1 = on
                            angle-snap    # 0 = off, 1 = on
                            ripple        # 0 = off, 1 = on
                            auto-sleep    # seconds until sleep
                            polling       # polling rate in Hz (125/250/500/1000/2000/4000)
```

**Writes:**
```bash
sudo pulsar-4k/pulsar-4k.py [write] [args]
                            dpi <stage>           # switch active DPI stage (0-indexed)
                            dpi-set <stage> <dpi> # set DPI value of stage (50..26000, step 50)
                            lod <1|2>             # set lift-off distance (1mm or 2mm)
                            motion-sync <0|1>     # 0 = off, 1 = on
                            angle-snap <0|1>      # 0 = off, 1 = on
                            ripple <0|1>          # 0 = off, 1 = on
                            auto-sleep <seconds>  # 10..600 in steps of 10
                            debounce <ms>         # 0..30
                            polling <Hz>          # 125/250/500/1000/2000/4000
```

Reads print an integer on stdout. Writes are silent and validate their input before sending anything to the dongle. Working toward parity with all settings available in Fusion.
