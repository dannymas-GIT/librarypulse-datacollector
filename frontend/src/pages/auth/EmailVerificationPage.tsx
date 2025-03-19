import React from 'react';
import { useSearchParams } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { api } from '@/lib/api';

export const EmailVerificationPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');

  const verifyMutation = useMutation({
    mutationFn: async () => {
      if (!token) throw new Error('No verification token provided');
      const response = await api.post('/api/v1/users/verify-email', { token });
      return response.data;
    },
  });

  React.useEffect(() => {
    if (token) {
      verifyMutation.mutate();
    }
  }, [token]);

  if (verifyMutation.isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="max-w-md w-full space-y-8 p-6">
          <h2 className="text-center text-3xl font-extrabold text-gray-900">
            Verifying your email...
          </h2>
        </div>
      </div>
    );
  }

  if (verifyMutation.isError) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="max-w-md w-full space-y-8 p-6">
          <h2 className="text-center text-3xl font-extrabold text-gray-900">
            Email Verification Failed
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            {verifyMutation.error instanceof Error
              ? verifyMutation.error.message
              : 'An error occurred during email verification.'}
          </p>
        </div>
      </div>
    );
  }

  if (verifyMutation.isSuccess) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="max-w-md w-full space-y-8 p-6">
          <h2 className="text-center text-3xl font-extrabold text-gray-900">
            Email Verified Successfully
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Your email has been verified. You can now log in to your account.
          </p>
          <div className="mt-6">
            <a
              href="/login"
              className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Go to Login
            </a>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8 p-6">
        <h2 className="text-center text-3xl font-extrabold text-gray-900">
          Invalid Verification Link
        </h2>
        <p className="mt-2 text-center text-sm text-gray-600">
          No verification token was provided. Please check your email for the verification link.
        </p>
      </div>
    </div>
  );
}; 