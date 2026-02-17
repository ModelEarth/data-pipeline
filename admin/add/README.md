# Pipeline Row Editor

[Add/Update](../#node=add_node) a row in [nodes.csv](https://github.com/ModelEarth/data-pipeline/blob/main/nodes.csv)

## Initial Row Insert

To insert row(s) initially, enter the folder in this vibe prompt:

    Add a data-pipeline/nodes.csv row or rows for the python processes found in folder [folder] and populate the columns based on analysis of the code in the folders. The "link" column contains the path from the site root to the python code’s folder. Include commands found to run the file with any documented parameters. The same folder may contain multiple files to run, so you can add more than one row if needed. The nodes.csv file can be used by n8n to create a “nodes.json” workflow json file. Update the local nodes.json file for the row(s) in nodes.csv updated and include any parent-child relations between nodes in the nodes.json update.

    node_id
    name
    description
    type
    order
    link
    python_cmds
    output_path
    output_info
    folder_size
    n8n_parallel_safe (yes indicates the python is safe to run in parallel)

    There are additional columns with info that will be useful to n8n when executing the python scripts.

## About Editor

- `node.py` reads `data-pipeline/admin/add/config.yaml` (uppercase first-level keys)
- It analyzes Python file (`SOURCE_PYTHON`) to infer:
  - `python_cmds`
  - `link`
  - `dependencies`
  - CLI flags from `argparse.add_argument(...)`
- It also reads the source script folder's `config.yaml` and expects node-row fields under `NODES`
- It inserts or updates exactly one row by `node_id`
- Default mode is **streaming upsert** (`READ_ALL_EXISTING_NODES: false`) so it does not load all nodes into memory

## Python, Yaml.Config, CSV Output

- `data-pipeline/admin/add/node.py` - upsert script
- `data-pipeline/admin/add/config.yaml` - node row config
- `data-pipeline/nodes.csv` - target registry

## Config Fields

`data-pipeline/admin/add/config.yaml`:

- `NODES_CSV`: path to `nodes.csv`
- `SOURCE_PYTHON`: script to analyze
- `READ_ALL_EXISTING_NODES`: optional, default `false`
- `INCLUDE_LOCAL_MODULES_IN_DEPENDENCIES`: optional, default `false`
- `NODE_ID`: optional explicit `node_id` override for this run
- Any other first-level uppercase keys are treated as row values (example: `NAME`, `TYPE`, `ORDER`, `RUN_PROCESS_AVAILABLE`)

Node-specific values are now taken from the source folder config at:

- `<SOURCE_PYTHON folder>/config.yaml` under top-level `NODES`
- `node.py` selects one entry by:
- `source_python` filename match (preferred), then
- key match to normalized source filename stem (for example `us-bea.py` -> `us_bea`)

Supported substitutions in each `NODES.<key>` values:

- `{source_python}`
- `{source_file}`
- `{source_dir}`
- `{detected_dependencies}`
- `{detected_flags}`

## Usage

From web interface:
[Add/Update](../#node=add_node) a row

From webroot:

```bash
python data-pipeline/admin/add/node.py
```

Or with a different config file:

```bash
python data-pipeline/admin/add/node.py path/to/config.yaml
```

## Add `us-bea.py` Node

Set in `data-pipeline/admin/add/config.yaml`:

- `SOURCE_PYTHON: ../../../exiobase/tradeflow/us-bea.py`

Set in `exiobase/tradeflow/config.yaml`:

- `NODES.us_bea.node_id: us_bea`
- `NODES.us_bea.python_cmds: python us-bea.py`
- `NODES.us_bea.link: exiobase/tradeflow`

Then run `node.py` when you are ready.

## Add `node.py` Itself as a Node

Reuse the same process with updated config values:

- `SOURCE_PYTHON: ../../../data-pipeline/admin/add/node.py`
- If no matching `NODES` entry exists for the source, `node.py` derives fallback values (`node_id`, `name`, `description`) from the source path.
- To force a specific id, set `NODE_ID` (example: `NODE_ID: add_node`).

Then run `node.py` again (when you are ready).

## Notes

- `node.py` does not run target scripts. It only updates one `nodes.csv` row.
- For Flask `Run Process`, ensure `python_cmds`, `link`, and `dependencies` are accurate.
- The UI reads a `config.yaml` in the script folder when building command inputs.
