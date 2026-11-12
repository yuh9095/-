# Source comparison: OnePlusOSS vs yuh9095

## Result

The three yuh9095 repositories contain the Android 15 V branch:

`oneplus/sm8650_v_15.0.0_oneplus12`

That branch exists in all three yuh9095 repositories and in the corresponding official OnePlusOSS repositories.

### Verified file-blob comparisons

The following files were fetched from the exact V branch in both organizations. Git blob SHAs match exactly:

| Repository | File | OnePlusOSS blob SHA | yuh9095 blob SHA | Result |
|---|---|---|---|---|
| common | `Makefile` | `e4c93266110f6f94ed5ac173098a71e74491868b` | same | identical |
| common | `arch/arm64/configs/gki_defconfig` | `6cd2f9fee125c43e7e96b9b7465d4dec17866f0f` | same | identical |
| msm-kernel | `Makefile` | `642bc195f4344779ae91406a598d50277df73a6c` | same | identical |
| msm-kernel | `kernel/sched/walt/Kconfig` | `311db2e556f1befd032ca6fe9c380c765456b638` | same | identical |
| modules/device-tree | `kernel_platform/oplus/build/oplus_build_module.sh` | `0528fae9bbb9d1a802c680497bb5a1ccba2062d1` | same | identical |
| modules/device-tree | `kernel_platform/oplus/build/oplus_setup.sh` | `3178204a580dd9a454293d9e976eba1cfe940560` | same | identical |

The latest commit search result also returned the same SHA for each official/yuh9095 repository pair at the time of this check:

- common: `d4ebeebda66f400ef47524375c42ac61b27e66ba`
- msm-kernel: `e39bf7032e38c547d588372a11a5dd55eb714860`
- modules/device-tree: `38d50357db2728300a61b6f757f2d3a09651c155`

## Interpretation

This is strong evidence that the three yuh9095 V-branch repositories are mirrors of the corresponding official source state for the sampled files, and their reported latest commit SHAs also match.

It is **not yet a full-tree proof**. The next validation should compare the resolved branch commit IDs directly and, if necessary, compare complete Git trees or repository archives. The sample file checks alone cannot prove every file is identical.

## Consequence for the project

Use the yuh9095 repositories as the convenient analysis source, but retain OnePlusOSS links and the official V manifest as the upstream reference. Do not merge or rewrite the three source trees: the manifest already defines how they fit together.
