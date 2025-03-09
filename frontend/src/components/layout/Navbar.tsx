import { useState } from 'react';
import { Search, Bell, HelpCircle, User } from 'lucide-react';

const Navbar = () => {
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    console.log('Searching for:', searchQuery);
    // Implement search functionality
  };

  return (
    <header className="bg-white border-b border-gray-200 py-4 px-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center flex-1">
          <form onSubmit={handleSearch} className="w-full max-w-lg">
            <div className="relative">
              <span className="absolute inset-y-0 left-0 flex items-center pl-3">
                <Search className="h-5 w-5 text-gray-400" />
              </span>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="block w-full rounded-md border-0 py-2 pl-10 pr-4 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-500 sm:text-sm"
                placeholder="Search libraries..."
              />
            </div>
          </form>
        </div>
        <div className="flex items-center space-x-4">
          <button className="p-1 rounded-full text-gray-500 hover:text-gray-700 focus:outline-none focus:ring-2 focus:ring-primary-500">
            <Bell className="h-6 w-6" />
          </button>
          <button className="p-1 rounded-full text-gray-500 hover:text-gray-700 focus:outline-none focus:ring-2 focus:ring-primary-500">
            <HelpCircle className="h-6 w-6" />
          </button>
          <div className="relative">
            <button className="flex items-center space-x-4 focus:outline-none">
              <div className="h-9 w-9 rounded-full bg-primary-100 flex items-center justify-center">
                <User className="h-5 w-5 text-primary-700" />
              </div>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Navbar; 