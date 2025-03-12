import React from 'react';
import { CheckCircle } from 'lucide-react';
import { Button } from '@/components/ui/Button';

interface SetupCompleteStepProps {
  onFinish: () => void;
}

const SetupCompleteStep: React.FC<SetupCompleteStepProps> = ({ onFinish }) => {
  return (
    <div className="text-center">
      <div className="flex justify-center mb-6">
        <CheckCircle className="h-16 w-16 text-green-500" />
      </div>
      <h2 className="text-2xl font-bold mb-4">Setup Complete!</h2>
      <p className="text-gray-600 mb-6">
        Your Library Pulse account is now set up and ready to use.
        You can now access your dashboard and start exploring your library data.
      </p>
      <p className="text-gray-600 mb-8">
        You can always add or remove libraries from your profile in the Data Management section.
      </p>
      <Button onClick={onFinish} className="px-6 py-2">
        Go to Dashboard
      </Button>
    </div>
  );
};

export default SetupCompleteStep; 