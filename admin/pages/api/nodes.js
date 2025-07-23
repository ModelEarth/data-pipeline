import fs from 'fs';
import path from 'path';
import { parse } from 'csv-parse/sync';

export default function handler(req, res) {
  if (req.method === 'GET') {
    try {
      // Read the nodes.csv file from the project root
      const csvPath = path.join(process.cwd(), '..', 'nodes.csv');
      const csvContent = fs.readFileSync(csvPath, 'utf-8');
      
      // Parse CSV content
      const records = parse(csvContent, {
        columns: true,
        skip_empty_lines: true
      });

      res.status(200).json(records);
    } catch (error) {
      console.error('Error reading nodes.csv:', error);
      res.status(500).json({ error: 'Failed to load nodes data' });
    }
  } else {
    res.setHeader('Allow', ['GET']);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}