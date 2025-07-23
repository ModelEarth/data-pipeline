import { exec } from 'child_process';
import path from 'path';
import fs from 'fs';

export default function handler(req, res) {
  if (req.method === 'POST') {
    try {
      const { node_id, command, working_directory } = req.body;
      
      if (!node_id || !command) {
        return res.status(400).json({ 
          success: false, 
          error: 'node_id and command are required' 
        });
      }

      // Construct the full path to the working directory
      const workingPath = path.join(process.cwd(), '..', working_directory || '');
      
      // Verify the working directory exists
      if (!fs.existsSync(workingPath)) {
        return res.status(400).json({
          success: false,
          error: `Working directory does not exist: ${workingPath}`
        });
      }

      // Execute the command
      const execOptions = {
        cwd: workingPath,
        timeout: 30000, // 30 second timeout
        maxBuffer: 1024 * 1024 // 1MB buffer
      };

      exec(command, execOptions, (error, stdout, stderr) => {
        if (error) {
          console.error(`Execution error for ${node_id}:`, error);
          return res.status(500).json({
            success: false,
            error: error.message,
            stderr: stderr,
            node_id: node_id
          });
        }

        // Log the execution
        console.log(`Successfully executed ${node_id}: ${command}`);
        
        res.status(200).json({
          success: true,
          output: stdout,
          stderr: stderr,
          node_id: node_id,
          command: command,
          working_directory: working_directory
        });
      });

    } catch (error) {
      console.error('Error running node:', error);
      res.status(500).json({ 
        success: false, 
        error: 'Failed to execute node command' 
      });
    }
  } else {
    res.setHeader('Allow', ['POST']);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}