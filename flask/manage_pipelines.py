#!/usr/bin/env python3
"""
Unified Data Pipeline Management Script

This script provides a centralized way to manage and run all data update processes
across the Model.earth data pipeline ecosystem.

Usage:
    python manage_pipelines.py list                    # List all available pipelines
    python manage_pipelines.py info <node_id>          # Show details for a specific node
    python manage_pipelines.py run <node_id>           # Run a specific pipeline node
    python manage_pipelines.py status                  # Show status of all pipelines
    python manage_pipelines.py dependencies <node_id>  # Show dependencies for a node
"""

import csv
import json
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Get the script directory
SCRIPT_DIR = Path(__file__).parent
NODES_CSV = SCRIPT_DIR.parent / "nodes.csv"
NODES_JSON = SCRIPT_DIR.parent / "nodes.json"


def load_nodes_csv() -> List[Dict]:
    """Load nodes from CSV file."""
    nodes = []
    if not NODES_CSV.exists():
        print(f"Warning: {NODES_CSV} not found")
        return nodes
    
    with open(NODES_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        nodes = list(reader)
    return nodes


def load_nodes_json() -> Dict:
    """Load nodes from JSON file."""
    if not NODES_JSON.exists():
        print(f"Warning: {NODES_JSON} not found")
        return {}
    
    with open(NODES_JSON, 'r', encoding='utf-8') as f:
        return json.load(f)


def list_all_pipelines():
    """List all available pipeline nodes."""
    nodes = load_nodes_csv()
    
    print("\n" + "="*80)
    print("MODEL.EARTH DATA PIPELINE NODES")
    print("="*80 + "\n")
    
    # Group by type
    by_type = {}
    for node in nodes:
        node_type = node.get('type', 'unknown')
        if node_type not in by_type:
            by_type[node_type] = []
        by_type[node_type].append(node)
    
    for node_type in sorted(by_type.keys()):
        print(f"\n{node_type.upper().replace('_', ' ')}:")
        print("-" * 80)
        for node in sorted(by_type[node_type], key=lambda x: int(x.get('order', 0))):
            node_id = node.get('node_id', 'N/A')
            name = node.get('name', 'N/A')
            description = node.get('description', '')[:60]
            processing_time = node.get('processing_time_est', 'unknown')
            print(f"  [{node_id:10s}] {name:40s} ({processing_time:10s})")
            if description:
                print(f"            {description}")
    
    print(f"\n\nTotal: {len(nodes)} pipeline nodes")
    print("="*80 + "\n")


def show_node_info(node_id: str):
    """Show detailed information for a specific node."""
    nodes = load_nodes_csv()
    
    node = next((n for n in nodes if n.get('node_id') == node_id), None)
    if not node:
        print(f"Error: Node '{node_id}' not found")
        return
    
    print("\n" + "="*80)
    print(f"NODE INFORMATION: {node_id}")
    print("="*80 + "\n")
    
    print(f"Name:        {node.get('name', 'N/A')}")
    print(f"Type:        {node.get('type', 'N/A')}")
    print(f"Description: {node.get('description', 'N/A')}")
    print(f"\nCommand:")
    print(f"  {node.get('python_cmds', 'N/A')}")
    print(f"\nWorking Directory:")
    print(f"  {node.get('link', 'N/A')}")
    print(f"\nOutput Path:")
    print(f"  {node.get('output_path', 'N/A')}")
    print(f"\nOutput Info:")
    print(f"  {node.get('output_info', 'N/A')}")
    print(f"\nProcessing Time: {node.get('processing_time_est', 'unknown')}")
    print(f"Folder Size:     {node.get('folder_size', 'unknown')}")
    print(f"Rate Limited:    {node.get('rate_limited', 'unknown')}")
    print(f"Parallel Safe:   {node.get('n8n_parallel_safe', 'unknown')}")
    
    deps = node.get('dependencies', '')
    if deps:
        print(f"\nDependencies:")
        for dep in deps.split(','):
            print(f"  - {dep.strip()}")
    
    api_keys = node.get('api_keys_required', 'none')
    if api_keys and api_keys.lower() != 'none':
        print(f"\nAPI Keys Required:")
        for key in api_keys.split(','):
            print(f"  - {key.strip()}")
    
    data_source = node.get('data_sources', '')
    if data_source:
        print(f"\nData Source: {data_source}")
    
    print("\n" + "="*80 + "\n")


def show_dependencies(node_id: str):
    """Show dependency chain for a node."""
    nodes_json = load_nodes_json()
    nodes_csv = load_nodes_csv()
    
    # Find node in CSV for name
    node_csv = next((n for n in nodes_csv if n.get('node_id') == node_id), None)
    if not node_csv:
        print(f"Error: Node '{node_id}' not found")
        return
    
    node_name = node_csv.get('name', node_id)
    
    # Find connections in JSON
    connections = nodes_json.get('connections', {})
    
    print("\n" + "="*80)
    print(f"DEPENDENCY CHAIN: {node_name} ({node_id})")
    print("="*80 + "\n")
    
    # Find what leads to this node
    upstream = []
    for source_node, targets in connections.items():
        for target_list in targets.get('main', []):
            for target in target_list:
                if target.get('node') == node_name:
                    upstream.append(source_node)
    
    if upstream:
        print("Upstream Dependencies (runs before this node):")
        for dep in upstream:
            print(f"  → {dep}")
    else:
        print("No upstream dependencies (can run independently)")
    
    # Find what this node leads to
    downstream = connections.get(node_name, {}).get('main', [])
    if downstream:
        print("\nDownstream Dependencies (runs after this node):")
        for target_list in downstream:
            for target in target_list:
                print(f"  → {target.get('node', 'N/A')}")
    else:
        print("\nNo downstream dependencies (terminal node)")
    
    print("\n" + "="*80 + "\n")


def run_node(node_id: str, dry_run: bool = False):
    """Run a specific pipeline node."""
    nodes = load_nodes_csv()
    
    node = next((n for n in nodes if n.get('node_id') == node_id), None)
    if not node:
        print(f"Error: Node '{node_id}' not found")
        return
    
    working_dir = node.get('link', '')
    command = node.get('python_cmds', '')
    
    if not command:
        print(f"Error: No command specified for node '{node_id}'")
        return
    
    # Resolve working directory path
    if working_dir.startswith('../'):
        # Relative to data-pipeline directory
        work_path = SCRIPT_DIR / working_dir
    else:
        work_path = SCRIPT_DIR / working_dir
    
    if not work_path.exists():
        print(f"Warning: Working directory does not exist: {work_path}")
        print(f"Attempting to run anyway...")
    
    print("\n" + "="*80)
    print(f"RUNNING NODE: {node.get('name', node_id)} ({node_id})")
    print("="*80 + "\n")
    print(f"Command:     {command}")
    print(f"Directory:   {work_path}")
    print(f"Processing:  {node.get('processing_time_est', 'unknown')}")
    
    if dry_run:
        print("\n[DRY RUN] Would execute command above")
        return
    
    print("\nStarting execution...\n")
    
    try:
        # Change to working directory and run command
        result = subprocess.run(
            command,
            shell=True,
            cwd=str(work_path),
            check=False
        )
        
        if result.returncode == 0:
            print(f"\n✓ Node '{node_id}' completed successfully")
        else:
            print(f"\n✗ Node '{node_id}' exited with code {result.returncode}")
            sys.exit(result.returncode)
            
    except Exception as e:
        print(f"\n✗ Error running node '{node_id}': {e}")
        sys.exit(1)


def show_status():
    """Show status of all pipelines."""
    nodes = load_nodes_csv()
    
    print("\n" + "="*80)
    print("PIPELINE STATUS OVERVIEW")
    print("="*80 + "\n")
    
    # Count by type
    by_type = {}
    by_time = {'fast': 0, 'medium': 0, 'slow': 0, 'very_slow': 0}
    rate_limited = 0
    parallel_safe = 0
    
    for node in nodes:
        node_type = node.get('type', 'unknown')
        by_type[node_type] = by_type.get(node_type, 0) + 1
        
        time_est = node.get('processing_time_est', '').lower()
        if time_est in by_time:
            by_time[time_est] += 1
        
        if node.get('rate_limited', '').lower() == 'yes':
            rate_limited += 1
        
        if node.get('n8n_parallel_safe', '').lower() == 'yes':
            parallel_safe += 1
    
    print("Pipeline Distribution by Type:")
    for node_type in sorted(by_type.keys()):
        print(f"  {node_type:20s}: {by_type[node_type]:3d} nodes")
    
    print(f"\nProcessing Time Distribution:")
    for time_cat in ['fast', 'medium', 'slow', 'very_slow']:
        print(f"  {time_cat:10s}: {by_time[time_cat]:3d} nodes")
    
    print(f"\nOther Statistics:")
    print(f"  Rate Limited:     {rate_limited}/{len(nodes)} nodes")
    print(f"  Parallel Safe:   {parallel_safe}/{len(nodes)} nodes")
    print(f"  Total Nodes:      {len(nodes)}")
    
    print("\n" + "="*80 + "\n")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'list':
        list_all_pipelines()
    
    elif command == 'info':
        if len(sys.argv) < 3:
            print("Usage: python manage_pipelines.py info <node_id>")
            sys.exit(1)
        show_node_info(sys.argv[2])
    
    elif command == 'run':
        if len(sys.argv) < 3:
            print("Usage: python manage_pipelines.py run <node_id> [--dry-run]")
            sys.exit(1)
        dry_run = '--dry-run' in sys.argv
        run_node(sys.argv[2], dry_run=dry_run)
    
    elif command == 'status':
        show_status()
    
    elif command == 'dependencies':
        if len(sys.argv) < 3:
            print("Usage: python manage_pipelines.py dependencies <node_id>")
            sys.exit(1)
        show_dependencies(sys.argv[2])
    
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == '__main__':
    main()

