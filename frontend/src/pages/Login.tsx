import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Zap } from "lucide-react";
import { authAPI } from "../services/api";
import { useAuthStore } from "../store/authStore";

export default function Login() {
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("admin123");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const login = useAuthStore((s) => s.login);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const res = await authAPI.login(username, password);
      login(res.access_token, res.user);
      navigate("/");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-grid-bg">
      <div className="w-full max-w-md bg-grid-panel border border-grid-border rounded-xl p-8">
        <div className="flex items-center justify-center gap-3 mb-6">
          <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-lg flex items-center justify-center">
            <Zap className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-grid-text">GridShield AI</h1>
            <p className="text-xs text-grid-muted">Control Center Login</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm text-grid-muted mb-1">Username</label>
            <input
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full bg-grid-bg border border-grid-border rounded px-3 py-2 text-grid-text focus:border-grid-accent outline-none"
              required
            />
          </div>
          <div>
            <label className="block text-sm text-grid-muted mb-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-grid-bg border border-grid-border rounded px-3 py-2 text-grid-text focus:border-grid-accent outline-none"
              required
            />
          </div>
          {error && <div className="text-sm text-grid-danger">{error}</div>}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-grid-accent hover:bg-blue-600 text-white font-semibold py-2 rounded transition disabled:opacity-50"
          >
            {loading ? "Signing in..." : "Sign In"}
          </button>
        </form>

        <div className="mt-6 text-xs text-grid-muted text-center">
          <div>Default: admin / admin123</div>
          <div>operator / operator123 | viewer / viewer123</div>
        </div>
      </div>
    </div>
  );
}
