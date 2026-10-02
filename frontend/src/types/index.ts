export interface User {
  id: number;
  username: string;
  email?: string;
  role: "ADMIN" | "OPERATOR" | "VIEWER";
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface GridComponent {
  component_id: string;
  component_type: string;
  name?: string;
  is_critical?: boolean;
  status: string;
  properties?: Record<string, any>;
}

export interface GridState {
  status?: string;
  total_generation?: number;
  total_load?: number;
  max_line_loading?: number;
  min_voltage?: number;
  max_voltage?: number;
  buses?: any[];
  lines?: any[];
}

export interface SensorReading {
  id: number;
  sensor_id: string;
  component_id?: string;
  timestamp: string;
  voltage?: number;
  current?: number;
  frequency?: number;
  active_power?: number;
  reactive_power?: number;
  temperature?: number;
  power_factor?: number;
  load_percentage?: number;
  breaker_status?: string;
  line_status?: string;
  status?: string;
}

export interface FaultEvent {
  id: number;
  fault_id: string;
  component_id: string;
  fault_type: string;
  severity?: number;
  confidence?: number;
  cascade_risk?: number;
  status: string;
  start_time: string;
  end_time?: string;
  details?: Record<string, any>;
}

export interface RecoveryPlan {
  id: number;
  plan_id: string;
  fault_id: string;
  actions: any[];
  restored_load?: number;
  cascade_risk?: number;
  max_line_loading?: number;
  constraint_violations?: any[];
  feasible: boolean;
  objective_score?: number;
  selected: boolean;
  created_at: string;
}

export interface AIPrediction {
  id: number;
  fault_id?: string;
  model_type: string;
  predicted_class: string;
  confidence: number;
  probabilities?: Record<string, number>;
  timestamp: string;
}

export interface WsMessage {
  event: string;
  timestamp: string;
  data: any;
}
