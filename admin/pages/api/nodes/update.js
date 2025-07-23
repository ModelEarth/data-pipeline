import fs from 'fs';
import path from 'path';
import { parse } from 'csv-parse/sync';
import { stringify } from 'csv-stringify/sync';

export default function handler(req, res) {
  if (req.method === 'POST') {
    try {
      const { node_id, todos } = req.body;
      
      if (!node_id) {
        return res.status(400).json({ error: 'node_id is required' });
      }

      // Read the current CSV file
      const csvPath = path.join(process.cwd(), '..', 'nodes.csv');
      const csvContent = fs.readFileSync(csvPath, 'utf-8');
      
      // Parse CSV content
      const records = parse(csvContent, {
        columns: true,
        skip_empty_lines: true
      });

      // Find and update the node
      const nodeIndex = records.findIndex(record => record.node_id === node_id);
      
      if (nodeIndex === -1) {
        return res.status(404).json({ error: 'Node not found' });
      }

      // Add todos field if it doesn't exist
      if (!records[nodeIndex].hasOwnProperty('todos')) {
        records[nodeIndex].todos = '';
      }

      records[nodeIndex].todos = todos || '';

      // Convert back to CSV
      const updatedCsv = stringify(records, {
        header: true,
        columns: Object.keys(records[0])
      });

      // Write back to file
      fs.writeFileSync(csvPath, updatedCsv, 'utf-8');

      res.status(200).json({ 
        success: true, 
        message: 'Node updated successfully',
        node: records[nodeIndex]
      });
    } catch (error) {
      console.error('Error updating node:', error);
      res.status(500).json({ error: 'Failed to update node' });
    }
  } else {
    res.setHeader('Allow', ['POST']);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}