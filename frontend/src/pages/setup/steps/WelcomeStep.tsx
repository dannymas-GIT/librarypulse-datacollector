import React from 'react';
import { Button } from '@/components/ui/Button';

interface WelcomeStepProps {
  onContinue: () => void;
}

const WelcomeStep: React.FC<WelcomeStepProps> = ({ onContinue }) => {
  return (
    <div className="text-center">
      <h2 className="text-2xl font-bold mb-4">Welcome to Library Pulse</h2>
      <p className="text-gray-600 mb-6">
        Library Pulse helps you track and analyze library statistics and performance metrics.
        Let's set up your account by selecting your library and preferences.
      </p>
      <p className="text-gray-600 mb-8">
        This quick setup will guide you through selecting your primary library and
        comparison libraries to get the most out of Library Pulse.
      </p>
      <Button onClick={onContinue} className="px-6 py-2">
        Get Started
      </Button>
    </div>
  );
};

export default WelcomeStep; 