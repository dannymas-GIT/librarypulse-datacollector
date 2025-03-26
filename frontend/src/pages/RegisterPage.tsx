import React from 'react';
import { Link } from 'react-router-dom';
import RegisterForm from '../components/auth/RegisterForm';

const RegisterPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="flex justify-center">
          <Link to="/">
            <img
              className="h-12 w-auto mb-4"
              src="/logo.svg"
              alt="Library Lens Logo"
              onError={(e) => {
                e.currentTarget.src = 'https://via.placeholder.com/120x48?text=Library+Lens';
              }}
            />
          </Link>
        </div>
        <h2 className="mt-2 text-center text-2xl font-bold tracking-tight text-gray-900">
          Library Lens
        </h2>
        <p className="mt-2 text-center text-sm text-gray-600">
          Create an account to get started
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <RegisterForm />
      </div>
    </div>
  );
};

export default RegisterPage; 