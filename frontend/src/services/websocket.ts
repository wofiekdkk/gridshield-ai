export interface WsMessage {
  event: string;
  timestamp: string;
  data: any;
}

type Listener = (msg: WsMessage) => void;

class WsClient {
  private ws: WebSocket | null = null;
  private listeners: Set<Listener> = new Set();
  private reconnectTimer: any = null;
  private url = "ws://localhost:8000/api/v1/ws/grid";

  connect() {
    if (typeof window === "undefined") return;
    if (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)) {
      return;
    }

    try {
      this.ws = new WebSocket(this.url);
      this.ws.onopen = () => {
        console.log("[WS] Connected to GridShield AI Control Bus");
      };
      this.ws.onmessage = (ev) => {
        try {
          const msg = JSON.parse(ev.data);
          const formatted: WsMessage = {
            event: msg.event || "unknown",
            timestamp: msg.timestamp || new Date().toISOString(),
            data: msg.data !== undefined ? msg.data : {},
          };
          this.listeners.forEach((l) => {
            try { l(formatted); } catch (err) { console.error(err); }
          });
        } catch (e) {
          console.warn("[WS] Parse error", e);
        }
      };
      this.ws.onclose = () => this.scheduleReconnect();
      this.ws.onerror = () => {
        try { this.ws?.close(); } catch {}
      };
    } catch (e) {
      this.scheduleReconnect();
    }
  }

  private scheduleReconnect() {
    if (this.reconnectTimer) return;
    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null;
      this.connect();
    }, 3000);
  }

  subscribe(listener: Listener) {
    this.listeners.add(listener);
    return () => {
      this.listeners.delete(listener);
    };
  }

  send(data: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      try {
        this.ws.send(JSON.stringify(data));
      } catch {}
    }
  }

  disconnect() {
    if (this.ws) {
      try { this.ws.close(); } catch {}
      this.ws = null;
    }
  }

  isConnected(): boolean {
    return !!(this.ws && this.ws.readyState === WebSocket.OPEN);
  }
}

export const wsClient = new WsClient();
