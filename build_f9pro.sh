#!/usr/bin/env bash
set -e
echo "=================================================="
echo "HACKiOS — OPPO F9 Pro (CPH1823) Build Orchestrator"
echo "=================================================="

WORK_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$WORK_DIR"

echo "[1/7] Generating OPPO F9 Pro MT6771 Apple Device Tree (ADT)..."
python3 tools/mkadt_mt6771.py mt6771.adt

echo "[2/7] Verifying ADT binary output..."
if [ -f mt6771.adt ]; then
    echo "  -> mt6771.adt successfully generated ($(stat -c %s mt6771.adt) bytes)."
else
    echo "  -> Error: mt6771.adt generation failed."
    exit 1
fi

echo "[3/7] Running automated pipeline verification (ADT parser test)..."
python3 tools/test_pipeline.py

echo "[4/7] Packing XNU kernel + ADT into payload (mt6771_payload.bin)..."
KERNEL_SRC="/home/alienf4ckowl/ios16_on_polaris_mix2s/kernel.release.sweet"
if [ -f "$KERNEL_SRC" ]; then
    python3 tools/mkpayload_mt6771.py "$KERNEL_SRC" mt6771.adt shim/out/mt6771_payload.bin \
        --cmdline 'debug=0xc serial=3 cpus=8 keepsyms=1 -enable_kprintf_spam rd=ufsroot0 ufsrw=1 rootrw=1'
    echo "  -> Payload successfully packed ($(stat -c %s shim/out/mt6771_payload.bin) bytes)."
else
    echo "  -> Warning: Kernel source not found at $KERNEL_SRC, skipping payload pack."
    exit 1
fi

echo "[5/7] Verifying stock DTB from unpacked factory boot.img..."
if [ -f dtb/boot_unpacked/dtb ]; then
    echo "  -> Stock DTB present ($(stat -c %s dtb/boot_unpacked/dtb) bytes)."
else
    echo "  -> Error: Stock DTB missing."
    exit 1
fi

echo "[6/7] Compiling shim and packaging final boot image (shim-boot.img)..."
cd shim
./build.sh out/mt6771_payload.bin
cd ..
if [ -f shim/out/shim-boot.img ]; then
    echo "  -> shim-boot.img successfully built ($(stat -c %s shim/out/shim-boot.img) bytes)."
else
    echo "  -> Error: shim-boot.img build failed."
    exit 1
fi

echo "[7/7] Build environment and validation complete successfully."
echo "=================================================="
echo "Generated Artifact: shim/out/shim-boot.img"
echo "Ready for fastboot testing: fastboot boot shim/out/shim-boot.img"
echo "=================================================="
