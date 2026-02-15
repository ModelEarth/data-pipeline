import fs from 'fs';
import path from 'path';

function sanitizeWorkingDirectory(input) {
  if (!input) return '';
  return String(input)
    .trim()
    .replace(/\\/g, '/')
    .replace(/^\/+/, '')
    .replace(/^(\.\.\/)+/, '')
    .replace(/\.\.\//g, '');
}

export default function handler(req, res) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', ['POST']);
    return res.status(405).end(`Method ${req.method} Not Allowed`);
  }

  try {
    const { working_directory, filename = 'config.yaml', content } = req.body || {};
    if (!working_directory) {
      return res.status(400).json({
        success: false,
        error: 'working_directory is required',
      });
    }

    if (filename !== 'config.yaml') {
      return res.status(400).json({
        success: false,
        error: 'Only config.yaml is allowed',
      });
    }

    if (typeof content !== 'string') {
      return res.status(400).json({
        success: false,
        error: 'content must be a string',
      });
    }

    const basePath = path.resolve(process.cwd(), '..', '..'); // webroot
    const safeDir = sanitizeWorkingDirectory(working_directory);
    const targetDir = path.resolve(basePath, safeDir);
    if (!targetDir.startsWith(basePath)) {
      return res.status(400).json({
        success: false,
        error: 'Invalid working_directory path',
      });
    }

    if (!fs.existsSync(targetDir) || !fs.statSync(targetDir).isDirectory()) {
      return res.status(400).json({
        success: false,
        error: `Working directory does not exist: ${targetDir}`,
      });
    }

    const targetFile = path.resolve(targetDir, filename);
    if (!targetFile.startsWith(targetDir)) {
      return res.status(400).json({
        success: false,
        error: 'Invalid target file path',
      });
    }

    fs.writeFileSync(targetFile, content, 'utf-8');
    const relativePath = path.relative(basePath, targetFile).replace(/\\/g, '/');

    return res.status(200).json({
      success: true,
      message: 'config.yaml saved',
      path: relativePath,
    });
  } catch (error) {
    return res.status(500).json({
      success: false,
      error: error.message || 'Failed to save config.yaml',
    });
  }
}
