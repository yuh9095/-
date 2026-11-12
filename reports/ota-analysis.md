# OTA image analysis (initial pass)

## Input inventory

The uploaded `860.zip` contains exactly five files:

| Image | Size |
|---|---:|
| `boot.img` | 201,326,592 bytes |
| `vendor_boot.img` | 201,326,592 bytes |
| `dtbo.img` | 25,165,824 bytes |
| `vendor_dlkm.img` | 46,088,192 bytes |
| `system_dlkm.img` | 14,532,608 bytes |

The ZIP itself is 73 MB. This archive is an image subset, not a full OTA package containing every Android partition.

## Header and filesystem observations

| Image | Verified observation |
|---|---|
| `boot.img` | Android boot image magic `ANDROID!`; header version 4 |
| `vendor_boot.img` | Vendor boot magic `VNDRBOOT`; header version 4; page size field is 4096 |
| `dtbo.img` | DT table magic `0xd7b7ab1e`; 12 entries; entry size 32 bytes; entries offset 4096; page size 4096; table header version 0 |
| `vendor_dlkm.img` | EROFS magic `0xe0f5e1e2` at byte offset 1024; block-size bits 12 (4 KiB) |
| `system_dlkm.img` | EROFS magic `0xe0f5e1e2` at byte offset 1024; block-size bits 12 (4 KiB) |

The DTBO table reports a total table size of 6,636,158 bytes, while the partition image file is 25,165,824 bytes. The remaining bytes are partition padding/reserved space, not additional table entries.

## SHA-256

| File | SHA-256 |
|---|---|
| `860.zip` | `f0eef7883a7fecd6682e10270c3343278914051166cf4ddba246d296f945dc5a` |
| `boot.img` | `e7164c25e547f98e0bd4417598a3611aa0680e9ff42417febfbe1dc15c705e9c` |
| `vendor_boot.img` | `b701269ad8cf1b9474da85b2bb6cbebca3118f55489a9c17abd9e3715ecc5e69` |
| `dtbo.img` | `688f27528418e6d5b5c8e38c84ebab3436fa5bb5c432b60e5e583c8ece09ba0d` |
| `vendor_dlkm.img` | `53cde023e4804a5c1a9b829f318c148c43d56de5f757c1449a39764917875f8c` |
| `system_dlkm.img` | `abb161ffe6e8fc1f91cd04571820c7caa7a96c189c2a8512357f67ddfad4945f` |

## What this establishes

- The OTA image set contains boot, vendor boot, DTBO, vendor DLKM and system DLKM partitions.
- Both DLKM images are EROFS filesystems, not raw ext4 images.
- The DTBO image contains 12 table entries.
- The Android 15 identification is supplied by the user; the image subset itself has not yet been independently tied to a specific OTA build fingerprint.

## Still required

1. Extract boot header fields, kernel payload and ramdisk metadata.
2. Extract vendor_boot ramdisk fragments and DTB.
3. Decode all 12 DTBO entries and identify their compatible strings/board IDs.
4. Mount or unpack both EROFS images and inventory every `.ko`.
5. Record module `vermagic`, `depends`, `name`, `srcversion` and hashes.
6. Compare the module inventory with the V-branch module build targets and module lists.
7. Compare DTB/DTBO compatibles and overlays with the device-tree source.
8. Establish OTA build fingerprint/build ID from trustworthy metadata if available.

No claim is made yet that the current source tree reproduces these exact binary images.
