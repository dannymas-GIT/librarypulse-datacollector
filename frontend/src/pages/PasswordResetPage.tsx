import React from 'react';
import { Link } from 'react-router-dom';
import PasswordResetForm from '../components/auth/PasswordResetForm';

const PasswordResetPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="flex justify-center">
          <Link to="/">
            <img
              className="h-12 w-auto"
              src="/logo.svg"
              alt="Library Lens Logo"
              onError={(e) => {
                e.currentTarget.src = 'https://via.placeholder.com/120x48?text=Library+Lens';
              }}
            />
          </Link>
        </div>
        <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Library Lens
        </h2>
        <p className="mt-2 text-center text-sm text-gray-600">
          Enter your email to reset your password
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <PasswordResetForm />
      </div>
    </div>
  );
};

export default PasswordResetPage; 