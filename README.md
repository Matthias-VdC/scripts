# Scripts Overview

| Script Name | Language | Description | Tools |
| :--- | :--- | :--- | :--- |
| [**`nuphy-keepalive.py`**](#1-nuphy-keep-alive-nuphy-keepalivepy) | Python | Prevents NuPhy Air75 HE (and similar) keyboards from continuously reconnecting by copying the nuphy website packet | `hidraw`, `udev` |
| [**`undervolt.sh`**](#2-undervolt-amd-cpu) | Bash | Automates Ryzen CPU undervolting. Applies Curve Optimizer offsets and runs stress tests to verify stability. | `ryzenadj`, `mprime`, `7zip` |
---

## [1. NuPhy Keep-Alive (`nuphy-keepalive.py`)](./nuphy-keepalive.py)

Fixes the issue where NuPhy keyboards (specifically the Air75 HE) disconnect or go to sleep aggressively on Linux. It works by scanning for the device ID `19f5:6120` and sending a specific 64-byte initialization packet every 60 seconds.


## [2. Undervolt AMD CPU (`undervolt.sh`)](./undervolt.sh)

Automatically undervolts and stress tests / performance tests the applied undervolt using 7Zip and mprime. The undervolt is done using ryzenadj.
