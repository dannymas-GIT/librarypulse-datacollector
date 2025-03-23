import express from 'express';
import cors from 'cors';

const app = express();
app.use(cors());
app.use(express.json());

// Mock data
const mockData = {
  switch: {
    status: 'healthy',
    ports: [
      { id: 1, status: 'up', speed: '1Gbps', description: 'Library Network' },
      { id: 2, status: 'up', speed: '1Gbps', description: 'Public WiFi' },
      { id: 3, status: 'down', speed: '0', description: 'Management' }
    ],
    lastUpdate: new Date().toISOString()
  },
  backup: {
    status: 'completed',
    lastBackup: new Date().toISOString(),
    size: '1.2TB',
    jobs: [
      { id: 1, name: 'Daily Backup', status: 'success', completedAt: new Date().toISOString() },
      { id: 2, name: 'Weekly Backup', status: 'pending', scheduledFor: new Date().toISOString() }
    ]
  },
  sonicwall: {
    status: 'active',
    throughput: {
      incoming: '150Mbps',
      outgoing: '75Mbps'
    },
    threats: {
      blocked: 1250,
      lastDetected: new Date().toISOString(),
      type: 'malware'
    }
  }
};

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'healthy' });
});

// Switch endpoints
app.get('/api/switch/status', (req, res) => {
  res.json(mockData.switch);
});

app.get('/api/switch/ports', (req, res) => {
  res.json(mockData.switch.ports);
});

// Backup endpoints
app.get('/api/backup/status', (req, res) => {
  res.json(mockData.backup);
});

app.get('/api/backup/jobs', (req, res) => {
  res.json(mockData.backup.jobs);
});

// SonicWall endpoints
app.get('/api/sonicwall/status', (req, res) => {
  res.json(mockData.sonicwall);
});

app.get('/api/sonicwall/threats', (req, res) => {
  res.json(mockData.sonicwall.threats);
});

const port = process.env.PORT || 3000;
app.listen(port, () => {
  console.log(`Mock services running on port ${port}`);
}); 