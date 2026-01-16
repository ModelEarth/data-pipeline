import { useState } from 'react';
import { checkFlaskAvailability, getFlaskRunEndpoint } from '../utils/flaskCheck';

export default function NodeDetailPanel({ node, onUpdateNode, onRunNode, flaskAvailable }) {
  const [todos, setTodos] = useState(node?.todos || '');
  const [newTodo, setNewTodo] = useState('');
  const [isRunning, setIsRunning] = useState(false);
  const [runResult, setRunResult] = useState(null);

  if (!node) {
    return (
      <div className="panel p-8 flex items-center justify-center text-center">
        <div>
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gray-700 flex items-center justify-center">
            <span className="text-2xl">🔧</span>
          </div>
          <h3 className="text-lg font-medium text-gray-100 mb-2">Select a Node</h3>
          <p className="text-muted">Choose a pipeline node from the list to view details and controls</p>
        </div>
      </div>
    );
  }

  const handleTodosUpdate = async () => {
    try {
      const basePath = process.env.NODE_ENV === 'production' ? '/data-pipeline/admin' : '';
      const response = await fetch(`${basePath}/api/nodes/update`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          node_id: node.node_id,
          todos: todos
        })
      });

      if (response.ok) {
        onUpdateNode?.({ ...node, todos });
        alert('TODOs updated successfully!');
      } else {
        alert('Failed to update TODOs');
      }
    } catch (error) {
      console.error('Error updating TODOs:', error);
      alert('Error updating TODOs');
    }
  };

  const handleRunNode = async () => {
    if (!node.python_cmds) {
      alert('No Python command available for this node');
      return;
    }

    // Check if Flask is available, otherwise fallback to Next.js API
    const useFlask = flaskAvailable === true;
    const apiUrl = useFlask 
      ? getFlaskRunEndpoint()
      : (process.env.NODE_ENV === 'production' ? '/data-pipeline/admin' : '') + '/api/nodes/run';

    setIsRunning(true);
    setRunResult(null);

    try {
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          node_id: node.node_id,
          command: node.python_cmds,
          working_directory: node.link
        })
      });

      const result = await response.json();
      setRunResult(result);
      onRunNode?.(node, result);
    } catch (error) {
      console.error('Error running node:', error);
      setRunResult({ success: false, error: error.message });
    } finally {
      setIsRunning(false);
    }
  };

  const getStatusColor = () => {
    if (isRunning) return 'text-orange-400';
    if (runResult?.success) return 'text-emerald-400';
    if (runResult?.success === false) return 'text-red-500';
    return 'text-gray-400';
  };

  const getTypeIcon = (type) => {
    const icons = {
      'data_fetcher': '📥',
      'data_processor': '⚙️',
      'data_aggregator': '📊',
      'ml_processor': '🤖',
      'api_fetcher': '🌐',
      'data_cleaner': '🧹',
      'data_merger': '🔗',
      'structure_creator': '📁',
      'batch_processor': '⚡'
    };
    return icons[type] || '🔧';
  };

  return (
    <div className="panel space-y-6 select-text" style={{padding: '29px'}}>
      {/* Header */}
      <div className="border-b border-gray-700 pb-4">
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-3">
            <span className="text-2xl">{getTypeIcon(node.type)}</span>
            <div>
              <h2 className="text-xl font-bold text-gray-100">{node.name}</h2>
              <p className="text-sm font-mono text-cyan-400">{node.node_id}</p>
            </div>
          </div>
          <span className={`text-sm font-medium px-3 py-1 rounded-full border ${
            node.n8n_parallel_safe === 'yes' 
              ? 'text-emerald-400 border-emerald-400/30 bg-emerald-400/10'
              : 'text-orange-400 border-orange-400/30 bg-orange-400/10'
          }`}>
            {node.n8n_parallel_safe === 'yes' ? 'Parallel Safe' : 'Sequential Only'}
          </span>
        </div>
        <p className="text-muted">{node.description}</p>
      </div>

      {/* Details Grid */}
      <div className="grid gap-4" style={{ gridTemplateColumns: 'minmax(110px, 1fr) 2fr' }}>
        <div className="space-y-3">
          <div>
            <label className="block text-sm font-medium text-gray-100 mb-1">Processing Time</label>
            <div className="flex items-center gap-2">
              <span className="text-sm bg-gray-700 px-3 py-1 rounded-lg">
                {node.processing_time_est}
              </span>
              {node.rate_limited === 'yes' && (
                <span className="text-xs text-orange-400">⚠️ Rate Limited</span>
              )}
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-100 mb-1">Folder Size</label>
            <span className="text-sm bg-gray-700 px-3 py-1 rounded-lg">
              {node.folder_size}
            </span>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-100 mb-1">Dependencies</label>
            <div className="flex flex-wrap gap-1">
              {node.dependencies?.split(',').map((dep, index) => (
                <span key={index} className="text-xs bg-blue-500/10 text-blue-400 px-2 py-1 rounded">
                  {dep.trim()}
                </span>
              ))}
            </div>
          </div>
        </div>

        <div className="space-y-3">
          <div>
            <label className="block text-sm font-medium text-gray-100 mb-1">Python Path</label>
            <span className="text-sm bg-gray-700 px-3 py-1 rounded-lg font-mono">
              {node.link}
            </span>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-100 mb-1">Output Path</label>
            <span className="text-sm bg-gray-700 px-3 py-1 rounded-lg font-mono">
              {node.output_path?.replace(/^(\.\.\/)+/, '')}
            </span>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-100 mb-1">Data Sources</label>
            <span className="text-sm text-muted">
              {node.data_sources}
            </span>
          </div>

          {node.api_keys_required && node.api_keys_required !== 'none' && (
            <div>
              <label className="block text-sm font-medium text-gray-100 mb-1">API Keys Required</label>
              <span className="text-sm text-orange-400">
                {node.api_keys_required}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Command Section */}
      {node.python_cmds && (
        <div>
          <label className="block text-sm font-medium text-gray-100 mb-2">Python Command</label>
          <div className="bg-gray-700 rounded-lg p-3 mb-3">
            <code className="text-sm font-mono text-cyan-400">{node.python_cmds}</code>
          </div>
          
          {flaskAvailable === false && (
            <div className="mb-3 p-3 bg-orange-500/10 border border-orange-500/30 rounded-lg">
              <p className="text-sm text-orange-300 light:text-orange-700">
                ⚠️ Flask server not available. Using Next.js API fallback.
              </p>
              <a 
                href="/cloud/run/" 
                target="_blank"
                className="text-sm text-blue-400 hover:text-blue-300 underline mt-1 inline-block"
              >
                View setup instructions →
              </a>
            </div>
          )}
          
          <div className="flex items-center gap-3">
            <button
              onClick={handleRunNode}
              disabled={isRunning || (node.run_process_available && node.run_process_available.toLowerCase() === 'no')}
              className={`btn-primary ${isRunning ? 'opacity-50 cursor-not-allowed' : ''} ${node.run_process_available && node.run_process_available.toLowerCase() === 'no' ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              {isRunning ? '🔄 Running...' : '▶️ Run Process'}
            </button>
            
            <span className={`text-sm ${getStatusColor()}`}>
              {isRunning && 'Running...'}
              {runResult?.success === true && '✅ Success'}
              {runResult?.success === false && '❌ Failed'}
            </span>
          </div>
          
          {flaskAvailable === true && (
            <div className="mt-2 text-xs text-green-400">
              ✓ Using Flask server (port 5001)
            </div>
          )}
        </div>
      )}

      {/* Run Result */}
      {runResult && (
        <div className={`rounded-lg p-4 ${
          runResult.success 
            ? 'bg-emerald-500/10 border border-emerald-500/30'
            : 'bg-red-500/10 border border-red-500/30'
        }`}>
          <h4 className="font-medium mb-2">Execution Result:</h4>
          <pre className="text-sm font-mono overflow-auto max-h-32">
            {runResult.output || runResult.stderr || runResult.error}
          </pre>
        </div>
      )}

      {/* TODOs Section */}
      <div>
        <label className="block text-sm font-medium text-gray-100 mb-2">Team TODOs</label>
        <textarea
          value={todos}
          onChange={(e) => setTodos(e.target.value)}
          className="w-full h-24 bg-gray-700 border border-gray-600 rounded-lg p-3 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-500/50 text-gray-100"
          placeholder=""
        />
        <button
          onClick={handleTodosUpdate}
          className="btn-accent mt-2"
        >
          💾 Update TODOs
        </button>
      </div>

      {/* New TODO Input Form */}
      <div className="border-t border-gray-700 pt-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={newTodo}
            onChange={(e) => setNewTodo(e.target.value)}
            className="flex-1 bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/50 text-gray-100"
            placeholder="Add new TODO item..."
            onKeyPress={(e) => {
              if (e.key === 'Enter' && newTodo.trim()) {
                const updatedTodos = todos ? `${todos}\n- ${newTodo.trim()}` : `- ${newTodo.trim()}`;
                setTodos(updatedTodos);
                setNewTodo('');
              }
            }}
          />
          <button
            onClick={() => {
              if (newTodo.trim()) {
                const updatedTodos = todos ? `${todos}\n- ${newTodo.trim()}` : `- ${newTodo.trim()}`;
                setTodos(updatedTodos);
                setNewTodo('');
              }
            }}
            className="btn-accent px-4"
            disabled={!newTodo.trim()}
          >
            Add
          </button>
        </div>
      </div>
    </div>
  );
}