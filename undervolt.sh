#!/bin/bash

TEST_DURATION="1800s" # 30min by default

# 1 = Smallest FFTs (tests L1/L2 caches, high power/heat/CPU stress).
# 2 = Small FFTs (tests L1/L2/L3 caches, maximum power/heat/CPU stress).
# 3 = Large FFTs (stresses memory controller and RAM).
# 4 = Blend (tests all of the above).
MPRIME_TEST_CHOICE=2


# ___ Colors ___
C_RED='\033[0;31m'
C_GREEN='\033[0;32m'
C_YELLOW='\033[1;33m'
C_BLUE='\033[0;34m'
C_NC='\033[0m'

info() { echo -e "${C_BLUE}INFO: $1${C_NC}"; }
warn() { echo -e "${C_YELLOW}WARN: $1${C_NC}"; }
error() { echo -e "${C_RED}ERROR: $1${C_NC}"; }
success() { echo -e "${C_GREEN}SUCCESS: $1${C_NC}"; }

# ___ Start __


# 1. Check input undervolt value
if [ -z "$1" ]; then
    error "No undervolt value provided."
    echo "Usage: $0 <value>"
    echo "Example: $0 -5"
    exit 1
fi

STEP_VALUE=$1
BENCH_DIR="$HOME/Documents/benchmark"
FILE_NAME="${BENCH_DIR}/benchmark_results_${STEP_VALUE}.txt"


# 2. Check for root (to allow install with pacman and modprobe)
warn "This script needs sudo access to install packages and apply settings"
sudo -v # asks password and caches it for 5 min (default)
if [ $? -ne 0 ]; then
    error "Failed to get sudo permissions. Exiting..."
    exit 1
fi


# 3. Check and install dependencies if necessary
info "Checking dependencies..."

### 7zip (used for bench)
if ! pacman -Q 7zip &>/dev/null; then
    warn "7zip (7z) not found. Installing..."
    sudo pacman -S --noconfirm 7zip
fi

### mprime
if ! pacman -Q mprime &>/dev/null; then
    warn "mprime not found. Installing..."
    sudo pacman -S --noconfirm mprime
fi

### ryzen_smu-dkms-git
if ! pacman -Q ryzen_smu-dkms-git &>/dev/null; then
    warn "ryzen_smu-dkms-git not found. Installing..."
    sudo pacman -S --noconfirm ryzen_smu-dkms-git
fi

### ryzenadj-git
if ! pacman -Q ryzenadj-git &>/dev/null; then
    warn "ryzenadj-git not found. Installing..."
    sudo pacman -S --noconfirm ryzenadj-git
fi

success "All dependencies are installed."


# 4. Activating ryzen_smu module
info "Checking ryzen_smu module..."
if ! lsmod | grep -q ryzen_smu; then
    warn "ryzen_smu module not loaded. Loading..."
    sudo modprobe ryzen_smu
    if [ $? -ne 0 ]; then
        error "Failed to load ryzen_smu module. Exiting..."
        exit 1
    fi
fi
success "ryzen_smu is loaded."


# 5. Verify ryzenadj support/working
info "Verifying ryzenadj..."
if ! sudo ryzenadj --help &>/dev/null; then
    error "ryzenadj command failed to execute. Exiting..."
    exit 1
fi
success "ryzenadj is working."


# 6. Apply ryzenadj undervolt
info "Applying undervolt..."
if ! sudo ryzenadj --set-coall=$STEP_VALUE; then
    error "Failed to apply ryzenadj value. Exiting..."
    exit 1
fi
success "Undervolt applied."


# 7. Run 7z bench
info "Running 10-pass 7z benchmark..."
mkdir -p "$BENCH_DIR"
echo "Benchmark for Curve Optimizer = $STEP_VALUE" > "$FILE_NAME"
for i in {1..10}; do
    echo "--- START RUN $i ---" >> "$FILE_NAME"
    7z b >> "$FILE_NAME" 2>&1
    echo "--- END RUN $i ---" >> "$FILE_NAME"
    echo "" >> "$FILE_NAME"
done
success "Benchmark complete. Results saved to $FILE_NAME"


# 8. Run mprime stress test
warn "!!! STARTING ${TEST_DURATION} STRESS TEST FOR $STEP_VALUE !!!"
warn "The system may crash if the undervolt is unstable."
warn "If it crashes, reboot, and DO NOT re-run with this value."
warn "Starting in 5 seconds..."
sleep 5

info "Creating mprime config (prime.txt) for non-interactive test..."
echo TortureTestChoice="$MPRIME_TEST_CHOICE" > prime.txt

yes N | timeout $TEST_DURATION mprime -t

MPRIME_EXIT_CODE=$?


# 9. Results
if [ $MPRIME_EXIT_CODE -eq 124 ]; then
    # 124 = 'timeout' killed the command, it survived
    success "***************************************************"
    success "STEP $STEP_VALUE PASSED ${TEST_DURATION} STRESS TEST!"
    success "You can now try the next step: $((STEP_VALUE - 1))"
    success "***************************************************"
else
    error "***************************************************"
    error "STEP $STEP_VALUE FAILED!"
    error "mprime exited with code $MPRIME_EXIT_CODE (a crash or worker error)."
    error "You should try a lower step like: $((STEP_VALUE + 1))."
    error "DO NOT PROCEED to the next step."
    error "***************************************************"
fi

# clean up
rm prime.txt
