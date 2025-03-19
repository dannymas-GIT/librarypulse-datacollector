import React from 'react';
import { useNavigate } from 'react-router-dom';
import Card from '../common/Card';
import Button from '../common/Button';

const SetupRequired: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <Card className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Setup Required
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Please complete the setup process to continue.
          </p>
        </div>
        <div className="mt-8 space-y-6">
          <Button
            onClick={() => navigate('/setup')}
            className="w-full"
          >
            Start Setup
          </Button>
        </div>
      </Card>
    </div>
  );
};

export default SetupRequired; 