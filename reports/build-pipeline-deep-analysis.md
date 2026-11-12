# SM8650 构建流水线：脚本级追踪与风险

分析分支：`oneplus/sm8650_v_15.0.0_oneplus12`

目标：OnePlus 12 / pineapple / SM8650 / Android 15。

## 1. 实际入口与调用关系

主入口 `kernel_platform/oplus/build/oplus_build_kernel.sh`：

1. source `kernel_platform/oplus/build/oplus_setup.sh $1 $2`
2. 调用 `init_build_environment`
3. 调用 `kernel_platform/build/android/prepare_vendor.sh pineapple gki`（以用户命令参数为准）
4. 将输出同时写到 `LOGDIR/build_时间戳.log`

`oplus_setup.sh` 设置了关键 Android/KP 环境变量：

- `TOPDIR`、`ANDROID_BUILD_TOP`
- `OPLUS_VND_BUILD_PLATFORM=SM8650`
- `ANDROID_PRODUCT_OUT=out/target/product/pineapple`
- `TARGET_BOARD_PLATFORM=pineapple`
- `EXTRA_KBUILD_ARGS=--skip abl`
- 工具路径：python3、mkbootimg、unpack_bootimg、lz4、cpio、simg2img、mkfs.erofs、build_image、mkdtimg、mkbootfs、avbtool、llvm-strip

它还会 source：

`vendor/oplus/kernel/prebuilt/vendorsetup.sh`

这个文件在当前公开 modules 仓库对应分支中未找到，属于构建前置条件/依赖完整性风险。需要从完整 Android vendor tree 或厂商预编译包确认其来源。

## 2. prepare_vendor.sh 的核心步骤

脚本本身启用 `set -e`，关键执行顺序：

1. 计算 Kernel Platform 根目录。
2. 检查并创建 `ANDROID_KERNEL_OUT`。
3. 解析 target/variant；将 `consolidate` 映射为 `gki`。
4. 将 `LTO` 转成 Kleaf 参数（例如 `--lto=thin`）。
5. 调用 `build/brunch pineapple gki` 建立构建配置。
6. 确定输出目录，默认 `out/msm-kernel-pineapple-gki`。
7. 必要时调用 `build_with_bazel.py` 执行 Bazel/Kleaf 编译。
8. 将 dist 中的 Image、vmlinux、System.map、.config、Module.symvers、UAPI headers、build_opts 等复制到 `device/qcom/pineapple-kernel`。
9. 整理 first-stage modules、vendor_dlkm modules、system_dlkm staging archive。
10. 编译 Android vendor 下的外置模块及 vendor devicetree（如环境中存在对应目录）。
11. 合并 kernel DTB/DTBO 与 vendor devicetree overlays。
12. 将 KP 输出同步到 Android tree 的 out 目录。

特别注意：`prepare_vendor.sh` 的注释明确说明它假设已在 Android build 环境中执行；当 `ANDROID_KERNEL_OUT` 未设置时，至少要求 `ANDROID_BUILD_TOP` 和 `TARGET_BOARD_PLATFORM`。因此这不是一个脱离完整 Android/vendor tree 即可直接运行的纯内核编译入口。

## 3. 发现的高优先级问题

### P1：主入口可能吞掉真实编译失败状态

`oplus_build_kernel.sh` 使用：

```bash
./kernel_platform/build/android/prepare_vendor.sh ... 2>&1 | tee LOGDIR/build_....log
```

但脚本没有启用 `set -o pipefail`。在 Bash 默认管道语义下，整个 pipeline 的退出码取最后一个命令 `tee` 的退出码，而不是前面的 `prepare_vendor.sh`。

后果：编译脚本失败、但 tee 成功写日志时，外层脚本可能仍继续执行 `build_end_time` 并以成功状态结束。CI workflow 如果只检查外层进程退出码，可能产生假绿灯。

建议修复：

```bash
set -o pipefail
```

并让调用链保留失败码；如果要保证任何命令失败立即退出，再评估启用 `set -euo pipefail` 的兼容性。

### P1：公开源码不包含 vendorsetup.sh

`oplus_setup.sh` 无条件 source `vendor/oplus/kernel/prebuilt/vendorsetup.sh`。当前公开 modules 分支没有发现该路径。缺少文件时环境初始化不能按预期完成。

建议在 workflow preflight 阶段明确检查该文件，并将其列为外部 Android/vendor 依赖；不要简单创建空文件冒充依赖满足，因为其中可能定义必要变量或函数。

### P2：模块 OOT 构建路径仍出现 Android 14 目录名

`oplus_build_module.sh` 的 out-of-tree Bazel run 使用：

```bash
--dist_dir=${TOPDIR}/kernel_platform/out/android14-6.1/msm-kernel/../../${ko_path}
```

该路径字面上带有 `android14-6.1`，与本次 Android 15 目标存在版本命名不一致。是否实际导致错误，取决于 Bazel target 的输出布局和路径归一化结果；目前应标记为待验证，而不是直接断言构建必然失败。

建议改为从实际 `DIST_INSTALL` / Bazel 输出变量推导，避免硬编码旧目录名，并检查最终输出目录是否存在、是否包含预期 KO。

### P2：构建脚本的环境依赖很重

`prepare_vendor.sh` 后续还会进入 Android tree 的模块构建、vendor devicetree 编译和 DT 合并逻辑。单纯 checkout 三个 kernel 仓库不足以构成完整可复现环境。需要 manifest 固定的依赖、Android device/vendor tree、预编译工具和必要的 build metadata。

## 4. 建议的 CI YAML 阶段设计（分析草案）

以下是适合后续实现的阶段划分；不是已经在仓库运行通过的 workflow：

- `preflight`：检查 manifest revision、必需目录、vendorsetup.sh、工具链文件、磁盘空间。
- `environment`：准备 Android build tree，设置 pineapple / user / gki 参数。
- `kernel`：运行 `oplus_build_kernel.sh pineapple gki`，保存完整日志并强制传播 pipeline 失败码。
- `modules`：检查 dist 中模块清单与 modules.load / vendor_dlkm.modules.load / system_dlkm.modules.load 一致。
- `dt`：验证 dtb、dtbo 和 overlay merge 产物。
- `images`：在具备合法原始镜像、image-info 和签名材料时重建 boot/vendor_boot/dtbo/vendor_dlkm/system_dlkm。
- `validation`：对镜像格式、AVB footer、模块清单、ABI/KMI 和 OTA 原始镜像做差异比较。
- `artifacts`：上传日志、`out/msm-kernel-pineapple-gki/dist` 和必要报告。

安全要求：不要把生产 AVB 私钥、内部签名服务凭据或 vendor 私有文件写入公开 workflow 日志或公开 artifacts。测试密钥只能用于明确的测试环境，不能替代设备正式签名链。

## 5. 当前状态

- 已完成：脚本调用关系和关键环境变量静态追踪。
- 已发现：pipeline 退出码可能被 tee 掩盖；vendorsetup.sh 是未在公开源码中找到的外部依赖；OOT module 路径有 Android 14 命名残留。
- 未完成：实际执行完整 Android build；验证 Bazel dist 真实产物路径；从 OTA 解包模块并逐项核对；确认正式 AVB 配置与签名链。

