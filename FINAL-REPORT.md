# OnePlus 12 Android 15 kernel analysis — status

This is an active investigation, not a final binary-reproducibility certification.

## Confirmed

1. The selected official baseline is `OnePlusOSS/kernel_manifest` branch `oneplus/sm8650`, manifest `oneplus_12_v.xml`.
2. All three source projects use `oneplus/sm8650_v_15.0.0_oneplus12`.
3. The corresponding V branches exist in the three yuh9095 source repositories.
4. Six representative source files have identical Git blob SHAs between OnePlusOSS and yuh9095.
5. The uploaded OTA ZIP contains boot, vendor_boot, dtbo, vendor_dlkm and system_dlkm images.
6. boot/vendor_boot are header v4; DTBO has 12 entries; both DLKM images are EROFS.

## Not yet confirmed

- Complete Git tree equality of all three mirror pairs.
- Exact OTA build fingerprint and kernel release string.
- Full boot/vendor_boot extraction.
- Complete DTB/DTBO overlay-to-source mapping.
- Full `.ko` inventory, module dependency graph and vermagic.
- Successful build from the pinned manifest.
- Byte-for-byte or semantically equivalent reproduction of the OTA images.

## Next work

Continue with full source commit/tree verification, then decode OTA ramdisks, DTBO entries and EROFS module files. Only after that should the build be attempted and compared with the OTA.
