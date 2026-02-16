#!/usr/bin/env python3
"""
Upsert a single node row in data-pipeline/nodes.csv from config.yaml.

Default behavior is streaming update (does not load all existing nodes into memory).
Set READ_ALL_NODES: true in config.yaml to use in-memory mode.
"""

from __future__ import annotations

import ast
import csv
import json
import re
import shutil
import sys
import traceback
from pathlib import Path
from typing import Dict, List, Set, Tuple

try:
    import yaml
except ImportError as exc:
    raise SystemExit("Missing dependency: pyyaml. Install with: pip install pyyaml") from exc


SCRIPT_DIR = Path(__file__).resolve().parent
WEBROOT_DIR = SCRIPT_DIR.parents[2]
DEFAULT_CONFIG_PATH = SCRIPT_DIR / "config.yaml"

IMPORT_TO_PIP = {
    "yaml": "pyyaml",
    "dotenv": "python-dotenv",
    "PIL": "pillow",
    "cv2": "opencv-python",
    "sklearn": "scikit-learn",
}

CONTROL_KEYS = {
    "NODE_ID",
    "ORIGINAL_NODE_ID",
    "NODES_CSV",
    "SOURCE_PYTHON",
    "MANUAL_ROW_UPDATE",
    "READ_ALL_NODES",
    "READ_ALL_EXISTING_NODES",
    "INCLUDE_LOCAL_MODULES",
    "INCLUDE_LOCAL_MODULES_IN_DEPENDENCIES",
}

FIELD_KEY_ALIASES = {
    "TIME_EST": "processing_time_est",
    "PROCESSING_TIME_EST": "processing_time_est",
    "RUN_PROCESS": "run_process_available",
    "RUN_PROCESS_AVAILABLE": "run_process_available",
}


def cfg_get(config: Dict, key: str, default=None):
    if key in config:
        return config[key]
    lower = key.lower()
    upper = key.upper()
    if lower in config:
        return config[lower]
    if upper in config:
        return config[upper]
    return default


def normalize_key(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "_", value or "").strip("_").lower()


def load_config(config_path: Path) -> Dict:
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")
    with config_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError("config.yaml must contain a YAML mapping/object")
    return data


def parse_cli_value(value: str):
    lower = value.lower()
    if lower in {"true", "yes"}:
        return True
    if lower in {"false", "no"}:
        return False
    if re.fullmatch(r"-?\d+", value):
        try:
            return int(value)
        except ValueError:
            return value
    return value


def parse_cli_overrides(argv: List[str]) -> Tuple[Path, Dict]:
    config_path = DEFAULT_CONFIG_PATH
    unknown = list(argv)
    if unknown and not unknown[0].startswith("--"):
        config_path = resolve_path(unknown[0], Path.cwd())
        unknown = unknown[1:]

    overrides: Dict[str, object] = {}
    i = 0
    while i < len(unknown):
        token = unknown[i]
        if not token.startswith("--"):
            i += 1
            continue
        key = token[2:].replace("-", "_").upper()
        if i + 1 < len(unknown) and not unknown[i + 1].startswith("--"):
            overrides[key] = parse_cli_value(unknown[i + 1])
            i += 2
        else:
            overrides[key] = True
            i += 1

    return config_path, overrides


def resolve_path(path_value: str, base_dir: Path) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    primary = (base_dir / path).resolve()
    if primary.exists():
        return primary
    # Allow repo-root relative paths passed from admin UI, e.g. airports/pipeline/pull-airports.py
    fallback = (WEBROOT_DIR / path).resolve()
    return fallback if fallback.exists() else primary


def stdlib_modules() -> Set[str]:
    if hasattr(sys, "stdlib_module_names"):
        return set(sys.stdlib_module_names)
    return {
        "argparse", "ast", "collections", "csv", "datetime", "functools", "hashlib",
        "itertools", "json", "logging", "math", "os", "pathlib", "random", "re",
        "shutil", "statistics", "subprocess", "sys", "tempfile", "threading", "time",
        "typing", "urllib", "uuid",
    }


def discover_imports(source_path: Path) -> Set[str]:
    source_text = source_path.read_text(encoding="utf-8")
    tree = ast.parse(source_text)

    modules: Set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                modules.add(node.module.split(".")[0])
    return modules


