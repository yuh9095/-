# OnePlus 12 GKI / KMI 基准核验（Android 15 系统）

核验分支：`oneplus/sm8650_v_15.0.0_oneplus12`  
设备平台：OnePlus 12 / SM8650 / pineapple（构建配置内部架构名为 kalama）  
核验日期：2026-11-12

## 结论

这套 OnePlus 12 内核源码的 GKI 基准**明确是 Android 14 的 `android14-6.1`，不是 Android 15 的 `android15-6.6`**。因此 Android 15 系统继续使用这套 Android 14 GKI/KMI 基线，是符合 Google GKI 兼容模型的；不能因为系统是 Android 15 就把内核或模块迁移到 Android 15 分支。

## 直接源码证据

仓库：`yuh9095/android_kernel_oneplus_sm8650`  
分支：`oneplus/sm8650_v_15.0.0_oneplus12`

| 文件 | 关键内容 | 证据 |
|---|---|---|
| `build.config.constants` | `BRANCH=android14-6.1` | blob `fa2b8497f4480bfb642f18eac858e4afee158709` |
| `build.config.common` | `KMI_GENERATION=11` | blob `f9becf2d72d8b7a18fc1685fb154491754e365b3` |
| `Makefile` | `VERSION=6`, `PATCHLEVEL=1`, `SUBLEVEL=118` | blob `642bc195f4344779ae91406a598d50277df73a6c` |
| `build.config.msm.kalama` | 继承 msm GKI 配置，定义 `VARIANTS=(consolidate gki)` | blob `356cb96322c92ff3ea0f3ef31ca1697207f5152c` |
| `build.config.msm.gki` | `KMI_ENFORCED=1`、`GKI_KMI_SYMBOL_LIST=../msm-kernel/android/abi_gki_aarch64_qcom` | blob `f989f00385feaf87a1b29b1751d06ec6472495b9` |
| `arch/arm64/configs/gki_defconfig` | `CONFIG_MODULES=y`、`CONFIG_MODVERSIONS=y`、`CONFIG_MODULE_SIG=y` | blob `08bd7f457beb995b1a3495f16cd09ca7b768f56c` |

### 对版本的解释

- GKI KMI 分支：`android14-6.1`。
- Linux 基础版本：`6.1.118`。
- KMI generation：`11`。
- 因此构建输出的 release 应由该分支、generation 和源码版本共同生成；在没有实际 OTA 内核字符串或构建产物前，不把推测的完整 `uname -r` 字符串当作已验证事实。
- `kalama` 是 Qualcomm 平台配置内部使用的架构名；设备产品目标仍由 OnePlus 构建脚本传入 `pineapple`。不能把 kalama 误判为另一台设备。

## Android 15 兼容性

Google AOSP 官方文档明确说明：Android 15 设备可以安全使用 Android 14 开发的 `android14-6.1` GKI 内核。GKI 在受支持的平台版本之间保持兼容；但不同 GKI KMI 分支之间不保证 KMI 兼容。例如 `android14-6.1` 不能直接替换成 `android15-6.6` 而不重建模块。

官方资料：
- https://source.android.com/docs/core/architecture/kernel/android-common
- https://source.android.com/docs/core/architecture/kernel/gki-android14-6_1-release-builds

因此本项目的正确版本判断应为：

| 层级 | 本次确认结果 |
|---|---|
| Android 系统 | Android 15（用户提供的系统基准） |
| GKI/KMI 分支 | `android14-6.1` |
| Linux 主版本 | `6.1.118` |
| KMI generation | `11` |
| 厂商模块 | 必须匹配这套内核实际导出的 KMI / symbol CRC / vermagic；不能仅凭“Android 14 模块”标签判定兼容 |

## 模块构建机制的源码证据

模块构建脚本 `kernel_platform/oplus/build/oplus_build_module.sh` 中，OOT 模块 Bazel 调用明确指定：

- `--user_kmi_symbol_lists=//msm-kernel:android/abi_gki_aarch64_qcom`
- `--//msm-kernel:skip_abi=true`
- 输出目录参数里硬编码了 `kernel_platform/out/android14-6.1/msm-kernel/../../${ko_path}`

该路径字符串与源码实际的 `BRANCH=android14-6.1` 一致，说明 Android 14 GKI 基线不是单纯从分支名猜测，而是被模块构建脚本实际引用。

此外，`build.config.msm.gki` 将 `KMI_ENFORCED=1` 和 Qualcomm KMI symbol list 纳入 GKI 构建流程；`gki_defconfig` 启用了模块版本校验和模块签名配置。这些是后续检查模块兼容性的关键基础。

## OTA 侧尚待完成的验证

已确认用户提供 OTA 中有 `boot.img`、`vendor_boot.img`、`vendor_dlkm.img`、`system_dlkm.img`。目前镜像容器格式已识别，但还没有成功提取 EROFS 内部所有 `.ko` 并读取每个模块的 `vermagic`、modversions CRC 和签名信息。

因此，当前结论分两层：

1. **源码基线已确认：** Android 14 / 6.1 / KMI generation 11。
2. **OTA 二进制模块逐个匹配：** 尚未完成，不能声称每个模块已经验证通过。

下一步必须从 OTA 中提取实际模块，并与本分支生成的 `Module.symvers`、`modules.order`、KMI symbol list 和 kernel release 逐项比对。还需要从 OTA 的 boot image kernel payload 中提取真实内核 release，最终闭环。

## 重要提醒

不能把 `KMI_GENERATION=11` 当成跨所有分支通用的版本号。它只在本分支对应的 KMI 基线上有意义。若更换 GKI 分支或 generation，必须重新检查并同步重建受影响的厂商模块。
