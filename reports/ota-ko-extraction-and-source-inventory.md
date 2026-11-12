# OTA .ko 全量提取与源码清单核对：准备阶段

日期：2026-11-12  
源码分支：oneplus/sm8650_v_15.0.0_oneplus12  
模块仓库：yuh9095/android_kernel_modules_and_devicetree_oneplus_sm8650

## 本轮限制

当前数据分析功能暂不可用，因此本轮没有对用户上传的 860.zip 执行解包，也没有生成任何从 OTA 提取出来的 .ko 文件。本文记录的是通过 GitHub 源码树确认的提取方法和源码侧比对基线，不代表 OTA 模块已提取。

## 源码仓库中已找到的工具

源码树包含：
- kernel_platform/oplus/tools/erofsfuse：预置 EROFS FUSE 可执行文件。
- kernel_platform/oplus/tools/erofs_unpack.sh：通过 erofsfuse 挂载 EROFS，再复制目录内容。
- kernel_platform/oplus/tools/oplus_get_ko_list.sh：内部提取脚本样例，覆盖 vendor_boot ramdisk 和 vendor_dlkm 两类模块。

oplus_get_ko_list.sh 的流程：
1. 用 unpack_bootimg 拆 vendor_boot。
2. 用 LZ4 解压 vendor ramdisk。
3. 用 cpio 提取 ramdisk 文件。
4. 复制 lib/modules/*.ko。
5. 将 vendor_dlkm sparse image 转换为 raw image。
6. 调用 erofs_unpack.sh 解包 vendor_dlkm。
7. 复制 lib/modules/*.ko。

该脚本的镜像下载 URL 被写成 xxx 占位符，不能直接运行完整下载流程；但其对本地镜像的解包路径具有参考价值。

## 源码侧模块清单

### Qualcomm 基础模块名清单

kernel_platform/oplus/tools/qcom_base_ko.txt：
- Git blob SHA：98c05c86d63cb323896c0c6bdbd5a50f0f2d07b8
- 约 400 个模块名（文件 401 行，末尾包含换行）。
- 列出 Qualcomm 基础模块名称，例如 adsp_loader_dlkm.ko、camcc-pineapple.ko、cnss2.ko、msm_kgsl.ko、qcom_glink.ko、sched-walt.ko、wlan_firmware_service.ko 等。

注意：这是基线模块名清单，不等同于当前 pineapple GKI 构建的最终安装清单；其中可能包含通用、可选、测试或其他配置模块。

### Oplus 外置模块构建目录

kernel_platform/oplus/config/modules.ext.oplus：
- Git blob SHA：e803f552806f5d7c9bb8c0f2bde7b5d0c5b792ac
- 24 个外置模块构建目录（文件 25 行，末尾空行）。
- 涵盖 Oplus phoenix、DFR、三段键、触控、secure common、rootguard、network、Wi-Fi、sensor、hans、game_opt、freqqos、thermal、IPC、radio、MM、synchronize、midas、stability helper、pogo keyboard、power hook 等目录。

modules.vendor_boot.list.oplus：
- Git blob SHA：cbf2796e47c3b7db3c8e3e3134ef217a844f86ec
- 当前仅列出 oplus_mdmfeature.ko。

modules.list.oplus 与 local_add_vendor_dlkm.txt 在该分支为空文件；不能将空文件解释为设备没有模块。

## 构建逻辑核对

oplus_build_module.sh：
- Git blob SHA：0528fae9bbb9d1a802c680497bb5a1ccba2062d1
- 区分 in-tree .ko 和 OOT 模块目录。
- OOT Bazel build 使用 Qualcomm GKI ABI symbol list。

oplus_modules_define.bzl：
- Git blob SHA：55a3b826dd6905b5267e27db295a59a3abfcadc9
- 使用 ddk_module 构建模块，默认输出名称为 <name>.ko，并支持条件编译。

## 一个需要进一步解释的配置差异

kernel_platform/oplus/tools/vendor_dlkm_image_info.txt 当前写着 vendor_dlkm_fs_type=ext4。

但同一源码树的 oplus_get_ko_list.sh 将 vendor_dlkm 作为 EROFS 路径处理，调用 erofs_unpack.sh；用户 OTA 的 vendor_dlkm 镜像此前也被识别为 EROFS。该文件可能是通用/旧构建配置，必须结合实际构建产物和脚本调用分支核对，不能只按单个 image_info 文件断言。

system_dlkm_image_info.txt 明确写有 system_dlkm_fs_type=erofs 和 erofs_default_compressor=lz4hc,9，并且其中 fingerprint 属性是 Android 14 的 pineapple 构建信息。这是构建配置证据，不是 OTA 镜像内容本身。

## 真正完成 OTA 缺模块比对所需的后续操作

待数据分析恢复后，对 860.zip 做以下全量操作：
1. 解开 vendor_dlkm.img、system_dlkm.img 的 EROFS 文件系统。
2. 解开 vendor_boot.img 的 vendor ramdisk（LZ4 + cpio）。
3. 递归提取所有 .ko，保留原始路径，生成文件名清单和 SHA-256。
4. 从每个 ELF 模块提取 .modinfo：vermagic、depends、name、srcversion、signer。
5. 搜索三个源码仓库中的所有模块构建定义、out 清单、modules.order、modules.load、Bazel targets 和 Module.symvers。
6. 生成差异表：OTA 有源码无、源码有 OTA 无、同名不同 SHA、vermagic 不一致、depends 缺失、模块符号 CRC / KMI 不匹配。
7. 区分源码缺失与源码存在但本次构建未启用/未安装，不能只按 .ko 文件名作结论。

## 当前结论

已从源码仓库找到可用的 EROFS 提取工具和内部模块提取脚本路径，也找到约 400 个 Qualcomm 基础模块名清单及 Oplus 外置模块构建目录。OTA 的 .ko 尚未实际提取，源码缺失项尚未判定。
