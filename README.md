# Yocto Toolchain SDK for AI SDK (Sparrow Hawk)

This branch holds the Releases of the Yocto toolchain SDK for Sparrow Hawk
(`poky-glibc-*-toolchain-*.sh`), tagged `toolchain-vYYYY-MM-DD`. The toolchain
is a different thing from the AI SDK itself.

This document records how each released toolchain was built. Add a new section
for every new Release, newest first.

## toolchain-v2026-10-30

### Build command

```bash
git clone https://github.com/rcar-community/meta-sparrow-hawk -b v2026-10-30
cd meta-sparrow-hawk
./build.sh --weston --sdk --sbom
```

### Commits

| Layer | Repository | Commit |
| --- | --- | --- |
| meta-openembedded | https://git.openembedded.org/meta-openembedded | 0f00f8b9a21950640da8c5707343e5540133f86e |
| poky | https://git.yoctoproject.org/poky | 64e69ed23703f6358ec431d3f5f1f8483f974cae |
| meta-sparrow-hawk | https://github.com/rcar-community/meta-sparrow-hawk | 8ceffbe3fa9966d8db1cdc7bb540a2ed9707bfdb |

### Build machine

| Item | Value |
| --- | --- |
| OS | Ubuntu 24.04.5 LTS (x86_64) |
| CPU | AMD Ryzen 9 8945HX (32 threads) |
| Memory | 32 GB |

