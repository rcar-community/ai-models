# Yocto Toolchain SDK for AI SDK (Sparrow Hawk)

This branch holds the Releases of the Yocto toolchain SDK for Sparrow Hawk
(`poky-glibc-*-toolchain-*.sh`), tagged `toolchain-vYYYY-MM-DD`. The toolchain
is a different thing from the AI SDK itself.

This document records how each released toolchain was built. Add a new section
for every new Release, newest first.

## toolchain-v2026-10-23-2ab46ab

### Build command

meta-sparrow-hawk v2026-10-23 with the 15 patches in [`patches/toolchain-v2026-10-23-2ab46ab`](patches/toolchain-v2026-10-23-2ab46ab)
(the commits up to 2ab46ab of scarthgap-dev).

```bash
git clone https://github.com/rcar-community/meta-sparrow-hawk -b v2026-10-23
cd meta-sparrow-hawk
git am <this repo>/patches/toolchain-v2026-10-23-2ab46ab/*.patch
./build.sh --weston --sdk --sbom
```

build.sh checks out poky and meta-openembedded by itself; a later build can
get other commits of them than the ones below.

### Commits

| Layer | Repository | Commit |
| --- | --- | --- |
| meta-openembedded | https://git.openembedded.org/meta-openembedded | 0f00f8b9a21950640da8c5707343e5540133f86e |
| poky | https://git.yoctoproject.org/poky | 104772c5fd0653290cbb5e4b77813343957939cc |
| meta-sparrow-hawk | https://github.com/rcar-community/meta-sparrow-hawk | 2ab46ab97a012958a94965330bd3247d7566fc64 |

### Build machine

| Item | Value |
| --- | --- |
| OS | Ubuntu 24.04.5 LTS (x86_64) |
| CPU | AMD Ryzen 9 8945HX (32 threads) |
| Memory | 32 GB |
