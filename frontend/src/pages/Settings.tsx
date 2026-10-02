import Card from "../components/ui/Card";
import { useAuthStore } from "../store/authStore";

export default function Settings() {
  const user = useAuthStore((s) => s.user);
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-grid-text">Settings</h1>
        <p className="text-sm text-grid-muted">User and system configuration</p>
      </div>

      <Card title="User Profile">
        <div className="space-y-3 text-sm">
          <div><span className="text-grid-muted">Username:</span> <span className="text-grid-text ml-2">{user?.username}</span></div>
          <div><span className="text-grid-muted">Email:</span> <span className="text-grid-text ml-2">{user?.email || "N/A"}</span></div>
          <div><span className="text-grid-muted">Role:</span> <span className="text-grid-accent ml-2 font-semibold">{user?.role}</span></div>
        </div>
      </Card>

      <Card title="System Info">
        <div className="space-y-2 text-sm">
          <div><span className="text-grid-muted">Backend:</span> <span className="text-grid-text ml-2">http://localhost:8000</span></div>
          <div><span className="text-grid-muted">WebSocket:</span> <span className="text-grid-text ml-2">ws://localhost:8000/api/v1/ws/grid</span></div>
          <div><span className="text-grid-muted">Version:</span> <span className="text-grid-text ml-2">GridShield AI v1.0.0</span></div>
        </div>
      </Card>
    </div>
  );
}
