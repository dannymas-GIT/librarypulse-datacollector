import React from 'react';
import { Link } from 'react-router-dom';
import LoginForm from '../components/auth/LoginForm';

const LoginPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="flex justify-center">
          <Link to="/" className="flex items-center">
            <img
              className="h-12 w-auto"
              src="/logo.svg"
              alt="Library Lens Logo"
            />
          </Link>
        </div>
        <h1 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Library Lens
        </h1>
        <p className="mt-2 text-center text-sm text-gray-600">
          Sign in to access your library dashboard
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <LoginForm />
      </div>
    </div>
  );
};

export default LoginPage; 