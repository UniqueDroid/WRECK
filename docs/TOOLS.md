# External tools

WRECK itself is small (Python standard library only). Deeper analysis needs external tools. All their output belongs
in `private/<device>/decompiled/`.

| Tool | Purpose | Notes |
| --- | --- | --- |
| Ghidra | disassembler/decompiler | exotic CPUs (e.g. JieLi pi32v2) need a processor module; community modules are often incomplete – a successful build does not prove correct semantics. Check small test cases against known functions. |
| pypcode / SLEIGH | translate instructions to P-code, mini emulation | good for "running" single functions on the PC to verify claims |
| Jadx / Apktool | read the companion app | only what interoperability needs (protocol, file formats); no classes in the repo |
| Android HCI snoop log + Wireshark | capture the Bluetooth traffic of **your own** watch | Developer options → "Enable Bluetooth HCI snoop log" |
| nRF Connect | inspect the watch's GATT services/characteristics | pair your own device only |
| The chip vendor's SDK | recognise structures, drivers, names | check the licence; usually not redistributable |
| Community format tools | containers, resources | check the licence; use locally |

## Patterns for your own verification tools

- **Hash-pinned inputs:** a tool that expects a specific original file checks its SHA-256 and aborts otherwise. That
  way no build comes from the wrong base.
- **Output directory must be new:** never overwrite anything existing.
- **Verifier separate from builder:** the verifier re-reads the finished build and compares independently.
- **JSON report per run:** input hashes, output hashes, changed regions, `hardware_tested: false`.
