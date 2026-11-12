#!/usr/bin/env python3
import csv, hashlib, json, os, re, shutil, subprocess
from pathlib import Path

ROOT = Path(os.environ.get("GITHUB_WORKSPACE", ".")).resolve()
OTA = Path(os.environ.get("OTA_EXTRACT", "work/ota")).resolve()
SRC_ROOTS = [ROOT / "source-common", ROOT / "source-msm", ROOT / "source-modules"]
OUT = ROOT / "reports" / "ota-module-audit"
OUT.mkdir(parents=True, exist_ok=True)

def run(args):
    try:
        p = subprocess.run(args, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return p.returncode, p.stdout.strip(), p.stderr.strip()
    except Exception as e:
        return 127, "", str(e)

def norm(s):
    return re.sub(r"[-_]+", "_", s.strip().lower())

def modinfo(path, field):
    rc, out, _ = run(["modinfo", "-F", field, str(path)])
    return out if rc == 0 else ""

def parse_modversions(path):
    rc, out, _ = run(["modprobe", "--dump-modversions", str(path)])
    found = {}
    if rc == 0:
        for line in out.splitlines():
            parts = line.split()
            if len(parts) >= 2:
                found[parts[-1]] = parts[0].lower()
    return found

ota_modules = [p for p in OTA.rglob("*.ko") if p.is_file()]
EXTRACTED_OUT = OUT / "extracted-modules"
EXTRACTED_OUT.mkdir(parents=True, exist_ok=True)
source_ko, source_targets, symvers, source_counts = {}, set(), {}, {}
source_file_candidates = {}

for root in SRC_ROOTS:
    if not root.exists():
        continue
    built = list(root.rglob("*.ko"))
    source_counts[root.name] = len(built)
    for p in built:
        source_ko.setdefault(norm(p.stem), []).append(p)
    for p in root.rglob("modules.order"):
        try:
            for line in p.read_text(errors="ignore").splitlines():
                line = line.strip()
                if line.endswith(".ko"):
                    source_targets.add(norm(Path(line).stem))
        except Exception:
            pass
    for p in root.rglob("Module.symvers"):
        try:
            for line in p.read_text(errors="ignore").splitlines():
                cols = line.split()
                if len(cols) >= 2:
                    symvers[cols[1]] = cols[0].lower()
        except Exception:
            pass

rows = []
for p in sorted(ota_modules):
    name = modinfo(p, "name") or p.stem
    vermagic, depends = modinfo(p, "vermagic"), modinfo(p, "depends")
    signer, srcversion = modinfo(p, "signer"), modinfo(p, "srcversion")
    key = norm(p.stem)
    candidates = source_ko.get(key, [])
    if candidates:
        source_status = "BUILT_KO_FOUND"
    elif key in source_targets:
        source_status = "MODULES_ORDER_TARGET_FOUND"
    else:
        source_status = "NO_BUILT_KO_OR_MODULES_ORDER_ENTRY"
    # Keep the actual OTA binary in the workflow artifact for independent inspection.
    rel = p.relative_to(OTA)
    copied = EXTRACTED_OUT / rel
    copied.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(p, copied)
    digest = hashlib.sha256(p.read_bytes()).hexdigest()
    # Find source files whose basename matches the module stem. This is a clue only:
    # composite modules and generated objects often have different names.
    source_candidates = []
    for root in SRC_ROOTS:
        if root.exists():
            for suffix in (".c", ".S", ".s", ".h"):
                candidate = root / (p.stem + suffix)
                if candidate.is_file():
                    source_candidates.append(str(candidate.relative_to(ROOT)))
            for candidate in root.rglob(p.stem):
                if candidate.is_file():
                    source_candidates.append(str(candidate.relative_to(ROOT)))
    imported = parse_modversions(p)
    missing, mismatch = [], []
    for symbol, crc in imported.items():
        if symbol not in symvers:
            missing.append(symbol)
        elif symvers[symbol] != crc:
            mismatch.append(f"{symbol}: OTA={crc}, source={symvers[symbol]}")
    crc_status = "NO_IMPORT_CRC_DATA"
    if imported:
        crc_status = "CRC_MATCH"
        if missing:
            crc_status = "SOURCE_EXPORT_NOT_FOUND"
        if mismatch:
            crc_status = "CRC_MISMATCH"
    rows.append({
        "partition_path": str(p.relative_to(OTA)), "file": p.name,
        "module_name": name, "vermagic": vermagic, "depends": depends,
        "signer": signer, "srcversion": srcversion,
        "source_status": source_status,
        "source_ko_candidates": ";".join(str(x.relative_to(ROOT)) for x in candidates),
        "source_file_candidates": ";".join(sorted(set(source_candidates))[:50]),
        "extracted_copy": str(copied.relative_to(OUT)),
        "sha256": digest,
        "imported_symbol_count": len(imported), "crc_status": crc_status,
        "missing_source_exports": ";".join(missing),
        "crc_mismatches": ";".join(mismatch),
    })

csv_path = OUT / "module-comparison.csv"
fields = list(rows[0].keys()) if rows else [
    "partition_path","file","module_name","vermagic","depends","signer","srcversion",
    "source_status","source_ko_candidates","source_file_candidates","extracted_copy","sha256","imported_symbol_count","crc_status",
    "missing_source_exports","crc_mismatches"]
with csv_path.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)

status_counts, crc_counts = {}, {}
for row in rows:
    status_counts[row["source_status"]] = status_counts.get(row["source_status"], 0) + 1
    crc_counts[row["crc_status"]] = crc_counts.get(row["crc_status"], 0) + 1

report = [
    "# OTA kernel module vs source audit", "",
    f"- OTA modules extracted: **{len(rows)}**",
    f"- Source built .ko counts: **{json.dumps(source_counts, ensure_ascii=False)}**",
    f"- Module.symvers symbols indexed: **{len(symvers)}**",
    f"- modules.order targets indexed: **{len(source_targets)}**",
    "", "## Source inventory results", ""
]
for k, v in sorted(status_counts.items()):
    report.append(f"- {k}: {v}")
report += ["", "## Symbol CRC results", ""]
for k, v in sorted(crc_counts.items()):
    report.append(f"- {k}: {v}")
report += [
    "", "## Interpretation cautions", "",
    "- NO_BUILT_KO_OR_MODULES_ORDER_ENTRY is a source-inventory warning, not proof that the driver source is absent. A source tree may require configuration and a build to generate modules.order or .ko files.",
    "- source_file_candidates are exact-basename hints only; composite modules and generated modules can have different source filenames.",
    "- Extracted .ko files are included under extracted-modules/ in this workflow artifact.",
    "- CRC comparison is meaningful only when Module.symvers belongs to the exact kernel configuration/build ABI used for the OTA.",
    "- A matching filename does not prove identical module contents. Compare vermagic, imported symbol CRCs, signer and srcversion as well.",
    "- This workflow audits vendor_dlkm and system_dlkm EROFS contents and attempts to unpack vendor_boot ramdisk fragments. If a ramdisk compression format is unsupported, its modules will not appear in the extracted inventory.",
    "", "See module-comparison.csv for per-module details."
]
(OUT / "SUMMARY.md").write_text("\n".join(report) + "\n")
print("\n".join(report))
