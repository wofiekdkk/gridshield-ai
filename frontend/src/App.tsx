import { useEffect } from "react";
import type { ReactNode } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import MainLayout from "./components/layout/MainLayout";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import DigitalTwin from "./pages/DigitalTwin";
import LiveSensors from "./pages/LiveSensors";
import FaultCenter from "./pages/FaultCenter";
import AIDiagnostics from "./pages/AIDiagnostics";
import RecoveryCenter from "./pages/RecoveryCenter";
import FaultSimulator from "./pages/FaultSimulator";
import Analytics from "./pages/Analytics";
import History from "./pages/History";
import Settings from "./pages/Settings";
import { useAuthStore } from "./store/authStore";

function ProtectedRoute({ children }: { children: ReactNode }) {
  const token = useAuthStore((s) => s.token);
  return token ? <>{children}</> : <Navigate to="/login" replace />;
}

export default function App() {
  const init = useAuthStore((s) => s.init);
  useEffect(() => { init(); }, [init]);

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route element={<ProtectedRoute><MainLayout /></ProtectedRoute>}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/digital-twin" element={<DigitalTwin />} />
          <Route path="/sensors" element={<LiveSensors />} />
          <Route path="/faults" element={<FaultCenter />} />
          <Route path="/ai" element={<AIDiagnostics />} />
          <Route path="/recovery" element={<RecoveryCenter />} />
          <Route path="/simulator" element={<FaultSimulator />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/history" element={<History />} />
          <Route path="/settings" element={<Settings />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