def discover_cli_flags(source_path: Path) -> List[str]:
    source_text = source_path.read_text(encoding="utf-8")
    tree = ast.parse(source_text)

    flags: List[str] = []
    seen = set()

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not isinstance(node.func, ast.Attribute) or node.func.attr != "add_argument":
            continue

        for arg in node.args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str) and arg.value.startswith("--"):
                flag = arg.value[2:].replace("-", "_")
                if flag not in seen:
                    flags.append(flag)
                    seen.add(flag)
                break
    return flags


def discover_dependencies(source_path: Path, include_local_modules: bool = False) -> List[str]:
    imports = discover_imports(source_path)
    stdlib = stdlib_modules()

    deps: Set[str] = set()
    for module in imports:
        if module in stdlib:
            continue

        local_module_file = source_path.parent / f"{module}.py"
        if local_module_file.exists() and not include_local_modules:
            continue

        deps.add(IMPORT_TO_PIP.get(module, module))

    return sorted(deps)


def infer_node_fields(config: Dict, source_path: Path) -> Tuple[Dict[str, str], Dict[str, List[str]]]:
    include_local_modules = bool(
        cfg_get(config, "INCLUDE_LOCAL_MODULES", cfg_get(config, "INCLUDE_LOCAL_MODULES_IN_DEPENDENCIES", False))
    )

    detected_dependencies = discover_dependencies(source_path, include_local_modules=include_local_modules)
    detected_flags = discover_cli_flags(source_path)

    source_dir_rel = source_path.parent.relative_to(WEBROOT_DIR).as_posix()
    source_file_name = source_path.name

    inferred = {
        "link": source_dir_rel,
        "python_cmds": f"python {source_file_name}",
        "dependencies": ",".join(detected_dependencies),
    }

    return inferred, {
        "dependencies": detected_dependencies,
        "cli_flags": detected_flags,
    }


def normalize_node_id(node_id: str) -> str:
    return normalize_key(node_id)


def format_value(value) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "yes" if value else "no"
    return str(value)


def merge_row(base_row: Dict[str, str], updates: Dict[str, str], fieldnames: List[str]) -> Dict[str, str]:
    merged = dict(base_row)
    for field in fieldnames:
        merged.setdefault(field, "")
    for key, value in updates.items():
        if key in fieldnames:
            merged[key] = format_value(value)
    return merged


def extend_fieldnames(fieldnames: List[str], updates: Dict[str, str]) -> List[str]:
    extended = list(fieldnames)
    for key in updates.keys():
        if key not in extended:
            extended.append(key)
    return extended


def select_node_cfg(source_config: Dict, source_python_rel: str) -> Dict:
    nodes_cfg = cfg_get(source_config, "NODES", {})
    if not nodes_cfg:
        return {}
    if not isinstance(nodes_cfg, dict):
        raise ValueError("NODES in source config.yaml must be a mapping/object")

    source_name = Path(source_python_rel).name
    source_stem_norm = normalize_key(Path(source_python_rel).stem)

    # Priority 1: explicit source_python match on each node config
    for _, node_cfg in nodes_cfg.items():
        if not isinstance(node_cfg, dict):
            continue
        cfg_source = node_cfg.get("source_python") or node_cfg.get("SOURCE_PYTHON")
        if cfg_source and Path(str(cfg_source)).name == source_name:
            return node_cfg

    # Priority 2: node key matches normalized source stem
    for key, node_cfg in nodes_cfg.items():
        if not isinstance(node_cfg, dict):
            continue
        if normalize_key(str(key)) == source_stem_norm:
            return node_cfg

    # Priority 3: single entry fallback
    if len(nodes_cfg) == 1:
        only_value = next(iter(nodes_cfg.values()))
        if isinstance(only_value, dict):
            return only_value

    return {}


def extract_admin_row_updates(admin_config: Dict) -> Dict[str, str]:
    updates: Dict[str, str] = {}
    for key, value in admin_config.items():
        if not isinstance(key, str):
            continue
        key_upper = key.upper()
        if key_upper in CONTROL_KEYS:
            continue
        updates[FIELD_KEY_ALIASES.get(key_upper, key.lower())] = value
    return updates


