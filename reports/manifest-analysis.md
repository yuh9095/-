# Android 15 manifest analysis

## Selected manifest

- Repository: [OnePlusOSS/kernel_manifest](https://github.com/OnePlusOSS/kernel_manifest)
- Manifest branch: `oneplus/sm8650`
- Manifest file: [oneplus_12_v.xml](https://github.com/OnePlusOSS/kernel_manifest/blob/oneplus/sm8650/oneplus_12_v.xml)
- Device/platform: OnePlus 12 / SM8650 / `pineapple`
- Three device source projects all use revision `oneplus/sm8650_v_15.0.0_oneplus12`.

## Main source projects

| Project | Manifest checkout path | Revision |
|---|---|---|
| `android_kernel_common_oneplus_sm8650` | `kernel_platform/common` | `oneplus/sm8650_v_15.0.0_oneplus12` |
| `android_kernel_oneplus_sm8650` | `kernel_platform/msm-kernel` | `oneplus/sm8650_v_15.0.0_oneplus12` |
| `android_kernel_modules_and_devicetree_oneplus_sm8650` | repository root (`./`) | `oneplus/sm8650_v_15.0.0_oneplus12` |

The modules/device-tree project being checked out at the root is important: it supplies the `kernel_platform/oplus` build integration and the platform device-tree/module content. The two kernel projects are nested under `kernel_platform/`.

## Pinned external build dependencies

The V manifest also pins external CodeLinaro projects. These are not optional if the goal is to reproduce the official build environment.

| Project | Checkout path | Pinned revision |
|---|---|---|
| `kernel/prebuilts/build-tools` | `kernel_platform/prebuilts/kernel-build-tools` | `d153b7ab4a4956198957e258d4f370e875c53059` |
| `kernel_platform/build/bazel_common_rules` | `kernel_platform/build/bazel_common_rules` | `415b543d5e1d270a22f8c6ae9d848b3560472062` |
| `kernel_platform/external/bazel-skylib` | `kernel_platform/external/bazel-skylib` | `7fdbc462f5001b7e82f026aa90bd43c494e2a8d8` |
| `kernel_platform/external/dtc` | `kernel_platform/external/dtc` | `3a8c1bbce993f9143835c7f40eeefcdf948cfaf5` |
| `kernel_platform/external/python/absl-py` | `kernel_platform/external/python/absl-py` | `e46584edbb247bf79c74c4f105b6fff18234cee8` |
| `kernel_platform/external/stardoc` | `kernel_platform/external/stardoc` | `0d74fed6f8d0844f696771e71bc0b071cae99021` |
| `kernel_platform/prebuilts/bazel/linux-x86_64` | `kernel_platform/prebuilts/bazel/linux-x86_64` | `eee09422f02e60f28192bcb5a8ce8660baba6706` |
| `kernel_platform/prebuilts/build-tools` | `kernel_platform/prebuilts/build-tools` | `cad7e11de82b3307000e09c9d539b2700bd17aea` |
| `kernel_platform/prebuilts/clang-tools` | `kernel_platform/prebuilts/clang-tools` | `0613fc5443d035335a9541994607bacae03750f2` |
| `kernel_platform/prebuilts/jdk/jdk11` | `kernel_platform/prebuilts/jdk/jdk11` | `ced68c9308cbc1b6ec3e602dba8d0d56df8b6d73` |
| `kernel_platform/system/tools/mkbootimg` | `kernel_platform/tools/mkbootimg` | `b17f184a20744a7e0a421f901bdf20a23be22b07` |
| `kernel_platform/toolchain/prebuilts/ndk/r23` | `kernel_platform/prebuilts/ndk-r23` | `269a5dc9e862f78dc2030d9262f73cb2642b8127` |
| `kernelplatform/prebuilts-master/clang/host/linux-x86` | `kernel_platform/prebuilts/clang/host/linux-x86` | `28b975ada54f8610ed531a6b57253aed10e7c87d` |
| `kernelplatform/prebuilts/gcc/linux-x86/host/x86_64-linux-glibc2.17-4.8` | `kernel_platform/prebuilts/gcc/linux-x86/host/x86_64-linux-glibc2.17-4.8` | `dd099b5d68822602228e2af66693e61e7b54e0a9` |

## Manifest linkfiles

The manifest creates integration files:
- common kernel root is linked to `kernel_platform/.source_date_epoch_dir`
- msm-kernel `bazel.WORKSPACE` is linked to `kernel_platform/WORKSPACE`
- msm-kernel `build_with_bazel.py` is linked to `kernel_platform/build_with_bazel.py`
- selected build-tools and GCC sysroot directories are linked into `kernel_platform/build/`.

These linkfiles are part of the source layout and should be preserved during a manual checkout.

## Build entry point

The manifest README documents:

```bash
./kernel_platform/oplus/build/oplus_build_kernel.sh pineapple gki
```

This identifies the official GKI build entry point, but a successful build has not yet been run in this analysis environment.

## Important caveats

- The manifest's `default` remote points to CodeLinaro and has `dummy_revision`; the three OnePlus projects override it with explicit branch revisions.
- A branch name is not a permanent source snapshot. For reproducibility, record each resolved commit SHA using `repo manifest -r`.
- Do not omit CodeLinaro dependencies when comparing build outputs; otherwise a mismatch may be caused by toolchain/build-rule drift rather than kernel source changes.
