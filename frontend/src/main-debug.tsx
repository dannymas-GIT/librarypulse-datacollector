import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

import App from './App';
import './index.css';

// Error handling
window.addEventListener('error', (event) => {
  console.error('Global error caught:', event.error);
  
  // Create an error display element
  const errorDisplay = document.createElement('div');
  errorDisplay.style.position = 'fixed';
  errorDisplay.style.top = '0';
  errorDisplay.style.left = '0';
  errorDisplay.style.right = '0';
  errorDisplay.style.padding = '20px';
  errorDisplay.style.backgroundColor = '#fee2e2';
  errorDisplay.style.color = '#ef4444';
  errorDisplay.style.zIndex = '9999';
  errorDisplay.style.fontFamily = 'system-ui, sans-serif';
  
  errorDisplay.innerHTML = `
    <h3>Error Loading Application</h3>
    <p>${event.error?.message || 'Unknown error'}</p>
    <pre>${event.error?.stack || ''}</pre>
  `;
  
  document.body.appendChild(errorDisplay);
});

// Unhandled promise rejection handling
window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled promise rejection:', event.reason);
  
  // Create an error display element
  const errorDisplay = document.createElement('div');
  errorDisplay.style.position = 'fixed';
  errorDisplay.style.top = '0';
  errorDisplay.style.left = '0';
  errorDisplay.style.right = '0';
  errorDisplay.style.padding = '20px';
  errorDisplay.style.backgroundColor = '#fef3c7';
  errorDisplay.style.color = '#f59e0b';
  errorDisplay.style.zIndex = '9999';
  errorDisplay.style.fontFamily = 'system-ui, sans-serif';
  
  errorDisplay.innerHTML = `
    <h3>Unhandled Promise Rejection</h3>
    <p>${event.reason?.message || 'Unknown error'}</p>
    <pre>${event.reason?.stack || ''}</pre>
  `;
  
  document.body.appendChild(errorDisplay);
});

console.log('Starting application initialization...');

try {
  // Create a client for React Query with error logging
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        refetchOnWindowFocus: false,
        staleTime: 1000 * 60 * 5, // 5 minutes
        retry: false,
        onError: (error) => {
          console.error('React Query error:', error);
        }
      },
    },
  });

  console.log('QueryClient created successfully');

  // Get the root element
  const rootElement = document.getElementById('root');
  
  if (!rootElement) {
    throw new Error('Root element not found');
  }
  
  console.log('Root element found');

  // Create root and render app
  const root = ReactDOM.createRoot(rootElement);
  
  console.log('React root created successfully');
  
  // Wrap rendering in try/catch
  try {
    console.log('Rendering application...');
    
    root.render(
      <React.StrictMode>
        <QueryClientProvider client={queryClient}>
          <BrowserRouter>
            <App />
          </BrowserRouter>
          <ReactQueryDevtools initialIsOpen={false} />
        </QueryClientProvider>
      </React.StrictMode>,
    );
    
    console.log('Application rendered successfully');
  } catch (renderError) {
    console.error('Error rendering application:', renderError);
    
    // Render a fallback UI
    root.render(
      <div style={{ padding: '20px', fontFamily: 'system-ui, sans-serif' }}>
        <h1>Error Rendering Application</h1>
        <p>There was an error rendering the application:</p>
        <pre style={{ 
          backgroundColor: '#f8f8f8', 
          padding: '10px', 
          borderRadius: '4px',
          overflow: 'auto'
        }}>
          {renderError.message}
          {'\n'}
          {renderError.stack}
        </pre>
        <div style={{ marginTop: '20px' }}>
          <a href="/simple-app.html" style={{
            display: 'inline-block',
            padding: '10px 15px',
            backgroundColor: '#3b82f6',
            color: 'white',
            textDecoration: 'none',
            borderRadius: '4px',
            marginRight: '10px'
          }}>
            Try Simple App
          </a>
          <a href="/minimal-react.html" style={{
            display: 'inline-block',
            padding: '10px 15px',
            backgroundColor: '#3b82f6',
            color: 'white',
            textDecoration: 'none',
            borderRadius: '4px'
          }}>
            Try Minimal React App
          </a>
        </div>
      </div>
    );
  }
} catch (initError) {
  console.error('Error during application initialization:', initError);
  
  // Create a fallback directly in the DOM
  const rootElement = document.getElementById('root');
  if (rootElement) {
    rootElement.innerHTML = `
      <div style="padding: 20px; font-family: system-ui, sans-serif;">
        <h1>Error Initializing Application</h1>
        <p>There was an error initializing the application:</p>
        <pre style="background-color: #f8f8f8; padding: 10px; border-radius: 4px; overflow: auto;">
          ${initError.message}
          ${initError.stack || ''}
        </pre>
        <div style="margin-top: 20px;">
          <a href="/simple-app.html" style="display: inline-block; padding: 10px 15px; background-color: #3b82f6; color: white; text-decoration: none; border-radius: 4px; margin-right: 10px;">
            Try Simple App
          </a>
          <a href="/minimal-react.html" style="display: inline-block; padding: 10px 15px; background-color: #3b82f6; color: white; text-decoration: none; border-radius: 4px;">
            Try Minimal React App
          </a>
        </div>
      </div>
    `;
  }
} 