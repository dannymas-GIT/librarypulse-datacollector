import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { AlertCircle, CheckCircle2, Loader } from 'lucide-react';

import authService from '../services/authService';

const EmailVerificationPage: React.FC = () => {
  const navigate = useNavigate();
  const { token } = useParams();
  const [verificationStatus, setVerificationStatus] = useState<'verifying' | 'success' | 'error'>('verifying');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const verifyMutation = useMutation({
    mutationFn: (token: string) => authService.verifyEmail(token),
    onSuccess: () => {
      setVerificationStatus('success');
      // Redirect to login after 3 seconds
      setTimeout(() => {
        navigate('/login');
      }, 3000);
    },
    onError: (error: Error) => {
      setVerificationStatus('error');
      setErrorMessage(error.message);
    },
  });

  useEffect(() => {
    if (token) {
      verifyMutation.mutate(token);
    } else {
      setVerificationStatus('error');
      setErrorMessage('Invalid verification link');
    }
  }, [token]);

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="flex justify-center">
          <img
            className="h-12 w-auto"
            src="/logo.svg"
            alt="Library Pulse Logo"
            onError={(e: React.SyntheticEvent<HTMLImageElement, Event>) => {
              e.currentTarget.src = 'https://via.placeholder.com/120x48?text=Library+Pulse';
            }}
          />
        </div>
        <h1 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Email Verification
        </h1>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white rounded-lg shadow-md p-8">
          {verificationStatus === 'verifying' && (
            <div className="text-center">
              <Loader className="animate-spin h-12 w-12 text-blue-500 mx-auto mb-4" />
              <h2 className="text-2xl font-bold mb-2">Verifying Your Email</h2>
              <p className="text-gray-600">
                Please wait while we verify your email address...
              </p>
            </div>
          )}

          {verificationStatus === 'success' && (
            <div className="text-center">
              <CheckCircle2 className="w-16 h-16 text-green-500 mx-auto mb-4" />
              <h2 className="text-2xl font-bold mb-2">Email Verified!</h2>
              <p className="text-gray-600 mb-4">
                Your email has been successfully verified. You can now log in to your account.
              </p>
              <p className="text-sm text-gray-500">
                Redirecting to login page...
              </p>
            </div>
          )}

          {verificationStatus === 'error' && (
            <div className="text-center">
              <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
              <h2 className="text-2xl font-bold mb-2">Verification Failed</h2>
              <p className="text-gray-600 mb-4">
                {errorMessage || 'There was an error verifying your email address.'}
              </p>
              <button
                onClick={() => navigate('/login')}
                className="text-blue-600 hover:text-blue-800 font-medium"
              >
                Return to Login
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default EmailVerificationPage; 