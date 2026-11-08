# HACKiOS — OPPO F9 Pro (CPH1823 / MT6771) XNU Kernel Patch Blueprint

To successfully boot XNU on MediaTek MT6771 (Helio P60) beyond the early shim phase, a custom XNU kernel patch series (analogous to `ios-sweet/xnu/patches/`) must be developed. This document outlines the required kernel-side architecture changes.

## 1. Platform Expert (`PE_init` / Machine Config)
- **Target:** `osfmk/arm64/` or platform expert initialization.
- **Requirement:** Replace Qualcomm platform identification (`sweet`) with MediaTek MT6771 machine configuration, mapping MT6771 system controller and timer base frequencies (13 MHz).

## 2. Interrupt Controller (GICv3 / GICv2)
- **Target:** `pexpert/arm64/` or ARM GIC driver.
- **Requirement:** Ensure XNU maps the MT6771 GIC distributor (`0x0c000000`) and redistributor (`0x0c0a0000`) correctly, mapping generic timer interrupts (PPI 27).

## 3. Storage Driver (`ufs` -> `msdc` eMMC)
- **Target:** `bsd/dev/` storage layer.
- **Requirement:** Implement a MediaTek MSDC eMMC host driver (`11230000.mmc`) to replace the Qualcomm UFS host driver, allowing XNU to mount the root filesystem on the device's eMMC storage partition (`mmcblk0` / `userdata`).

## 4. Framebuffer & Display (`AppleCLCD`)
- **Target:** `iokit/Kernel/arm/` display drivers.
- **Requirement:** Map MT6771 framebuffer base (`0x773b0000`, `mblock-11-framebuffer`) for software CoreAnimation rendering to the 1080p DSI panel.
