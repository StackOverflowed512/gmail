import React from 'react';
import { useAuth } from '../context/AuthContext';
import { LayoutDashboard, Inbox, LogOut, MessageSquareDashedIcon } from 'lucide-react';
import { Link, Outlet } from 'react-router';

function DashboardLayout() {
  const { user } = useAuth();

  return (
    <div className='grid grid-cols-[auto_1fr] h-screen'>
      <div className="h-screen bg-primary text-white p-4 border-r flex flex-col justify-between border-background w-64">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl text-white uppercase font-black">
              Dashboard
            </h2>
          </div>

          {/* Navigation Links */}
          <nav className="space-y-2">
            <Link
              to="/dashboard/home"
              className="flex items-center px-4 py-2 rounded hover:bg-primary-focus transition-colors duration-200"
            >
              <LayoutDashboard size={20} className="mr-2" />
              <span>Dashboard</span>
            </Link>
            <Link
              to="/dashboard/inbox"
              className="flex items-center px-4 py-2 rounded hover:bg-primary-focus transition-colors duration-200"
            >
              <Inbox size={20} className="mr-2" />
              <span>Inbox</span>
            </Link>
            <Link
              to="/dashboard/sent"
              className="flex items-center px-4 py-2 rounded hover:bg-primary-focus transition-colors duration-200"
            >
              <MessageSquareDashedIcon size={20} className="mr-2" />
              <span>Sent</span>
            </Link>
          </nav>
        </div>
        <button
          onClick={() => {
            localStorage.removeItem('access_token');
            window.location.href = '/';
          }}
          className="w-full items-center gap-2 flex bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600 transition-colors duration-200"
        >
          <LogOut size={14} />
          <p>Logout</p>
        </button>
      </div>
      {/* Main Content Area */}
      <div className="flex-1 max-h-screen w-full overflow-hidden bg-primary bg-base-100">
        <Outlet />
      </div>
    </div>
  );
}

export default DashboardLayout;
