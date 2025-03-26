import React from 'react';
import { Card } from '@/components/common';

const TermsPage: React.FC = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <Card>
        <h1 className="text-3xl font-bold mb-6">Terms of Service</h1>
        <div className="prose max-w-none">
          <p className="mb-4">
            Welcome to Library Lens. By using this application, you agree to these terms.
          </p>
          <h2 className="text-2xl font-semibold mt-6 mb-4">1. Acceptance of Terms</h2>
          <p className="mb-4">
            By accessing and using Library Lens, you accept and agree to be bound by the terms and conditions of this agreement.
          </p>
          <h2 className="text-2xl font-semibold mt-6 mb-4">2. Use License</h2>
          <p className="mb-4">
            Permission is granted to temporarily access Library Lens for personal, non-commercial use only.
          </p>
          <h2 className="text-2xl font-semibold mt-6 mb-4">3. Disclaimer</h2>
          <p className="mb-4">
            The materials on Library Lens are provided on an 'as is' basis. Library Lens makes no warranties, expressed or implied, and hereby disclaims and negates all other warranties including, without limitation, implied warranties or conditions of merchantability, fitness for a particular purpose, or non-infringement of intellectual property or other violation of rights.
          </p>
        </div>
      </Card>
    </div>
  );
};

export default TermsPage; 