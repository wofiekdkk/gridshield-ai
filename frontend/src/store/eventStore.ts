import { create } from "zustand";
import type { WsMessage } from "../types";

interface EventState {
  events: WsMessage[];
  alerts: WsMessage[];
  addEvent: (event: WsMessage) => void;
  clear: () => void;
}

export const useEventStore = create<EventState>((set) => ({
  events: [],
  alerts: [],
  addEvent: (event) => set((state) => {
    const events = [event, ...state.events].slice(0, 200);
    const alerts =
      ["fault_detected", "fault_classified", "cascade_predicted", "recovery_executed"].includes(event.event)
        ? [event, ...state.alerts].slice(0, 50)
        : state.alerts;
    return { events, alerts };
  }),
  clear: () => set({ events: [], alerts: [] }),
}));
