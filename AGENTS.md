# Data Pipeline - AI CLI Guide

This file provides guidance to Claude Code (claude.ai/code) and other AI CLI processes when working with the data-pipeline repository.

## Overview

The data-pipeline repository provides tools for processing, analyzing, and managing data workflows. It includes:
- **Admin Interface**: Web-based UI at `/data-pipeline/admin/` for managing pipeline nodes
- **Flask API Server**: Backend server (port 5001) for executing data pipeline nodes with automatic dependency management
- **Pipeline Nodes**: CSV-defined processing tasks with Python script execution

## Development Commands

### Start Data Pipeline Flask Server

When you type "start pipeline", run:

```bash
# Check if data-pipeline Flask server is already running on port 5001
if lsof -ti:5001 > /dev/null 2>&1; then
  echo "Data pipeline Flask server already running on port 5001"
else
  # Navigate to data-pipeline/flask
  cd data-pipeline/flask

  # Create virtual environment if it doesn't exist
  if [ ! -d "env" ]; then
    python3 -m venv env
  fi

  # Activate virtual environment
  source env/bin/activate

  # Install Flask and CORS if not already installed
  pip install -q flask flask-cors

  # Start Flask server in background (disable debug/reloader for stable daemon mode)
  nohup python -c "import flask_server as s; s.app.run(host='127.0.0.1', port=5001, debug=False, use_reloader=False)" > flask.log 2>&1 &

  echo "Started data pipeline Flask server on port 5001"
  echo "Health check: http://localhost:5001/health"
  echo "Data pipeline API: http://localhost:5001/api/nodes/"

  # Return to webroot
  cd ../..
fi
```

**What this command does:**
- Starts Flask server on port 5001 for data pipeline operations
- Executes data pipeline nodes with automatic Python dependency installation
- Manages background processes for long-running tasks
- Uses dedicated virtual environment in `data-pipeline/flask/env/`
- Runs in background with output logged to `data-pipeline/flask/flask.log`

**Verify server is running:**
```bash
curl http://localhost:5001/health
```

**If `start pipeline` says started but `5001` is still down:**
```bash
cd data-pipeline/flask
source env/bin/activate
python -c "import flask_server as s; s.app.run(host='127.0.0.1', port=5001, debug=False, use_reloader=False)"
```
This runs Flask in the active terminal so startup errors are visible immediately.

**Stop the server:**
```bash
lsof -ti:5001 | xargs kill
```

**View logs:**
```bash
tail -f data-pipeline/flask/flask.log
```

### Using the Data Pipeline Admin

Once the Flask server is running, visit:
- **Admin Interface**: http://localhost:8887/data-pipeline/admin/
- **Node Management**: Select nodes from the list to view details and run processes
- **Flask Integration**: The admin checks for Flask availability and shows a warning banner if not running

## Flask API Server Features

The Flask server (port 5001) provides:
- ✅ **Dedicated API endpoints** for executing data pipeline Python scripts
- ✅ **Automatic Python pip dependency installation** before running each node
- ✅ **Background process management** for long-running tasks
- ✅ **Process status tracking** via `/api/nodes/<node_id>/status`
- ✅ **CORS-enabled API** for the admin interface

## API Endpoints

- **Health Check**: `GET /health`
- **List Nodes**: `GET /api/nodes`
- **Get Node**: `GET /api/nodes/<node_id>`
- **Run Node**: `POST /api/nodes/run`
- **Node Status**: `GET /api/nodes/<node_id>/status`

## Pipeline Nodes Configuration

Pipeline nodes are defined in `data-pipeline/nodes.csv` with the following key fields:
- `node_id`: Unique identifier
- `name`: Display name
- `python_cmds`: Python command to execute
- `dependencies`: Comma-separated pip packages (auto-installed)
- `run_process_available`: `yes` to enable web execution
- `processing_time_est`: `fast`, `medium`, `slow`, `very_slow`
- `link`: Working directory path for execution

## Development Standards

- **Virtual Environment**: Each Flask server maintains its own isolated virtual environment
- **Port Assignment**: Data pipeline Flask uses port 5001 (different from cloud/run on 8100)
- **Dependency Management**: Dependencies are auto-installed per node from `nodes.csv`
- **Background Execution**: Long-running processes (`slow`, `very_slow`) run in background threads

## Related Documentation

- **Flask Setup Guide**: [data-pipeline/flask/README.md](flask/README.md)
- **Admin Interface**: [data-pipeline/admin/](admin/)
- **Main Webroot Guide**: [team/CLAUDE.md](../team/CLAUDE.md)