def build_target_updates(
    admin_config: Dict,
    source_config: Dict,
    inferred_fields: Dict[str, str],
    discovered: Dict[str, List[str]],
) -> Dict[str, str]:
    admin_row_updates = extract_admin_row_updates(admin_config)
    manual_row_update = bool(cfg_get(admin_config, "MANUAL_ROW_UPDATE", False))

    if manual_row_update:
        updates = dict(admin_row_updates)
        node_id = cfg_get(admin_config, "NODE_ID", updates.get("node_id"))
        if node_id is None or str(node_id).strip() == "":
            raise ValueError("NODE_ID is required for MANUAL_ROW_UPDATE")
        updates["node_id"] = normalize_node_id(str(node_id))
        if not updates["node_id"]:
            raise ValueError("Could not derive a valid node_id")
        return updates

    source_path_value = cfg_get(admin_config, "SOURCE_PYTHON")
    source_path_str = source_path_value if source_path_value else ""
    node_cfg = select_node_cfg(source_config, source_path_str) or {}

    if not isinstance(node_cfg, dict):
        raise ValueError("Selected NODES entry in source config.yaml must be a mapping/object")

    substitutions = {
        "source_python": source_path_str,
        "source_file": Path(source_path_str).name if source_path_str else "",
        "source_dir": str(Path(source_path_str).parent).replace("\\", "/") if source_path_str else "",
        "detected_dependencies": ",".join(discovered.get("dependencies", [])),
        "detected_flags": ",".join(discovered.get("cli_flags", [])),
    }

    def apply_substitutions(item):
        if isinstance(item, str):
            return item.format(**substitutions)
        return item

    updates = {}
    updates.update({k: apply_substitutions(v) for k, v in inferred_fields.items()})
    updates.update({k: apply_substitutions(v) for k, v in admin_row_updates.items()})
    updates.update({k: apply_substitutions(v) for k, v in node_cfg.items()})

    node_id = cfg_get(admin_config, "NODE_ID")
    if node_id is None or str(node_id).strip() == "":
        node_id = updates.get("node_id")

    if not node_id:
        fallback = Path(source_path_str).with_suffix("").as_posix().replace("/", "_") if source_path_str else "node"
        node_id = fallback

    updates["node_id"] = normalize_node_id(str(node_id))

    if not updates["node_id"]:
        raise ValueError("Could not derive a valid node_id")

    if not updates.get("name"):
        updates["name"] = Path(source_path_str).stem.replace("-", " ").replace("_", " ").title()
    if not updates.get("description"):
        updates["description"] = f"Runs {Path(source_path_str).name}" if source_path_str else "Runs Python script"

    return updates


def upsert_streaming(nodes_csv: Path, target_updates: Dict[str, str], match_node_id: str | None = None) -> Tuple[bool, List[str]]:
    temp_path = nodes_csv.with_suffix(".tmp")
    replaced = False

    with nodes_csv.open("r", encoding="utf-8", newline="") as source, temp_path.open("w", encoding="utf-8", newline="") as dest:
        reader = csv.DictReader(source)
        if not reader.fieldnames:
            raise ValueError(f"nodes.csv has no header row: {nodes_csv}")

        fieldnames = extend_fieldnames(list(reader.fieldnames), target_updates)
        writer = csv.DictWriter(dest, fieldnames=fieldnames)
        writer.writeheader()

        target_id = target_updates["node_id"]
        match_id = (match_node_id or target_id).strip().lower()

        for row in reader:
            if row.get("node_id", "").strip().lower() == match_id:
                row = merge_row(row, target_updates, fieldnames)
                replaced = True
            writer.writerow({k: row.get(k, "") for k in fieldnames})

        if not replaced:
            new_row = merge_row({}, target_updates, fieldnames)
            writer.writerow({k: new_row.get(k, "") for k in fieldnames})

    shutil.move(str(temp_path), str(nodes_csv))
    return replaced, fieldnames


