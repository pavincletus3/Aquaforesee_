import React from "react";
import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";
import { Droplets, LogOut, User } from "lucide-react";
import toast from "react-hot-toast";

const Header = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    toast.success("Logged out successfully");
    navigate("/");
  };

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Logo and Title */}
        <div className="flex items-center space-x-3">
          <div className="bg-water-500 p-2 rounded-lg">
            <Droplets className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">AquaForesee</h1>
            <p className="text-sm text-gray-600">
              Water Resource Management Dashboard
            </p>
          </div>
        </div>

        {/* User Info and Actions */}
        <div className="flex items-center space-x-4">
          {/* User Info */}
          <div className="flex items-center space-x-2 text-sm">
            <User className="w-4 h-4 text-gray-500" />
            <span className="text-gray-700">{user?.name}</span>
            <span className="text-gray-500">•</span>
            <span className="text-primary-600 font-medium">{user?.role}</span>
          </div>

          {/* Logout Button */}
          <button
            onClick={handleLogout}
            className="flex items-center space-x-2 px-3 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors duration-200"
          >
            <LogOut className="w-4 h-4" />
            <span>Logout</span>
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;
