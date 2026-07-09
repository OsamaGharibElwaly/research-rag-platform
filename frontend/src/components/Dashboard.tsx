import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/auth';
import { authApi } from '../api/auth';

export default function Dashboard() {
  const navigate = useNavigate();
  const { user, isAuthenticated, logout } = useAuthStore();

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    // Verify token is still valid
    authApi.getMe().catch(() => {
      logout();
      navigate('/login');
    });
  }, [isAuthenticated, navigate, logout]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (!user) return null;

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-gray-900">AI Research Assistant</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">{user.email}</span>
              <button
                onClick={handleLogout}
                className="px-4 py-2 text-sm font-medium text-red-600 hover:text-red-800"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="bg-white rounded-xl shadow p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Welcome, {user.full_name || user.username}!</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-primary-50 rounded-lg p-4">
                <h3 className="font-semibold text-primary-700">Paper Library</h3>
                <p className="text-sm text-gray-600 mt-1">Manage your research papers</p>
              </div>
              <div className="bg-primary-50 rounded-lg p-4">
                <h3 className="font-semibold text-primary-700">Chat with AI</h3>
                <p className="text-sm text-gray-600 mt-1">Ask questions about your papers</p>
              </div>
              <div className="bg-primary-50 rounded-lg p-4">
                <h3 className="font-semibold text-primary-700">Generate Reports</h3>
                <p className="text-sm text-gray-600 mt-1">Summaries, quizzes, citations</p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}