#!/usr/bin/env python3
"""Build the Hollow Knight: Silksong high-FPS patches (IPS32 + IPSwitch .pchtxt) for Eden.

No game files are needed: the patch is a table of 3 instructions.

    python tools/build_patches.py            # builds 120 and 240 FPS
    python tools/build_patches.py --hz 144   # experimental: any refresh rate

How the target rate maps to the patch: Eden treats a swap interval >= 5 as
"speed = interval / 100" for its emulated display vsync, so 60 Hz * interval/100 = target Hz.
"""
import argparse
import os
import struct

BUILD_ID = "DC3E4B892043EF2345C3EAF97A177E7C"  # Silksong main, update v1.0.28324 (v131072)
NSO_HEADER = 0x100  # IPS offsets for ExeFS patches include the NSO header
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def movz_w1(imm):
    return struct.pack("<I", 0x52800000 | (imm << 5) | 1)  # mov w1, #imm


def patches(interval):
    return [
        (0x120AF34, movz_w1(interval),
         f"window builder: ldr w1,[x21,#0x6f8] -> mov w1,#{interval} (initial NVN present interval)"),
        (0x11F27A8, struct.pack("<I", 0xF9462102),
         "interval setter: add x8,x8,#0xc40 / ldr x2,[x8] -> ldr x2,[x8,#0xc40] (frees a slot)"),
        (0x11F27AC, movz_w1(interval),
         f"interval setter: -> mov w1,#{interval} (always hand {interval} to nvnWindowSetPresentInterval)"),
    ]


def build(hz):
    interval = round(hz / 60 * 100)
    if not 5 <= interval <= 0xFFFF:
        raise SystemExit(f"{hz} Hz is out of range")
    name = f"{hz} FPS"
    ips = bytearray(b"IPS32")
    lines = [f"// Hollow Knight: Silksong {hz} FPS for Eden (swap interval {interval})",
             f"// Game: 010013C00E930000, update v1.0.28324, main build id {BUILD_ID}",
             f"@nsobid-{BUILD_ID}", "", "@flag offset_shift 0x100", "", "@enabled"]
    for addr, data, desc in patches(interval):
        ips += struct.pack(">IH", addr + NSO_HEADER, len(data)) + data
        lines.append(f"// {desc}")
        lines.append(f"{addr:08X} {data.hex().upper()}")
    ips += b"EEOF"
    lines += ["@stop", ""]

    mod_dir = os.path.join(ROOT, "mods", name, "exefs")
    os.makedirs(mod_dir, exist_ok=True)
    with open(os.path.join(mod_dir, BUILD_ID + ".ips"), "wb") as f:
        f.write(ips)
    os.makedirs(os.path.join(ROOT, "pchtxt"), exist_ok=True)
    with open(os.path.join(ROOT, "pchtxt", f"silksong-{hz}fps.pchtxt"), "w", newline="\n") as f:
        f.write("\n".join(lines))
    print(f"built {name}: interval {interval}, {len(ips)} byte IPS")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--hz", type=int, action="append", help="target refresh rate (default: 120 and 240)")
    for hz in ap.parse_args().hz or [120, 240]:
        build(hz)
