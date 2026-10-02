import { useEffect, useState } from "react";
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts";
import Card from "../components/ui/Card";
import { sensorAPI } from "../services/api";

export default function LiveSensors() {
  const [readings, setReadings] = useState<any[]>([]);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await sensorAPI.list(100);
        if (Array.isArray(data)) setReadings(data);
      } catch (e) {
        console.error(e);
      }
    };
    load();
    const t = setInterval(load, 2000);
    return () => clearInterval(t);
  }, []);

  const chartData = readings.slice(0, 30).reverse().map((r) => ({
    name: new Date(r.timestamp || Date.now()).toLocaleTimeString(),
    voltage: r.voltage,
    current: r.current,
    temperature: r.temperature,
    load: r.load_percentage,
  }));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-grid-text">Live Sensors</h1>
        <p className="text-sm text-grid-muted">Real-time IoT sensor measurements</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Voltage & Current">
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={chartData}>
              <CartesianGrid stroke="#2a3447" />
              <XAxis dataKey="name" stroke="#9ca3af" fontSize={10} />
              <YAxis stroke="#9ca3af" fontSize={10} />
              <Tooltip contentStyle={{ background: "#1a2234", border: "1px solid #2a3447" }} />
              <Line type="monotone" dataKey="voltage" stroke="#3b82f6" dot={false} />
              <Line type="monotone" dataKey="current" stroke="#f59e0b" dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </Card>

        <Card title="Temperature & Load">
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={chartData}>
              <CartesianGrid stroke="#2a3447" />
              <XAxis dataKey="name" stroke="#9ca3af" fontSize={10} />
              <YAxis stroke="#9ca3af" fontSize={10} />
              <Tooltip contentStyle={{ background: "#1a2234", border: "1px solid #2a3447" }} />
              <Line type="monotone" dataKey="temperature" stroke="#ef4444" dot={false} />
              <Line type="monotone" dataKey="load" stroke="#10b981" dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </Card>
      </div>

      <Card title="Latest Readings">
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead className="text-grid-muted uppercase border-b border-grid-border">
              <tr>
                <th className="text-left py-2 px-2">Time</th>
                <th className="text-left py-2 px-2">Sensor</th>
                <th className="text-right py-2 px-2">V</th>
                <th className="text-right py-2 px-2">I</th>
                <th className="text-right py-2 px-2">Hz</th>
                <th className="text-right py-2 px-2">Temp</th>
                <th className="text-right py-2 px-2">Load%</th>
                <th className="text-center py-2 px-2">Status</th>
              </tr>
            </thead>
            <tbody>
              {readings.slice(0, 30).map((r) => (
                <tr key={r.id || r.sensor_id} className="border-b border-grid-border/50">
                  <td className="py-1 px-2 text-grid-muted">{new Date(r.timestamp || Date.now()).toLocaleTimeString()}</td>
                  <td className="py-1 px-2 font-mono text-grid-text">{r.sensor_id}</td>
                  <td className="py-1 px-2 text-right text-grid-text">{(r.voltage || 0).toFixed(1)}</td>
                  <td className="py-1 px-2 text-right text-grid-text">{(r.current || 0).toFixed(1)}</td>
                  <td className="py-1 px-2 text-right text-grid-text">{(r.frequency || 0).toFixed(2)}</td>
                  <td className="py-1 px-2 text-right text-grid-text">{(r.temperature || 0).toFixed(1)}</td>
                  <td className="py-1 px-2 text-right text-grid-text">{(r.load_percentage || 0).toFixed(1)}</td>
                  <td className="py-1 px-2 text-center text-grid-success">{r.status || "NORMAL"}</td>
                </tr>
              ))}
              {readings.length === 0 && (
                <tr><td colSpan={8} className="text-center py-6 text-grid-muted">No sensor data yet</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
