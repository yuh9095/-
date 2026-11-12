# Workflow YAML / CI 流程分析（初查）

## 范围

目标为 OnePlus 12 / SM8650 / Android 15 对应分支：

`oneplus/sm8650_v_15.0.0_oneplus12`

检查的公开源码仓库：

- `yuh9095/android_kernel_common_oneplus_sm8650`
- `yuh9095/android_kernel_oneplus_sm8650`
- `yuh9095/android_kernel_modules_and_devicetree_oneplus_sm8650`

## 结论：当前没有发现 GitHub Actions 工作流 YAML

对三个仓库检查了常见的 `.github/workflows` 路径，均返回 404；GitHub 代码搜索 `workflow`、`*.yml`、`*.yaml` 也没有返回匹配文件。

这只能说明在当前检查的分支和可检索范围内没有发现工作流文件，不能据此断言项目没有任何 YAML 配置，也不能证明官方私有 CI 不存在。

## 可替代的真实构建流程入口

该源码树的主要构建逻辑实际由 shell + Bazel/Kleaf 配置驱动，而不是 GitHub Actions YAML：

1. 主入口：`kernel_platform/oplus/build/oplus_build_kernel.sh`
2. 环境初始化：`kernel_platform/oplus/build/oplus_setup.sh`
3. 总构建封装：`kernel_platform/oplus/build/oplus_build.sh`
4. 模块构建：`kernel_platform/oplus/build/oplus_build_module.sh`
5. DTBO 构建：`kernel_platform/oplus/build/oplus_build_dtbo.sh`
6. 镜像重打包：`kernel_platform/oplus/build/oplus_build_repack_bootimg.sh`
7. 镜像重建：`kernel_platform/oplus/build/oplus_rebuild_img.sh`
8. Bazel/Kleaf 配置：`kernel_platform/build`、各仓库中的 `BUILD.bazel`、`WORKSPACE` 与 build config。

官方 README 的主构建命令为：

```bash
./kernel_platform/oplus/build/oplus_build_kernel.sh pineapple gki
```

## 后续分析方法

由于没有发现可直接复用的 CI YAML，后续将把实际脚本和 Bazel 配置整理成“等价流水线”：

- 输入：manifest 固定的三个源码仓库、工具链和预编译工具版本。
- 环境：平台 pineapple / SM8650、variant gki、构建环境变量。
- 执行：setup → prepare_vendor → Bazel/Kleaf kernel build → module build → DTBO/镜像处理。
- 输出：Image、模块、dtbo.img、boot/vendor_boot 相关镜像及中间产物。
- 校验：产物存在性、模块清单、ABI/KMI、镜像格式与 OTA 中提取的实际文件进行比对。

注意：以上是根据源码入口整理的待验证流程，不代表已经成功执行过完整编译。每个步骤的确切依赖、产物路径和失败条件还需继续从脚本及 Bazel 规则中逐项追踪。
