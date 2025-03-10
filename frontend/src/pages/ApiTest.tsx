import React, { useState, useEffect } from 'react';
import axios from 'axios';

const ApiTest: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  const testApi = async () => {
    setLoading(true);
    setError(null);
    
    try {
      console.log('Testing API connection...');
      const response = await axios.get('http://localhost:8000/api/historical/summary');
      console.log('API response:', response.data);
      setData(response.data);
    } catch (err: any) {
      console.error('API error:', err);
      setError(err.message || 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">API Connection Test</h1>
      
      <button 
        className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded mb-4"
        onClick={testApi}
        disabled={loading}
      >
        Test API Connection
      </button>
      
      {loading && <p className="text-gray-500">Loading...</p>}
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          <p><strong>Error:</strong> {error}</p>
        </div>
      )}
      
      {data && (
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
          <p><strong>API Connection Successful!</strong></p>
          <pre className="mt-2 bg-gray-100 p-2 rounded overflow-auto">
            {JSON.stringify(data, null, 2)}
          </pre>
        </div>
      )}
      
      <div className="mt-8">
        <h2 className="text-xl font-bold mb-2">Troubleshooting</h2>
        <ol className="list-decimal list-inside space-y-2">
          <li>Make sure the backend API server is running: <code>cd backend && python -m api.main</code></li>
          <li>Check for CORS issues in browser console (F12)</li>
          <li>Verify network connectivity and firewall settings</li>
          <li>Ensure the API endpoint URL is correct</li>
        </ol>
      </div>
    </div>
  );
};

export default ApiTest; 