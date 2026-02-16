import { spawn } from 'child_process';
import path from 'path';
import fs from 'fs';

function normalizeWorkingDirectory(input) {
  if (!input) return '';
  return String(input)
    .trim()
    .replace(/^(\.\.\/)+/, '')
    .replace(/^\/+/, '')
    .replace(/^data-pipeline\//, '');
}

function toCliValue(value) {
  if (value === null || value === undefined) return '';
  return String(value);
}

export default function handler(req, res) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', ['POST']);
    return res.status(405).end(`Method ${req.method} Not Allowed`);
  }

  try {
    const { original_node_id, row_updates } = req.body || {};
    if (!row_updates || typeof row_updates !== 'object') {
      return res.status(400).json({
        success: false,
        error: 'row_updates object is required',
      });
    }

    const nextNodeId = String(row_updates.node_id || '').trim();
    if (!nextNodeId) {
      return res.status(400).json({
        success: false,
        error: 'row_updates.node_id is required',
      });
    }

    const normalizedDir = normalizeWorkingDirectory('data-pipeline/admin/add');
    const workingPath = path.join(process.cwd(), '..', normalizedDir);
    if (!fs.existsSync(workingPath)) {
      return res.status(400).json({
        success: false,
        error: `Working directory does not exist: ${workingPath}`,
      });
    }

    const args = [
      'node.py',
      '--manual-row-update',
      'true',
      '--nodes-csv',
      '../../nodes.csv',
      '--node-id',
      nextNodeId,
      '--original-node-id',
      String(original_node_id || nextNodeId),
    ];

    Object.entries(row_updates).forEach(([key, value]) => {
      if (!key || key === 'node_id') return;
      args.push(`--${String(key).replace(/_/g, '-')}`);
      args.push(toCliValue(value));
    });

    const py = spawn('python3', args, {
      cwd: workingPath,
      timeout: 30000,
      stdio: ['ignore', 'pipe', 'pipe'],
    });

    let stdout = '';
    let stderr = '';
    py.stdout.on('data', (chunk) => {
      stdout += chunk.toString();
    });
    py.stderr.on('data', (chunk) => {
      stderr += chunk.toString();
    });

    py.on('close', (code) => {
      if (code !== 0) {
        return res.status(500).json({
          success: false,
          error: stderr.trim() || stdout.trim() || `node.py exited with code ${code}`,
          stderr,
          output: stdout,
        });
      }
      return res.status(200).json({
        success: true,
        node_id: nextNodeId,
        output: stdout,
        stderr,
      });
    });

    py.on('error', (error) => {
      return res.status(500).json({
        success: false,
        error: error.message || 'Failed to execute node.py',
      });
    });
  } catch (error) {
    return res.status(500).json({
      success: false,
      error: error.message || 'Failed to save node row',
    });
  }
}

