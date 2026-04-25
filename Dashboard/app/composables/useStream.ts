export const useStream = () => {
  const config = useRuntimeConfig();
  const ws = useState<WebSocket | null>("ws-stream", () => null);
  const connected = useState("ws-connected", () => false);
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  let shouldReconnect = true;

  const clearReconnectTimer = () => {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer);
      reconnectTimer = null;
    }
  };

  const connect = () => {
    if (import.meta.server) return;
    if (ws.value && ws.value.readyState <= WebSocket.OPEN) return;

    shouldReconnect = true;
    clearReconnectTimer();

    const base = config.public.apiBase.replace(/^http/, "ws");
    const socket = new WebSocket(`${base}/api/v1/stream`);

    socket.onopen = () => {
      connected.value = true;
    };

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (!data.event) return;

        if (data.event === "alert:new" || data.event === "alert:updated" || data.event === "alert:mobile_emergency") {
          const { refreshAlerts } = useAlerts();
          refreshAlerts();
        }

        if (data.event === "location:occupancy_update") {
          const { refreshLocations } = useSafeLocations();
          refreshLocations();
        }
      } catch {
        // ignore malformed messages
      }
    };

    socket.onclose = () => {
      connected.value = false;
      ws.value = null;
      if (shouldReconnect) {
        clearReconnectTimer();
        reconnectTimer = setTimeout(connect, 3000);
      }
    };

    socket.onerror = () => {
      socket.close();
    };

    ws.value = socket;
  };

  const disconnect = () => {
    shouldReconnect = false;
    clearReconnectTimer();
    if (ws.value) {
      ws.value.close();
      ws.value = null;
      connected.value = false;
    }
  };

  return { connected, connect, disconnect };
};
