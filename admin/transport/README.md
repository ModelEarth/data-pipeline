# File Transport

Moves .csv files into a data-pipe-csv sub-folder (repo).
We use to reduce the size of the data-pipeline repo so we can include it in our webroot.

You can fork data-pipe-csv into data-pipeline.
Remove OUTPUT_LOCAL_PATH to push directly to Github.

Run in the root of your local data-pipeline repo:

	python3 -m venv env
	source env/bin/activate
	python admin/transport/data_transport


DELETE_LOCAL_AFTER_COPY = False

Prevents files from being deleted in the data-pipeline folder.