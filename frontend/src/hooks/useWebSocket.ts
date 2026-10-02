import { useEffect } from "react";
import { wsClient } from "../services/websocket";
import { useEventStore } from "../store/eventStore";

export function useWebSocket() {
  const addEvent = useEventStore((s) => s.addEvent);

  useEffect(() => {
    wsClient.connect();
    const unsub = wsClient.subscribe((msg) => addEvent(msg));
    return () => { unsub(); };
  }, [addEvent]);
}
