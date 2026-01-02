#!/usr/bin/env python3
"""
Flask Server for Data Pipeline Admin Interface

This Flask server provides API endpoints for running data pipeline nodes
from the web-based admin interface.

Usage:
    python flask_server.py
    # or
    flask run --port 5001

The server runs on http://localhost:5001 since 5000 is used by macOS AirPlay
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import os
import sys
import csv
import json
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

# Import functions from manage_pipelines.py
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))
from manage_pipelines import load_nodes_csv, run_node as run_pipeline_node

app = Flask(__name__)
CORS(app)  # Enable CORS for localhost requests

# Store running processes
running_processes = {}
process_lock = threading.Lock()

NODES_CSV = SCRIPT_DIR / "nodes.csv"


def get_node_by_id(node_id: str) -> Optional[Dict]:
    """Get node information by node_id."""
    nodes = load_nodes_csv()
    return next((n for n in nodes if n.get('node_id') == node_id), None)


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Flask availability detection."""
    return jsonify({
        'status': 'ok',
        'service': 'data-pipeline-flask-server',
        'port': 5001,
        'timestamp': datetime.now().isoformat()
    }), 200


@app.route('/api/nodes', methods=['GET'])
def list_nodes():
    """List all pipeline nodes."""
    try:
        nodes = load_nodes_csv()
        return jsonify({
            'success': True,
            'nodes': nodes,
            'count': len(nodes)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/nodes/<node_id>', methods=['GET'])
def get_node(node_id: str):
    """Get information about a specific node."""
    try:
        node = get_node_by_id(node_id)
        if not node:
            return jsonify({
                'success': False,
                'error': f'Node {node_id} not found'
            }), 404
        
        return jsonify({
            'success': True,
            'node': node
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/nodes/run', methods=['POST'])
def run_node():
    """Execute a pipeline node command."""
    try:
        data = request.get_json()
        node_id = data.get('node_id')
        command = data.get('command')
        working_directory = data.get('working_directory')
        
        if not node_id:
            return jsonify({
                'success': False,
                'error': 'node_id is required'
            }), 400
        
        # Get node info
        node = get_node_by_id(node_id)
        if not node:
            return jsonify({
                'success': False,
                'error': f'Node {node_id} not found'
            }), 404
        
        # Check if run_process_available
        run_available = node.get('run_process_available', '').lower()
        if run_available == 'no':
            return jsonify({
                'success': False,
                'error': f'Node {node_id} does not have run_process_available enabled'
            }), 400
        
        # Use command from node if not provided
        if not command:
            command = node.get('python_cmds', '')
        
        if not command:
            return jsonify({
                'success': False,
                'error': f'No command specified for node {node_id}'
            }), 400
        
        # Use working directory from node if not provided
        if not working_directory:
            working_directory = node.get('link', '')
        
        # Resolve working directory path
        if working_directory.startswith('../'):
            work_path = SCRIPT_DIR / working_directory
        else:
            work_path = SCRIPT_DIR / working_directory
        
        if not work_path.exists():
            return jsonify({
                'success': False,
                'error': f'Working directory does not exist: {work_path}'
            }), 400
        
        # Check if process is already running
        with process_lock:
            if node_id in running_processes:
                return jsonify({
                    'success': False,
                    'error': f'Node {node_id} is already running'
                }), 409
        
        # For very_slow processes, run in background
        processing_time = node.get('processing_time_est', '').lower()
        is_long_running = processing_time in ['slow', 'very_slow']
        
        if is_long_running:
            # Run in background thread
            thread = threading.Thread(
                target=run_node_background,
                args=(node_id, command, str(work_path), node)
            )
            thread.daemon = True
            thread.start()
            
            return jsonify({
                'success': True,
                'message': f'Node {node_id} started in background',
                'node_id': node_id,
                'status': 'running',
                'processing_time': processing_time
            }), 202
        else:
            # Run synchronously
            return run_node_sync(node_id, command, str(work_path), node)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def run_node_sync(node_id: str, command: str, work_path: str, node: Dict):
    """Run a node synchronously and return result."""
    try:
        with process_lock:
            running_processes[node_id] = {
                'status': 'running',
                'started_at': datetime.now().isoformat()
            }
        
        # Execute command
        result = subprocess.run(
            command,
            shell=True,
            cwd=work_path,
            capture_output=True,
            text=True,
            timeout=3600  # 1 hour timeout for non-long-running processes
        )
        
        output = result.stdout
        error_output = result.stderr
        
        success = result.returncode == 0
        
        # Handle auto_commit if enabled
        auto_commit_result = None
        if success and node.get('auto_commit', '').lower() == 'yes':
            auto_commit_result = handle_auto_commit(node, work_path)
        
        response_data = {
            'success': success,
            'node_id': node_id,
            'output': output,
            'stderr': error_output,
            'returncode': result.returncode,
            'command': command,
            'working_directory': work_path
        }
        
        if auto_commit_result:
            response_data['auto_commit'] = auto_commit_result
        
        with process_lock:
            if node_id in running_processes:
                del running_processes[node_id]
        
        status_code = 200 if success else 500
        return jsonify(response_data), status_code
    
    except subprocess.TimeoutExpired:
        with process_lock:
            if node_id in running_processes:
                del running_processes[node_id]
        return jsonify({
            'success': False,
            'error': f'Node {node_id} execution timed out',
            'node_id': node_id
        }), 504
    except Exception as e:
        with process_lock:
            if node_id in running_processes:
                del running_processes[node_id]
        return jsonify({
            'success': False,
            'error': str(e),
            'node_id': node_id
        }), 500


def run_node_background(node_id: str, command: str, work_path: str, node: Dict):
    """Run a node in background thread."""
    try:
        with process_lock:
            running_processes[node_id] = {
                'status': 'running',
                'started_at': datetime.now().isoformat()
            }
        
        # Execute command (no timeout for very_slow processes)
        result = subprocess.run(
            command,
            shell=True,
            cwd=work_path,
            capture_output=True,
            text=True
        )
        
        success = result.returncode == 0
        
        # Handle auto_commit if enabled
        auto_commit_result = None
        if success and node.get('auto_commit', '').lower() == 'yes':
            auto_commit_result = handle_auto_commit(node, work_path)
        
        # Store result (could be written to a file or database)
        with process_lock:
            running_processes[node_id] = {
                'status': 'completed' if success else 'failed',
                'started_at': running_processes[node_id]['started_at'],
                'completed_at': datetime.now().isoformat(),
                'success': success,
                'auto_commit': auto_commit_result
            }
    
    except Exception as e:
        with process_lock:
            running_processes[node_id] = {
                'status': 'failed',
                'error': str(e),
                'started_at': running_processes.get(node_id, {}).get('started_at'),
                'completed_at': datetime.now().isoformat()
            }


@app.route('/api/nodes/<node_id>/status', methods=['GET'])
def get_node_status(node_id: str):
    """Get status of a running node."""
    with process_lock:
        status = running_processes.get(node_id)
    
    if not status:
        return jsonify({
            'success': False,
            'error': f'No running process found for node {node_id}'
        }), 404
    
    return jsonify({
        'success': True,
        'node_id': node_id,
        'status': status
    }), 200


def handle_auto_commit(node: Dict, work_path: str) -> Dict:
    """Handle automatic commit and PR creation for data updates."""
    try:
        target_repo = node.get('target_repo', '')
        if not target_repo:
            return {'success': False, 'error': 'No target_repo specified'}
        
        # Map target_repo names to actual repository paths
        repo_paths = {
            'community-data': Path(SCRIPT_DIR.parent.parent) / 'community-data',
            'community-timelines': Path(SCRIPT_DIR.parent.parent) / 'community-timelines',
            'products-data': Path(SCRIPT_DIR.parent.parent) / 'products-data'
        }
        
        repo_path = repo_paths.get(target_repo)
        if not repo_path or not repo_path.exists():
            return {'success': False, 'error': f'Repository {target_repo} not found at {repo_path}'}
        
        # Get output path from node
        output_path = node.get('output_path', '')
        if not output_path:
            return {'success': False, 'error': 'No output_path specified'}
        
        # Resolve output path relative to repo
        if output_path.startswith('../../../'):
            # Relative path from data-pipeline
            actual_output_path = SCRIPT_DIR.parent.parent.parent / output_path.replace('../../../', '')
        elif output_path.startswith('../../'):
            actual_output_path = SCRIPT_DIR.parent.parent / output_path.replace('../../', '')
        else:
            actual_output_path = repo_path / output_path
        
        # Check if output path exists and has changes
        if not actual_output_path.exists():
            return {'success': False, 'error': f'Output path does not exist: {actual_output_path}'}
        
        # Change to repo directory
        os.chdir(str(repo_path))
        
        # Check git status
        git_status = subprocess.run(
            ['git', 'status', '--porcelain'],
            capture_output=True,
            text=True
        )
        
        if not git_status.stdout.strip():
            return {'success': True, 'message': 'No changes to commit'}
        
        # Get current branch
        branch_result = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            capture_output=True,
            text=True
        )
        current_branch = branch_result.stdout.strip()
        
        # Create a new branch for this update
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        new_branch = f'data-update-{node.get("node_id")}-{timestamp}'
        
        # Create and checkout new branch
        subprocess.run(['git', 'checkout', '-b', new_branch], check=True)
        
        # Add changes
        subprocess.run(['git', 'add', '.'], check=True)
        
        # Commit
        commit_message = f'Data update from {node.get("node_id")}: {node.get("name")}'
        subprocess.run(
            ['git', 'commit', '-m', commit_message],
            check=True
        )
        
        # Get remote URL to determine fork
        remote_result = subprocess.run(
            ['git', 'remote', 'get-url', 'origin'],
            capture_output=True,
            text=True
        )
        remote_url = remote_result.stdout.strip()
        
        # Push to fork (assuming fork remote exists or is origin)
        push_result = subprocess.run(
            ['git', 'push', 'origin', new_branch],
            capture_output=True,
            text=True
        )
        
        if push_result.returncode != 0:
            return {
                'success': False,
                'error': f'Failed to push to remote: {push_result.stderr}'
            }
        
        # Create PR using GitHub CLI or API
        pr_result = create_pr_via_gh_cli(repo_path, new_branch, commit_message, remote_url)
        
        return {
            'success': True,
            'branch': new_branch,
            'commit_message': commit_message,
            'pushed': True,
            'pr': pr_result
        }
    
    except subprocess.CalledProcessError as e:
        return {
            'success': False,
            'error': f'Git operation failed: {e.stderr}'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def create_pr_via_gh_cli(repo_path: Path, branch: str, title: str, remote_url: str) -> Dict:
    """Create a PR using GitHub CLI if available."""
    try:
        # Extract repo owner and name from remote URL
        # Format: https://github.com/owner/repo.git or git@github.com:owner/repo.git
        if 'github.com' in remote_url:
            parts = remote_url.replace('.git', '').split('/')
            repo_name = parts[-1]
            owner = parts[-2] if len(parts) > 1 else 'ModelEarth'
        else:
            repo_name = repo_path.name
            owner = 'ModelEarth'
        
        # Try to create PR using gh CLI
        pr_result = subprocess.run(
            ['gh', 'pr', 'create', '--title', title, '--body', f'Automated data update from pipeline node.\n\nBranch: {branch}'],
            cwd=str(repo_path),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if pr_result.returncode == 0:
            return {
                'success': True,
                'url': pr_result.stdout.strip(),
                'method': 'gh_cli'
            }
        else:
            # Return PR creation URL for manual creation
            base_repo = remote_url.replace('.git', '').replace('git@github.com:', 'https://github.com/')
            pr_url = f'{base_repo}/compare/{branch}?expand=1'
            return {
                'success': False,
                'message': 'GitHub CLI not available or failed',
                'manual_url': pr_url,
                'method': 'manual'
            }
    
    except FileNotFoundError:
        # gh CLI not installed
        base_repo = remote_url.replace('.git', '').replace('git@github.com:', 'https://github.com/')
        pr_url = f'{base_repo}/compare/{branch}?expand=1'
        return {
            'success': False,
            'message': 'GitHub CLI not installed',
            'manual_url': pr_url,
            'method': 'manual'
        }
    except Exception as e:
        base_repo = remote_url.replace('.git', '').replace('git@github.com:', 'https://github.com/')
        pr_url = f'{base_repo}/compare/{branch}?expand=1'
        return {
            'success': False,
            'error': str(e),
            'manual_url': pr_url,
            'method': 'manual'
        }


if __name__ == '__main__':
    # Use port 5001 to avoid conflict with macOS AirPlay on port 5000
    FLASK_PORT = 5001
    print("Starting Flask server for Data Pipeline Admin...")
    print(f"Server will run on http://localhost:{FLASK_PORT}")
    print(f"Health check: http://localhost:{FLASK_PORT}/health")
    app.run(host='127.0.0.1', port=FLASK_PORT, debug=True)