def upsert_in_memory(nodes_csv: Path, target_updates: Dict[str, str], match_node_id: str | None = None) -> Tuple[bool, List[str]]:
    with nodes_csv.open("r", encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source)
        if not reader.fieldnames:
            raise ValueError(f"nodes.csv has no header row: {nodes_csv}")
        fieldnames = extend_fieldnames(list(reader.fieldnames), target_updates)
        rows = list(reader)

    target_id = target_updates["node_id"]
    match_id = (match_node_id or target_id).strip().lower()
    replaced = False

    for idx, row in enumerate(rows):
        if row.get("node_id", "").strip().lower() == match_id:
            rows[idx] = merge_row(row, target_updates, fieldnames)
            replaced = True
            break

    if not replaced:
        rows.append(merge_row({}, target_updates, fieldnames))

    with nodes_csv.open("w", encoding="utf-8", newline="") as dest:
        writer = csv.DictWriter(dest, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows([{k: r.get(k, "") for k in fieldnames} for r in rows])

    return replaced, fieldnames


def sort_nodes_csv_by_order(nodes_csv: Path):
    with nodes_csv.open("r", encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source)
        if not reader.fieldnames:
            raise ValueError(f"nodes.csv has no header row: {nodes_csv}")
        fieldnames = list(reader.fieldnames)
        rows = list(reader)

    def rank(row: Dict[str, str]) -> Tuple[int, str]:
        raw = (row.get("order") or "").strip()
        try:
            order_num = int(raw)
        except (TypeError, ValueError):
            order_num = 10**9
        node_id = (row.get("node_id") or "").strip().lower()
        return order_num, node_id

    rows.sort(key=rank)

    with nodes_csv.open("w", encoding="utf-8", newline="") as dest:
        writer = csv.DictWriter(dest, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows([{k: r.get(k, "") for k in fieldnames} for r in rows])


def load_json_map(path: Path) -> Dict:
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def guess_working_directory(link_value: str) -> str:
    raw = (link_value or "").strip().replace("\\", "/")
    if raw.startswith("data-pipeline/"):
        return raw.replace("data-pipeline/", "", 1)
    return raw


def make_node_notes(row: Dict[str, str]) -> str:
    parts: List[str] = []
    if row.get("description"):
        parts.append(row["description"].strip())
    if row.get("output_info"):
        parts.append(f"Output: {row['output_info'].strip()}")
    if row.get("processing_time_est"):
        parts.append(f"Processing time: {row['processing_time_est'].strip()}")
    return ". ".join([p for p in parts if p]).strip()


def index_node_positions(*datasets: Dict) -> Dict[str, List[int]]:
    positions: Dict[str, List[int]] = {}
    for dataset in datasets:
        for node in dataset.get("nodes", []) if isinstance(dataset.get("nodes"), list) else []:
            if not isinstance(node, dict):
                continue
            pos = node.get("position")
            if not (isinstance(pos, list) and len(pos) == 2):
                continue
            node_id = str(node.get("id") or "").strip()
            if node_id:
                positions[node_id] = [int(pos[0]), int(pos[1])]
    return positions


def grid_position(index: int) -> List[int]:
    cols = 4
    col = index % cols
    row = index // cols
    return [240 + col * 260, 120 + row * 160]


def update_nodes_json_from_csv(nodes_csv: Path):
    nodes_json = nodes_csv.parent / "nodes.json"
    nodes_all_json = nodes_csv.parent / "nodes-all.json"

    with nodes_csv.open("r", encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source)
        rows = list(reader)

    existing_nodes_json = load_json_map(nodes_json)
    template_nodes_json = load_json_map(nodes_all_json)
    known_positions = index_node_positions(existing_nodes_json, template_nodes_json)

    nodes = [
        {
            "id": "trigger",
            "name": "Start Pipeline",
            "type": "n8n-nodes-base.manualTrigger",
            "position": [100, 300],
            "parameters": {},
            "typeVersion": 1,
        }
    ]

    node_name_by_id: Dict[str, str] = {}

    for idx, row in enumerate(rows):
        node_id = (row.get("node_id") or "").strip()
        if not node_id:
            continue
        node_name = (row.get("name") or node_id).strip()
        node_name_by_id[node_id] = node_name
        position = known_positions.get(node_id) or grid_position(idx)
        nodes.append(
            {
                "id": node_id,
                "name": node_name,
                "type": "n8n-nodes-base.executeCommand",
                "position": position,
                "parameters": {
                    "command": (row.get("python_cmds") or "").strip(),
                    "workingDirectory": guess_working_directory(row.get("link") or ""),
                },
                "typeVersion": 1,
                "notes": make_node_notes(row),
            }
        )

    connections: Dict[str, Dict[str, List[List[Dict[str, object]]]]] = {}

    for row in rows:
        child_id = (row.get("node_id") or "").strip()
        parent_id = (row.get("node_parent") or row.get("parent_node") or "").strip()
        if not child_id or not parent_id:
            continue
        parent_name = node_name_by_id.get(parent_id)
        child_name = node_name_by_id.get(child_id)
        if not parent_name or not child_name:
            continue
        if parent_name not in connections:
            connections[parent_name] = {"main": [[]]}
        connections[parent_name]["main"][0].append(
            {"node": child_name, "type": "main", "index": 0}
        )

    payload = {"nodes": nodes, "connections": connections}
    with nodes_json.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")


def main() -> int:
    config_path, cli_overrides = parse_cli_overrides(sys.argv[1:])
    config = load_config(config_path)
    if cli_overrides:
        config.update(cli_overrides)

    nodes_csv_raw = str(cfg_get(config, "NODES_CSV", "../../nodes.csv"))
    manual_row_update = bool(cfg_get(config, "MANUAL_ROW_UPDATE", False))
    source_python_raw = cfg_get(config, "SOURCE_PYTHON")

    nodes_csv = resolve_path(nodes_csv_raw, config_path.parent)
    source_python = resolve_path(str(source_python_raw), config_path.parent) if source_python_raw else None

    if not nodes_csv.exists():
        raise FileNotFoundError(f"nodes.csv not found: {nodes_csv}")
    if not manual_row_update:
        if not source_python_raw:
            raise ValueError("config.yaml must set SOURCE_PYTHON")
        if source_python is None or not source_python.exists():
            raise FileNotFoundError(f"source_python not found: {source_python}")

    inferred_fields: Dict[str, str] = {}
    discovered: Dict[str, List[str]] = {"dependencies": [], "cli_flags": []}
    source_rel = ""
    source_config_path: Path | None = None
    source_config: Dict = {}

    if not manual_row_update:
        inferred_fields, discovered = infer_node_fields(config, source_python)
        # Ensure substitution paths are repo-relative and portable.
        source_rel = source_python.relative_to(WEBROOT_DIR).as_posix()
        config["SOURCE_PYTHON"] = source_rel

        source_config_path = source_python.parent / "config.yaml"
        source_config = load_config(source_config_path) if source_config_path.exists() else {}
    elif source_python and source_python.exists():
        source_rel = source_python.relative_to(WEBROOT_DIR).as_posix()
        config["SOURCE_PYTHON"] = source_rel

    target_updates = build_target_updates(config, source_config, inferred_fields, discovered)
    match_node_id = cfg_get(config, "ORIGINAL_NODE_ID")
    if match_node_id is not None:
        match_node_id = normalize_node_id(str(match_node_id))
    if not match_node_id:
        match_node_id = target_updates["node_id"]

    read_all = bool(cfg_get(config, "READ_ALL_NODES", cfg_get(config, "READ_ALL_EXISTING_NODES", False)))

    try:
        if read_all:
            replaced, fieldnames = upsert_in_memory(nodes_csv, target_updates, match_node_id=match_node_id)
            mode = "in-memory"
        else:
            replaced, fieldnames = upsert_streaming(nodes_csv, target_updates, match_node_id=match_node_id)
            mode = "streaming"

        sort_nodes_csv_by_order(nodes_csv)
        update_nodes_json_from_csv(nodes_csv)
    except PermissionError as exc:
        err_path = getattr(exc, "filename", None) or getattr(exc, "filename2", None) or str(nodes_csv)
        raise PermissionError(
            f"Permission denied while updating pipeline files. "
            f"Path: {err_path}. "
            f"Operation: upsert/sort/write nodes.csv or nodes.json. "
            f"Original error: {exc}"
        ) from exc

    print(f"[OK] {'Updated' if replaced else 'Inserted'} node_id={target_updates['node_id']}")
    print(f"[OK] nodes.csv: {nodes_csv.relative_to(WEBROOT_DIR)}")
    print(f"[OK] nodes.json: {(nodes_csv.parent / 'nodes.json').relative_to(WEBROOT_DIR)}")
    print(f"[OK] mode: {mode}")
    if source_rel:
        print(f"[OK] source analyzed: {source_rel}")
    if source_config_path is not None:
        print(
            f"[OK] source config: "
            f"{source_config_path.relative_to(WEBROOT_DIR) if source_config_path.exists() else 'not found'}"
        )
    if discovered["dependencies"]:
        print(f"[OK] detected dependencies: {', '.join(discovered['dependencies'])}")
    if discovered["cli_flags"]:
        print(f"[OK] detected CLI flags: {', '.join(discovered['cli_flags'])}")
    print(f"[OK] columns preserved: {len(fieldnames)}")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"[ERROR] {exc.__class__.__name__}: {exc}", file=sys.stderr)
        print(f"[ERROR] cwd: {Path.cwd()}", file=sys.stderr)
        print(f"[ERROR] argv: {' '.join(sys.argv)}", file=sys.stderr)
        if isinstance(exc, OSError):
            print(
                f"[ERROR] os_error_details: errno={getattr(exc, 'errno', None)} "
                f"filename={getattr(exc, 'filename', None)} "
                f"filename2={getattr(exc, 'filename2', None)}",
                file=sys.stderr,
            )
        traceback.print_exc()
        raise SystemExit(1)
