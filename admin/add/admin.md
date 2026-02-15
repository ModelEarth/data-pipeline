# Add Node Quick Guide

Use **Add or Update a Node** (`add_node`) to upsert rows in `data-pipeline/nodes.csv`.

## Example 1: Add/Update `exiobase`

Set these config fields in the Add Node panel:

- `SOURCE_PYTHON`: `../../../exiobase/tradeflow/main.py`
- `NODE_ID`: `exiobase`

Then click **Run Process**.

## Example 2: Add/Update `us_bea`

Set these config fields in the Add Node panel:

- `SOURCE_PYTHON`: `../../../exiobase/tradeflow/us-bea.py`
- `NODE_ID`: `us_bea`

Then click **Run Process**.

## Note

You do not manually enter `exiobase/tradeflow/config.yaml` in the UI.
`add_node` reads it automatically from the folder that contains `SOURCE_PYTHON`.
