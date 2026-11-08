# HACKiOS — OPPO F9 Pro (CPH1823 / MT6771) Boot Strategy & Mitigation

## 1. The MediaTek Fastboot Boot Limitation
Unlike Qualcomm platforms (e.g., Redmi Note 10 Pro `sweet` in `ios-sweet`) which support `fastboot boot` for temporary RAM execution of unsigned shims, MediaTek's LK (Little Kernel) bootloader does not implement `fastboot boot` for custom binaries. Attempting `fastboot boot` results in USB I/O failure (Error 31) because MediaTek LK expects signed boot headers or explicit partition flashing.

## 2. Safe Staging & Execution Strategy (Preserving Android)
To maintain compliance with the project rule **"Preserve the Android installation for now"**:
- **NO DESTRUCTIVE FLASHING:** Never flash test shims directly to live `boot` or `recovery` partitions without a verified SP Flash Tool backup and scatter file.
- **BROM / Preloader Mode (`mtkclient`):** MediaTek devices support entering BROM (Boot ROM) mode via hardware testpoints or key combinations (Volume Up + Volume Down during USB plug-in). `mtkclient` allows secure, read-only inspection and temporary memory payload injection without overwriting permanent eMMC partitions (`mmcblk0`).
- **Custom Recovery Integration:** Alternatively, staging the shim/payload execution from a custom recovery (e.g., OrangeFox) environment provides a controlled test vector.

## 3. Current Build Status
- **ADT Generation:** `tools/mkadt_mt6771.py` successfully produces `mt6771.adt` (7,244 bytes) with `d22ap.adt` product integration.
- **Payload Packaging:** `tools/mkpayload_mt6771.py` successfully packs XNU kernel Mach-O and ADT into `mt6771_payload.bin` (11.7 MB).
- **Shim & Boot Image:** `shim/out/shim-boot.img` (11.96 MB) successfully built and packaged via `build_f9pro.sh`.
