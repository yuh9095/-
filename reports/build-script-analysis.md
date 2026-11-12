# Build script review (Android 15 V branch)

## Entry points

The modules/device-tree repository provides these scripts under `kernel_platform/oplus/build/`:
- `oplus_build_kernel.sh`: sources `oplus_setup.sh`, initializes the environment, then invokes `kernel_platform/build/android/prepare_vendor.sh` for the selected platform/variant.
- `oplus_build_dtbo.sh`: invokes the same prepare script with `RECOMPILE_KERNEL=0`, `COPY_NEEDED=0`, and `RECOMPILE_EXT_MODULE=0`; intended to rebuild DTBO without rebuilding the kernel and external modules.
- `oplus_build_module.sh`: builds an in-tree `.ko` target or an out-of-tree module directory via Bazel.

## Variant behavior

The setup script maps `pineapple` to SM8650; `gki` / `user` to GKI; and `consolidate` / `userdebug` to consolidate.

The manifest README documents:
```bash
./kernel_platform/oplus/build/oplus_build_kernel.sh pineapple gki
```

## Module build behavior

The module script distinguishes:
1. In-tree module: pass a path ending in `.ko`, e.g. `drivers/power/oplus/v2/oplus_chg_v2.ko`; it queries/builds a Bazel target under `//msm-kernel:${platform}_${variant}/...`.
2. Out-of-tree module: pass a module directory, e.g. `vendor/oplus/kernel/boot/oplus_phoenix`; it queries a matching `*_dist` target and runs it with the Qualcomm GKI KMI symbol list.

Therefore module analysis must include both `kernel_platform/msm-kernel` and out-of-tree vendor module directories.

## Build blockers / suspicious details

### 1. vendor setup script dependency

`oplus_setup.sh` executes `source vendor/oplus/kernel/prebuilt/vendorsetup.sh`. That exact path was not found in the public yuh9095 modules/device-tree repository during this check. A public OnePlus kernel issue also records a build failure with this same missing path. This may be an omitted proprietary/prebuilt input or packaging issue; it must be resolved before claiming a clean build can start.

Reference: [OnePlusOSS/android_kernel_common_oneplus_sm8650 issue #3](https://github.com/OnePlusOSS/android_kernel_common_oneplus_sm8650/issues/3).

### 2. Android 14 path literal in an Android 15 branch

The out-of-tree module path in `oplus_build_module.sh` contains `kernel_platform/out/android14-6.1/msm-kernel/../../${ko_path}`.

This is suspicious in the Android 15 V branch. It may be a stale output-directory literal or may still be compatible with the actual Bazel output layout. Do not edit it blindly: inspect the generated output tree and Bazel target metadata, then test one out-of-tree module.

### 3. Empty local module-add lists

The tracked files `kernel_platform/oplus/prebuild/local_add_vendor_boot.txt` and `kernel_platform/oplus/prebuild/local_add_vendor_dlkm.txt` are empty in the V branch. These are local-addition lists, not a complete inventory of shipped modules. Their emptiness does not mean the OTA has no modules.

## Next validation

1. Resolve the `vendorsetup.sh` dependency and determine whether it is intentionally external.
2. Inspect actual Bazel output paths for GKI and out-of-tree module targets.
3. Extract OTA module lists from EROFS and compare them with Bazel targets and install lists.
4. Verify which modules are placed in vendor_boot, vendor_dlkm and system_dlkm.
5. Only then attempt a full GKI build and DTBO-only build.