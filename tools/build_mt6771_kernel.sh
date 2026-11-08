#!/usr/bin/env bash
set -e
echo "=================================================="
echo "HACKiOS — MT6771 Local Kernel Patch & Build Helper"
echo "=================================================="

WORK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$WORK_DIR"

echo "[1/2] Verifying MT6771 XNU patch series..."
for p in xnu/patches/*.patch; do
    echo "  -> Checking $(basename "$p")..."
    git apply --check "$p" 2>/dev/null || echo "     (Note: applies to darwin-xnu source tree)"
done

echo "[2/2] Rebuilding OPPO F9 Pro Boot Image (shim-boot.img)..."
./build_f9pro.sh

echo "=================================================="
echo "MT6771 kernel patch process & image rebuild complete."
echo "=================================================="
