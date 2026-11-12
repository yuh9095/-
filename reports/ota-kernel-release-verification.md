# OTA 内核 Release 实测结果

日期：2026-11-12  
输入：用户提供的 `860.zip`，解包得到 `boot.img`  
设备分析基准：OnePlus 12 / SM8650 / pineapple

## 结论

从 OTA 的 boot image 内核 payload 中直接搜索并读取到 Linux 内核版本字符串：

```
Linux version 6.1.118-android14-11-o-g06ac81e30674
```

这是 OTA 二进制中的实际字符串，不是根据源码配置推测。

## 与源码对照

| 项目 | OTA boot.img | 内核源码配置 |
|---|---|---|
| Linux 主版本 | 6.1.118 | Makefile: VERSION=6, PATCHLEVEL=1, SUBLEVEL=118 |
| GKI 分支 | android14-6.1 | build.config.constants: BRANCH=android14-6.1 |
| KMI generation | 11 | build.config.common: KMI_GENERATION=11 |
| build identifier | g06ac81e30674 | 源码分支配置负责生成 release 后缀，需继续追溯对应提交 |

**源码配置与 OTA 内核 Release 的前三项完全吻合。** 因此可确认该 OTA 的实际内核是 Android 14 GKI 6.1.118 / KMI generation 11，而系统平台可以是 Android 15。

## boot.img 解析记录

- 文件：`boot.img`
- Android boot magic：`ANDROID!`
- Header version：4
- Kernel payload size：35,826,176 bytes
- Kernel payload offset：4096 bytes
- Kernel payload 开头：`MZ`（ARM64 Image 的 PE/EFI 头部标识）
- 从 kernel payload 中检索到 `Linux version 6.1.118-android14-11-o-g06ac81e30674`

## DLKM 文件系统初步检查

OTA 中同时包含：
- `vendor_dlkm.img`：46,088,192 bytes
- `system_dlkm.img`：14,532,608 bytes

两者在偏移 1024 处均识别到 EROFS magic `0xe0f5e1e2`，块大小 4096 bytes。按 EROFS superblock 字段读取：
- vendor_dlkm：root NID 39，inode count 420，blocks 11021
- system_dlkm：root NID 38，inode count 185，blocks 3460

当前运行环境没有 `fsck.erofs` / `dump.erofs` / `erofsfuse`，因此还没有解出文件系统内部的模块文件。不能在缺少提取结果时声称已验证每个模块的 vermagic 或符号 CRC。

## 下一步

1. 获取可用 EROFS 解包工具或使用可靠解析器提取两套 DLKM 文件系统。
2. 收集所有 `.ko` 的 `modinfo`（尤其 vermagic、depends、name、signer）和 ELF section/symbol version。
3. 与源码构建生成的 `Module.symvers`、模块列表、KMI symbol list 和上述 OTA Release 交叉核对。
4. 追溯 build identifier `g06ac81e30674` 对应的源码提交，确认 OTA 与仓库分支的精确提交关系。
