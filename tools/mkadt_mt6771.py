#!/usr/bin/env python3
"""Build the Apple Device Tree for OPPO F9 Pro (MT6771 / Helio P60).
Based on ios-sweet mkadt.py, adapted for MT6771 MMIO, framebuffer (0x773b0000), and MSDC eMMC host.
"""
import hashlib, os, struct, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import adt

PHYS_BASE = 0x40000000
MEM_SIZE = 0x160000000  # ~5.5 GB total RAM
PANIC_LOG_SIZE = 0x100000
SOC_BASE = 0x10000000

# MT6771 GIC and Framebuffer derived from inventory evidence (dump-test.dts)
GICD, GICD_SIZE = 0x0c000000, 0x10000
GICR, GICR_SIZE = 0x0c0a0000, 0x100000
FB, FB_SIZE = 0x773b0000, 0x2250000
MT6771_ECID = 0x4350483138323301  # 'CPH1823' + 1
FB_W, FB_H, FB_STRIDE = 1080, 2340, 1080 * 4
MSDC, MSDC_SIZE = 0x11230000, 0x1000
TIMEBASE = 13000000  # MT6771 generic timer base frequency (13 MHz)
VTIMER_INTID = 27

BOOT_MANIFEST_HASH = hashlib.sha384(b'hackios-f9pro boot manifest').digest()
D22AP_ADT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../research/ipsw-x/d22ap.adt')

def d22ap_product(path=D22AP_ADT):
    if not os.path.exists(path):
        print(f'warning: {path} missing, no /product node', file=sys.stderr)
        return []
    root, _ = adt.parse(open(path, 'rb').read())
    for c in root.children:
        if dict((k, v) for k, f, v in c.props).get('name') == b'product\0':
            return [(k, v) for k, f, v in c.props if not f and k not in ('name', 'AAPL,phandle')]
    return []

u32 = lambda *v: struct.pack('<%dI' % len(v), *v)
u64 = lambda *v: struct.pack('<%dQ' % len(v), *v)
cstr = lambda s: s.encode() + b'\0'

def node(name, props=(), children=()):
    n = adt.Node()
    n.props = [('name', 0, cstr(name))] + [(k, 0, v) for k, v in props]
    n.children = list(children)
    return n

def build():
    seed = os.urandom(64)
    phandle = iter(range(1, 1000))
    ph = lambda: ('AAPL,phandle', u32(next(phandle)))

    chosen = node('chosen', [
        ph(),
        ('dram-base', u64(PHYS_BASE)),
        ('dram-size', u64(MEM_SIZE)),
        ('random-seed', seed),
        ('debug-enabled', u32(1)),
        ('embedded-panic-log-size', u32(PANIC_LOG_SIZE)),
        ('firmware-version', cstr('hackios-mt6771-shim')),
        ('system-firmware-version', cstr('hackios-mt6771-shim')),
        ('boot-manifest-hash', BOOT_MANIFEST_HASH),
        ('crypto-hash-method', cstr('sha2-384')),
    ])

    defaults = node('defaults', [ph(), ('platform-name', cstr('mt6771'))])
    
    cpus = node('cpus', [ph()], [
        node('cpu0', [ph(), ('cpu-id', u32(0)), ('reg', u64(0)), ('device_type', cstr('cpu')), ('status', cstr('okay'))]),
        node('cpu1', [ph(), ('cpu-id', u32(1)), ('reg', u64(1)), ('device_type', cstr('cpu')), ('status', cstr('okay'))]),
        node('cpu2', [ph(), ('cpu-id', u32(2)), ('reg', u64(2)), ('device_type', cstr('cpu')), ('status', cstr('okay'))]),
        node('cpu3', [ph(), ('cpu-id', u32(3)), ('reg', u64(3)), ('device_type', cstr('cpu')), ('status', cstr('okay'))]),
        node('cpu4', [ph(), ('cpu-id', u32(4)), ('reg', u64(0x100)), ('device_type', cstr('cpu')), ('status', cstr('okay'))]),
        node('cpu5', [ph(), ('cpu-id', u32(5)), ('reg', u64(0x101)), ('device_type', cstr('cpu')), ('status', cstr('okay'))]),
        node('cpu6', [ph(), ('cpu-id', u32(6)), ('reg', u64(0x102)), ('device_type', cstr('cpu')), ('status', cstr('okay'))]),
        node('cpu7', [ph(), ('cpu-id', u32(7)), ('reg', u64(0x103)), ('device_type', cstr('cpu')), ('status', cstr('okay'))]),
    ])

    arm_io = node('arm-io', [
        ph(),
        ('ranges', b''),
        ('clock-frequency', u32(TIMEBASE)),
        ('voltage-states', u32(0)),
    ], [
        node('interrupt-controller', [ph(), ('compatible', cstr('arm,gic-v3')), ('reg', u64(GICD, GICD_SIZE, GICR, GICR_SIZE))]),
        node('timer', [ph(), ('interrupts', u32(VTIMER_INTID, 0xf))]),
        node('pmgr', [ph(), ('reg', u64(SOC_BASE, 0x100000))]),
        node('uart0', [ph(), ('reg', u64(0x11002000, 0x1000)), ('clock-frequency', u32(26000000))]),
        node('msdc0', [ph(), ('reg', u64(MSDC, MSDC_SIZE)), ('compatible', cstr('mediatek,mt6771-msdc'))]),
    ])

    fbcon = node('framebuffer', [
        ph(),
        ('reg', u64(FB, FB_SIZE)),
        ('width', u32(FB_W)),
        ('height', u32(FB_H)),
        ('rowbytes', u32(FB_STRIDE)),
        ('pixel-format', u32(0x2)),
    ])

    product = [node('product', [(k, v) for k, v in d22ap_product()])] if os.path.exists(D22AP_ADT) else []

    root = node('device-tree', [('compatible', cstr('apple,device-tree')), ('processor-frequency', u32(2000000000)), ('timebase-frequency', u32(TIMEBASE)), ('clock-frequency', u32(TIMEBASE)), ('ecid', u64(MT6771_ECID))], [chosen, defaults, cpus, arm_io, fbcon] + product)
    return adt.serialize(root)

if __name__ == '__main__':
    out_path = sys.argv[1] if len(sys.argv) > 1 else 'mt6771.adt'
    adt_bytes = build()
    open(out_path, 'wb').write(adt_bytes)
    print(f'Successfully built OPPO F9 Pro MT6771 ADT -> {out_path} ({len(adt_bytes)} bytes)')
