# Data Pipeline Admin Interface

A Next.js-based admin interface for managing and monitoring the data pipeline processes. Features a clean, high-tech dark mode design optimized for data operations and monitoring.

## Features

- 🌙 **Dark Mode First**: Optimized for comfortable extended use
- 📊 **Real-time Flow Visualization**: Interactive pipeline flow charts
- 🎛️ **Node Management**: Control individual pipeline processes
- 📝 **TODO Management**: Team collaboration on pipeline tasks
- ▶️ **Remote Execution**: Run Python processes through Flask integration
- 📱 **Responsive Layout**: Flexible column, full-width, and floating layouts
- 🎨 **Space-flight UX**: Minimalist design with curved borders and vibrant accents

## Quick Start

```bash
cd admin
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the interface.

## Architecture

### Components

- **NodesList**: Displays pipeline nodes from `nodes.csv`
- **FlowChart**: Renders real-time flow diagram from `nodes.json`
- **NodeDetailPanel**: Controls and metadata for individual nodes
- **DarkModeToggle**: Theme switching with bean-shaped toggle

### Layout Modes

1. **Column Layout** (30% sidebar): Default view with list on left
2. **Full Width Layout**: List positioned below main content
3. **Floating Layout**: List in modal popup overlay

### API Endpoints

- `GET /api/nodes` - Fetch all pipeline nodes
- `POST /api/nodes/update` - Update node TODOs
- `POST /api/nodes/run` - Execute Python processes

## Integration

### Flask Backend

The interface connects to a Flask server for:
- Executing Python pipeline processes
- Managing node configurations
- Updating CSV data

### Embeddable Widget

Use the standalone `NodesCSVParser` utility to embed node lists in any application:

```javascript
import { NodesCSVParser } from './utils/csvParser.js';

const parser = new NodesCSVParser(csvContent);
const widgetHTML = parser.generateWidget('my-container', {
  showSearch: true,
  showFilters: true,
  theme: 'dark'
});

document.getElementById('target').innerHTML = widgetHTML;
```

## Styling

Built with Tailwind CSS using a custom space-flight inspired theme:

- **Background**: Dark grays (#0f0f0f, #1a1a1a)
- **Accents**: Cyan (#06b6d4), Blue (#3b82f6), Emerald (#10b981)
- **Borders**: Curved corners (40px/18px) with directional flows
- **Typography**: Strong hierarchy with monospace accents

## File Structure

```
admin/
├── components/
│   ├── DarkModeToggle.js
│   ├── NodesList.js
│   ├── FlowChart.js
│   └── NodeDetailPanel.js
├── pages/
│   ├── index.js
│   ├── _app.js
│   └── api/
│       ├── nodes.js
│       └── nodes/
│           ├── update.js
│           └── run.js
├── styles/
│   └── globals.css
├── utils/
│   └── csvParser.js
└── README.md
```

## Data Sources

The interface reads from:
- `../nodes.csv` - Pipeline node definitions
- `../nodes.json` - Flow chart connections and positioning

## Security Notes

- API endpoints validate input parameters
- File paths are resolved safely
- Command execution is sandboxed with timeouts
- Working directories are verified before execution