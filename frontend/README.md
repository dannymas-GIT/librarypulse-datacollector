# IMLS Library Pulse - Frontend

This is the frontend application for the IMLS Library Pulse project. It provides a user interface for searching, browsing, and analyzing Public Libraries Survey (PLS) data.

## Technology Stack

- **React 18+** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and development server
- **React Router** - Client-side routing
- **React Query** - Server state management
- **Tailwind CSS** - Utility-first CSS framework
- **Lucide React** - Icon library
- **React Hook Form** - Form handling
- **Zod** - Schema validation

## Development

### Prerequisites

- Node.js 18+
- npm or yarn

### Setup

1. Install dependencies:
   ```bash
   npm install
   # or
   yarn
   ```

2. Start the development server:
   ```bash
   npm run dev
   # or
   yarn dev
   ```

3. Open [http://localhost:5173](http://localhost:5173) in your browser.

### Building for Production

```bash
npm run build
# or
yarn build
```

The build artifacts will be stored in the `dist/` directory.

## Project Structure

```
frontend/
├── public/              # Static assets
├── src/
│   ├── assets/          # Images, fonts, etc.
│   ├── components/      # Reusable components
│   │   ├── ui/          # UI components
│   │   └── layout/      # Layout components
│   ├── hooks/           # Custom React hooks
│   ├── pages/           # Page components
│   ├── services/        # API services
│   ├── types/           # TypeScript type definitions
│   ├── utils/           # Utility functions
│   ├── App.tsx          # Main application component
│   ├── main.tsx         # Application entry point
│   └── index.css        # Global styles
├── index.html           # HTML template
├── package.json         # Dependencies and scripts
├── tsconfig.json        # TypeScript configuration
├── vite.config.ts       # Vite configuration
└── tailwind.config.js   # Tailwind CSS configuration
```

## Features

- **Dashboard** - Overview of library statistics
- **Libraries** - Search and browse libraries
- **Library Details** - Detailed information about a specific library
- **Statistics** - Summary statistics for libraries
- **Trends** - Visualize trends in library statistics over time
- **Comparison** - Compare multiple libraries across various metrics
- **Data Management** - Manage the PLS data available in the system

## API Integration

The frontend communicates with the backend API to fetch and display data. The API endpoints are defined in the `services` directory.

## License

[Add appropriate license information]

## Contributors

[Add contributor information] 