import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { Droplets, Users, Search } from "lucide-react";
import toast from "react-hot-toast";

const LoginPage = () => {
  const [selectedRole, setSelectedRole] = useState("");
  const [name, setName] = useState("");
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleLogin = (e) => {
    e.preventDefault();

    if (!selectedRole || !name.trim()) {
      toast.error("Please select a role and enter your name");
      return;
    }

    // Simple mock authentication
    const userData = {
      name: name.trim(),
      role: selectedRole,
      loginTime: new Date().toISOString(),
    };

    login(userData);
    toast.success(`Welcome, ${userData.name}!`);
    navigate("/dashboard");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-water-50 to-primary-100 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        {/* Logo and Title */}
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <div className="bg-water-500 p-3 rounded-full">
              <Droplets className="w-8 h-8 text-white" />
            </div>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">AquaForesee</h1>
          <p className="text-gray-600">
            Decision Support System for Water Resource Management
          </p>
        </div>

        {/* Login Form */}
        <div className="card p-6">
          <form onSubmit={handleLogin} className="space-y-6">
            <div>
              <label
                htmlFor="name"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                Your Name
              </label>
              <input
                type="text"
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="input-field"
                placeholder="Enter your name"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Select Your Role
              </label>
              <div className="space-y-3">
                <div
                  className={`p-4 border-2 rounded-lg cursor-pointer transition-all duration-200 ${
                    selectedRole === "Policymaker"
                      ? "border-primary-500 bg-primary-50"
                      : "border-gray-200 hover:border-gray-300"
                  }`}
                  onClick={() => setSelectedRole("Policymaker")}
                >
                  <div className="flex items-center">
                    <Users className="w-5 h-5 text-primary-600 mr-3" />
                    <div>
                      <h3 className="font-medium text-gray-900">Policymaker</h3>
                      <p className="text-sm text-gray-600">
                        Access policy insights and regional overviews
                      </p>
                    </div>
                  </div>
                </div>

                <div
                  className={`p-4 border-2 rounded-lg cursor-pointer transition-all duration-200 ${
                    selectedRole === "Researcher"
                      ? "border-primary-500 bg-primary-50"
                      : "border-gray-200 hover:border-gray-300"
                  }`}
                  onClick={() => setSelectedRole("Researcher")}
                >
                  <div className="flex items-center">
                    <Search className="w-5 h-5 text-primary-600 mr-3" />
                    <div>
                      <h3 className="font-medium text-gray-900">Researcher</h3>
                      <p className="text-sm text-gray-600">
                        Access detailed analytics and modeling tools
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <button
              type="submit"
              className="w-full btn-primary py-3 text-lg"
              disabled={!selectedRole || !name.trim()}
            >
              Access Dashboard
            </button>
          </form>
        </div>

        {/* Footer */}
        <div className="text-center mt-6 text-sm text-gray-500">
          <p></p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
