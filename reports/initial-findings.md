# Initial verified findings

Date: 2026-11-12

## Baseline

The user confirmed the supplied OTA is Android 15. The analysis baseline is therefore OnePlus 12 / SM8650 / `pineapple`, official `oneplus_12_v.xml`, and branch `oneplus/sm8650_v_15.0.0_oneplus12`.

## Key result: yuh9095 source mirrors

All three expected V branches exist in the yuh9095 repositories. Six representative files were fetched from the exact official and yuh9095 V branches; all six Git blob SHAs match. The latest commit search result for each official/yuh9095 pair also returned matching SHAs.

Conclusion: the yuh9095 repositories appear to be faithful mirrors of the official Android 15 source for the checked content. Full-tree identity still needs a direct commit/tree comparison.

## Key result: OTA structure

The supplied ZIP contains five partition images. Boot and vendor_boot are header v4; DTBO contains 12 entries; vendor_dlkm and system_dlkm are EROFS with 4 KiB blocks.

## Engineering interpretation

The source architecture is split by the official manifest:
- common GKI kernel at `kernel_platform/common`
- OnePlus/Qualcomm msm-kernel at `kernel_platform/msm-kernel`
- modules, device tree and Oplus build integration at repository root
- pinned CodeLinaro build tools and Bazel dependencies

This means the three source repositories must be analyzed as one manifest-defined workspace, not merged as unrelated kernel trees.

## Current confidence

- Android 15 / V branch selection: confirmed by user and official manifest.
- V branch availability in all three yuh9095 repos: confirmed.
- Representative source file equality: confirmed for six files.
- Whole-repository equality: not yet proven.
- OTA image formats and DTBO count: confirmed.
- Exact module list, DTB/DTBO source mapping and binary reproducibility: pending.
