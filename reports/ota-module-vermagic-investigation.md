# OTA 模块版本线索与待验证问题

日期：2026-11-12  
输入：`/mnt/data/860.zip` 解包后的 `boot.img`、`vendor_boot.img`、`vendor_ramdisk.bin`、`vendor_dlkm.img`、`system_dlkm.img`

## 目前可确认的内核版本

从 boot.img 的 kernel payload 中读取到：

```
Linux version 6.1.118-android14-11-o-g06ac81e30674
```

与源码配置一致：
- `BRANCH=android14-6.1`
- `KMI_GENERATION=11`
- Linux Makefile 版本为 6.1.118

## vendor ramdisk 中发现的模块字符串线索

对 `vendor_ramdisk.bin` 做原始字节字符串扫描，发现多个形如 `.ko` 的模块文件名，以及重复出现的 vermagic 字符串：

```
6.1.118-android14-11-o-g3019e86a20f2 SMP preempt mod_unload
```

扫描到的不同 vermagic 字符串前缀约 34 种，其中多条是被二进制数据截断或夹杂控制字符的字符串。由于 vendor_ramdisk.bin 是 LZ4 legacy 格式的 ramdisk 数据，且当前环境没有可用的 ramdisk 解包器；尝试按 LZ4 legacy block 方式逐块解压未成功。因此这些字符串目前只能记为**原始镜像中的模块元数据线索**，不能据此声称已提取模块文件或完成 modinfo 验证。

## 必须关注的潜在版本后缀差异

当前出现两个不同的完整 release 后缀：

- boot.img kernel payload：`6.1.118-android14-11-o-g06ac81e30674`
- vendor_ramdisk.bin 原始扫描：`6.1.118-android14-11-o-g3019e86a20f2`

两者共同部分是 `6.1.118-android14-11`，但 build identifier 不同（`g06ac81e30674` vs `g3019e86a20f2`）。

如果第二个字符串确实来自 ramdisk 内实际待加载的 `.ko` 的 ELF .modinfo 段，而不是压缩数据中的偶然字符串或其他残留文件，那么它与当前 boot 内核的完整 UTS_RELEASE 不一致，可能导致模块加载时出现 vermagic 不匹配。**这属于高优先级待验证项，暂时不能直接定性为 OTA 错误。**

## DLKM 镜像现状

- `vendor_dlkm.img` 和 `system_dlkm.img` 均识别为 EROFS，块大小 4096。
- 当前执行环境具备内核 EROFS 文件系统支持，但没有 `/dev/loop*` 设备，且不允许创建 loop block device；因此不能直接 loop-mount。
- 未安装 `fsck.erofs`、`dump.erofs`、`erofsfuse`。所以 DLKM 文件系统中的模块尚未提取。

## 下一步验证顺序

1. 使用可用的 EROFS 工具提取 vendor_dlkm 和 system_dlkm，直接对每个 ELF 模块执行 `modinfo`。
2. 正确解包 vendor_boot ramdisk，确认原始字符串是否来自真实模块 ELF 的 `.modinfo` section。
3. 对每个模块读取 `vermagic`、`depends`、`signer`、`srcversion`，并检查 ELF 的 `__versions` / symbol CRC。
4. 将实际模块 release 与 boot kernel 的完整 UTS_RELEASE 比较；如果后缀不一致，检查是否有强制加载机制、是否为不参与加载的模块，或是否来自不同分区/不同 slot。
5. 对照源码生成的 `Module.symvers`、模块清单、KMI symbol list；不能仅凭相同的 `android14-6.1` 和 generation 认定逐模块兼容。

## 当前结论

已确认 OTA 内核属于 Android 14 GKI 6.1.118 / KMI generation 11。OTA 模块的逐个兼容性尚未完成验证。vendor ramdisk 的原始字符串扫描发现另一个 build identifier，必须先通过真正解包和 ELF modinfo 确认，不能忽略，也不能过早断言它一定会造成加载失败。
