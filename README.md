# OnePlus 12 (SM8650) Android 15 kernel analysis

This repository is the analysis workspace for the OnePlus 12 Android 15 / ColorOS 15 kernel source and OTA artifacts.

## Scope

- Device platform: Qualcomm SM8650 (pineapple)
- Official manifest: [OnePlusOSS/kernel_manifest](https://github.com/OnePlusOSS/kernel_manifest), branch `oneplus/sm8650`
- Manifest: `oneplus_12_v.xml`
- Kernel branch: `oneplus/sm8650_v_15.0.0_oneplus12`
- OTA input: user-provided `860.zip` (five partition images extracted)

## Analysis rules

1. Treat the official V manifest as the source-of-truth for source revisions and build dependencies.
2. Compare the three yuh9095 source repositories against the corresponding OnePlusOSS repositories.
3. Keep source analysis separate from OTA binary observations.
4. Do not claim a source-to-binary match until config, module, DTB/DTBO and build outputs are actually compared.
5. Never modify upstream source repositories as part of this analysis.

## Current findings

See [reports/initial-findings.md](reports/initial-findings.md) for the first verified results and known gaps.

## Planned reports

- `reports/manifest-analysis.md`: manifest projects, paths, revisions and build dependencies
- `reports/source-comparison.md`: yuh9095 mirrors vs OnePlusOSS
- `reports/ota-analysis.md`: OTA image formats, metadata and module/DTBO extraction
- `reports/build-reproduction.md`: reproducible build environment and validation
- `FINAL-REPORT.md`: consolidated conclusions
