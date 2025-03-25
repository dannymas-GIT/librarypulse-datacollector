import React from 'react';
import { Link } from 'react-router-dom';
import { BookOpen, TrendingUp, Users, Database, PieChart, LineChart, ArrowRight } from 'lucide-react';

export const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-16">
        <div className="text-center">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            Welcome to <span className="text-blue-600">LibraryPulse</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Your comprehensive library data collection and analysis platform. 
            Turn public library data into actionable insights for decision-makers.
          </p>
          <div className="space-x-4">
            <Link
              to="/login"
              className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors"
            >
              Sign In
            </Link>
            <Link
              to="/register"
              className="inline-block bg-white text-blue-600 px-6 py-3 rounded-lg font-medium border border-blue-600 hover:bg-blue-50 transition-colors"
            >
              Create Account
            </Link>
          </div>
        </div>
      </div>
      
      {/* Feature Section */}
      <div className="bg-white py-16">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12 text-gray-900">
            Powerful Library Analytics
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="bg-blue-50 rounded-lg p-6 shadow-sm transition-transform hover:translate-y-[-5px]">
              <div className="bg-blue-100 w-12 h-12 rounded-full flex items-center justify-center mb-4">
                <Database size={24} className="text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold mb-2 text-gray-900">Data Collection</h3>
              <p className="text-gray-600">
                Import and manage public library survey data from multiple sources in a standardized format.
              </p>
            </div>
            
            {/* Feature 2 */}
            <div className="bg-blue-50 rounded-lg p-6 shadow-sm transition-transform hover:translate-y-[-5px]">
              <div className="bg-blue-100 w-12 h-12 rounded-full flex items-center justify-center mb-4">
                <PieChart size={24} className="text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold mb-2 text-gray-900">Visual Analysis</h3>
              <p className="text-gray-600">
                Transform complex library statistics into clear, interactive visualizations and dashboards.
              </p>
            </div>
            
            {/* Feature 3 */}
            <div className="bg-blue-50 rounded-lg p-6 shadow-sm transition-transform hover:translate-y-[-5px]">
              <div className="bg-blue-100 w-12 h-12 rounded-full flex items-center justify-center mb-4">
                <TrendingUp size={24} className="text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold mb-2 text-gray-900">Trend Analysis</h3>
              <p className="text-gray-600">
                Track performance metrics over time and identify important trends in library usage and services.
              </p>
            </div>
            
            {/* Feature 4 */}
            <div className="bg-blue-50 rounded-lg p-6 shadow-sm transition-transform hover:translate-y-[-5px]">
              <div className="bg-blue-100 w-12 h-12 rounded-full flex items-center justify-center mb-4">
                <LineChart size={24} className="text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold mb-2 text-gray-900">Benchmark Comparison</h3>
              <p className="text-gray-600">
                Compare your library's performance against similar institutions or regional averages.
              </p>
            </div>
            
            {/* Feature 5 */}
            <div className="bg-blue-50 rounded-lg p-6 shadow-sm transition-transform hover:translate-y-[-5px]">
              <div className="bg-blue-100 w-12 h-12 rounded-full flex items-center justify-center mb-4">
                <BookOpen size={24} className="text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold mb-2 text-gray-900">Collection Insights</h3>
              <p className="text-gray-600">
                Analyze your collection usage and circulation patterns to optimize resource allocation.
              </p>
            </div>
            
            {/* Feature 6 */}
            <div className="bg-blue-50 rounded-lg p-6 shadow-sm transition-transform hover:translate-y-[-5px]">
              <div className="bg-blue-100 w-12 h-12 rounded-full flex items-center justify-center mb-4">
                <Users size={24} className="text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold mb-2 text-gray-900">Patron Analytics</h3>
              <p className="text-gray-600">
                Understand patron demographics and usage patterns to better serve your community.
              </p>
            </div>
          </div>
        </div>
      </div>
      
      {/* CTA Section */}
      <div className="bg-blue-600 text-white py-16">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-6">Ready to transform your library data?</h2>
          <p className="text-xl mb-8 max-w-2xl mx-auto">
            Join library directors nationwide who are using LibraryPulse to make data-driven decisions.
          </p>
          <Link
            to="/register"
            className="inline-flex items-center bg-white text-blue-600 px-6 py-3 rounded-lg font-medium hover:bg-blue-50 transition-colors"
          >
            Get Started <ArrowRight size={20} className="ml-2" />
          </Link>
        </div>
      </div>
    </div>
  );
};

export default LandingPage; 