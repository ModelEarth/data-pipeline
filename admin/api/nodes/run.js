import { exec } from 'child_process';
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

export default function handler(req, res) {
  if (req.method === 'POST') {
    try {
      const { node_id, command, working_directory } = req.body;

      if (!node_id || !command) {
        return res.status(400).json({
          success: false,
          error: 'node_id and command are required',
        });
      }

      const normalizedDir = normalizeWorkingDirectory(working_directory);
      const workingPath = path.join(process.cwd(), '..', normalizedDir || '');

      if (!fs.existsSync(workingPath)) {
        return res.status(400).json({
          success: false,
          error: `Working directory does not exist: ${workingPath}`,
        });
      }

      const execOptions = {
        cwd: workingPath,
        timeout: 30000,
        maxBuffer: 1024 * 1024,
      };

      exec(command, execOptions, (error, stdout, stderr) => {
        if (error) {
          console.error(`Execution error for ${node_id}:`, error);
          return res.status(500).json({
            success: false,
            error: error.message,
            stderr,
            node_id,
          });
        }

        console.log(`Successfully executed ${node_id}: ${command}`);

        res.status(200).json({
          success: true,
          output: stdout,
          stderr,
          node_id,
          command,
          working_directory: normalizedDir,
        });
      });
    } catch (error) {
      console.error('Error running node:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to execute node command',
      });
    }
  } else {
    res.setHeader('Allow', ['POST']);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}
