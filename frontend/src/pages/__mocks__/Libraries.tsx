import React from 'react';

const Libraries = () => {
  return (
    <div data-testid="mock-libraries">
      <h1 className="text-2xl font-bold mb-6">Libraries</h1>
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <input
              type="text"
              className="block w-full rounded-md border-0 py-2 px-4 text-gray-900"
              placeholder="Search libraries..."
            />
          </div>
          <div className="w-full md:w-64">
            <select className="block w-full rounded-md border-0 py-2 px-4 text-gray-900">
              <option value="">All States</option>
              <option value="CA">CA</option>
              <option value="NY">NY</option>
            </select>
          </div>
        </div>
      </div>
      <div className="space-y-4">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold">San Francisco Public Library</h2>
          <p>San Francisco, CA</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold">New York Public Library</h2>
          <p>New York, NY</p>
        </div>
      </div>
    </div>
  );
};

export default Libraries; 