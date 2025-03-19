import React from 'react';
import { Link } from 'react-router-dom';
import { BarChart, BookText, TrendingUp as TrendingUpIcon, Users } from 'lucide-react';

const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      <div className="container mx-auto px-4 py-8">
        <header className="flex justify-between items-center mb-16">
          <div className="flex items-center">
            <img
              src="/logo.svg"
              alt="Library Pulse Logo"
              className="h-10 w-auto"
              onError={(e: React.SyntheticEvent<HTMLImageElement>) => {
                e.currentTarget.src = 'https://via.placeholder.com/40x40?text=LP';
              }}
            />
            <h1 className="text-2xl font-bold ml-2 text-blue-800">Library Pulse</h1>
          </div>
          <div className="space-x-4">
            <Link
              to="/login"
              className="px-4 py-2 text-blue-600 hover:text-blue-800 font-medium"
            >
              Log In
            </Link>
            <Link
              to="/register"
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 font-medium"
            >
              Sign Up
            </Link>
          </div>
        </header>
        
        <main>
          <div className="max-w-4xl mx-auto text-center mb-16">
            <h2 className="text-4xl font-bold mb-6 text-gray-900">
              Unlock the Power of Library Data
            </h2>
            <p className="text-xl text-gray-600 mb-8">
              Library Pulse helps you visualize, analyze, and leverage your library's statistics 
              to make data-driven decisions and demonstrate your impact.
            </p>
            <Link
              to="/register"
              className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-lg font-medium"
            >
              Get Started
            </Link>
          </div>
          
          {/* Feature highlights */}
          <div className="grid md:grid-cols-3 gap-8 mb-16">
            <div className="bg-white p-6 rounded-lg shadow-md">
              <div className="flex justify-center mb-4">
                <BarChart className="h-12 w-12 text-blue-500" />
              </div>
              <h3 className="text-xl font-semibold mb-3 text-center text-gray-900">
                Visualize Your Data
              </h3>
              <p className="text-gray-600 text-center">
                Interactive dashboards and charts that bring your library statistics to life.
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-md">
              <div className="flex justify-center mb-4">
                <Users className="h-12 w-12 text-blue-500" />
              </div>
              <h3 className="text-xl font-semibold mb-3 text-center text-gray-900">
                Compare & Benchmark
              </h3>
              <p className="text-gray-600 text-center">
                See how your library compares to others of similar size and demographics.
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-md">
              <div className="flex justify-center mb-4">
                <TrendingUpIcon className="h-12 w-12 text-blue-500" />
              </div>
              <h3 className="text-xl font-semibold mb-3 text-center text-gray-900">
                Track Trends
              </h3>
              <p className="text-gray-600 text-center">
                Monitor changes over time and identify patterns in your library's performance.
              </p>
            </div>
          </div>
          
          {/* How it works section */}
          <div className="max-w-4xl mx-auto mb-16">
            <h2 className="text-3xl font-bold mb-8 text-center text-gray-900">
              How Library Pulse Works
            </h2>
            <div className="grid md:grid-cols-3 gap-8">
              <div className="text-center">
                <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl font-bold text-blue-600">1</span>
                </div>
                <h3 className="text-lg font-semibold mb-2">Create an Account</h3>
                <p className="text-gray-600">
                  Sign up and set up your library profile in minutes.
                </p>
              </div>
              <div className="text-center">
                <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl font-bold text-blue-600">2</span>
                </div>
                <h3 className="text-lg font-semibold mb-2">Select Your Library</h3>
                <p className="text-gray-600">
                  Choose your primary library and any comparison libraries.
                </p>
              </div>
              <div className="text-center">
                <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl font-bold text-blue-600">3</span>
                </div>
                <h3 className="text-lg font-semibold mb-2">Explore Your Data</h3>
                <p className="text-gray-600">
                  Access powerful visualizations and insights about your library.
                </p>
              </div>
            </div>
          </div>
          
          {/* CTA section */}
          <div className="bg-blue-600 rounded-lg p-8 text-center mb-16">
            <h2 className="text-2xl font-bold mb-4 text-white">
              Ready to transform your library data?
            </h2>
            <p className="text-blue-100 mb-6 max-w-2xl mx-auto">
              Join thousands of libraries using Library Pulse to make data-driven decisions
              and demonstrate their impact in their communities.
            </p>
            <Link
              to="/register"
              className="px-6 py-3 bg-white text-blue-600 rounded-md hover:bg-blue-50 font-medium"
            >
              Create Your Free Account
            </Link>
          </div>
        </main>
        
        <footer className="border-t border-gray-200 pt-8 pb-12">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="mb-4 md:mb-0">
              <p className="text-sm text-gray-500">
                &copy; {new Date().getFullYear()} Library Pulse. All rights reserved.
              </p>
            </div>
            <div className="flex space-x-6">
              <Link to="/terms" className="text-sm text-gray-500 hover:text-gray-700">
                Terms of Service
              </Link>
              <Link to="/privacy" className="text-sm text-gray-500 hover:text-gray-700">
                Privacy Policy
              </Link>
              <Link to="/contact" className="text-sm text-gray-500 hover:text-gray-700">
                Contact Us
              </Link>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
};

export default LandingPage; 