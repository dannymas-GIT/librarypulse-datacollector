import React from 'react';
import { Link } from 'react-router-dom';

const TermsPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-md p-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Terms and Conditions</h1>
          <p className="mt-2 text-gray-600">Last updated: March 17, 2025</p>
        </div>
        
        <div className="prose max-w-none">
          <h2>1. Acceptance of Terms</h2>
          <p>
            By accessing and using Library Pulse, you agree to be bound by these Terms and Conditions.
            If you do not agree with any part of these terms, please do not use our service.
          </p>
          
          <h2>2. Description of Service</h2>
          <p>
            Library Pulse provides analytics and visualization tools for public library data.
            Our service is designed to help library administrators, analysts, and stakeholders
            understand and optimize library performance and impact.
          </p>
          
          <h2>3. User Accounts</h2>
          <p>
            To access certain features of Library Pulse, you may be required to register for an account.
            You are responsible for maintaining the confidentiality of your account credentials
            and for all activities that occur under your account.
          </p>
          
          <h2>4. Data Usage</h2>
          <p>
            Library Pulse collects and processes public library data from official sources.
            We do not claim ownership of this data, but we do provide analysis and visualizations
            based on this information.
          </p>
          
          <h2>5. Privacy</h2>
          <p>
            We respect your privacy and are committed to protecting your personal information.
            Please review our Privacy Policy to understand how we collect, use, and safeguard your data.
          </p>
          
          <h2>6. Limitations of Liability</h2>
          <p>
            Library Pulse and its developers shall not be liable for any indirect, incidental,
            special, consequential, or punitive damages resulting from your use of or inability
            to use the service.
          </p>
          
          <h2>7. Changes to Terms</h2>
          <p>
            We reserve the right to modify these Terms and Conditions at any time.
            Continued use of Library Pulse following any changes constitutes your acceptance
            of the revised terms.
          </p>
        </div>
        
        <div className="mt-8 text-center">
          <Link to="/register" className="text-blue-600 hover:text-blue-800 font-medium">
            Back to Registration
          </Link>
        </div>
      </div>
    </div>
  );
};

export default TermsPage; 