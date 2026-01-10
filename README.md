# Scripts Overview

| Script Name | Language | Description | Tools |
| :--- | :--- | :--- | :--- |
| [**`nuphy-keepalive`**](#1-nuphy-keep-alive-rust--python) | Rust / Python | Prevents NuPhy Air75 HE (and similar) keyboards from continuously reconnecting/sleeping. Rust version is recommended for lower resource usage. | `hidraw`, `udev` |
| [**`undervolt.sh`**](#2-undervolt-amd-cpu-undervoltsh) | Bash | Automates Ryzen CPU undervolting. Applies Curve Optimizer offsets and runs stress tests to verify stability. | `ryzenadj`, `mprime`, `7zip` |

---

## 1. NuPhy Keep-Alive (Rust & Python)

Fixes the issue where NuPhy keyboards (specifically the Air75 HE) disconnect or go to sleep aggressively on Linux. It works by scanning for the device ID `19f5:6120` (specifically the vendor interface) and sending a specific 64-byte initialization packet every 60 seconds.

### Option A: Rust Version (Recommended)
**File:** [`nuphy-keepalive-rust/src/main.rs`](./nuphy-keepalive-rust/src/main.rs)

A compiled binary that is lighter on resources and handles device reconnection automatically.

**Build & Install:**
```bash
cd nuphy-keepalive-rust
cargo build --release
sudo cp target/release/nuphy-keepalive-rust /usr/local/bin/nuphy-keepalive-rust
```

**Run:**
Add this to your window manager startup (e.g., Niri, Sway, Hyprland config):
```bash
/usr/local/bin/nuphy-keepalive-rust &
```

or this for a systemd service:

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

### Option B: Python Version
**File:** [`nuphy-keepalive.py`](./nuphy-keepalive.py)

Useful for quick editing or if you do not have a Rust toolchain installed. Requires a Systemd service to handle restarts if the device disconnects.

---

## [2. Undervolt AMD CPU (`undervolt.sh`)](./undervolt.sh)

Automatically undervolts and stress tests / performance tests the applied undervolt using 7Zip and mprime. The undervolt is done using ryzenadj.
