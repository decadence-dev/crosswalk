const connectEventActions = (store, delay = 1000) => {
  const ws = new WebSocket('ws://localhost:3000/events-actions');
  ws.onopen = () => {
    ws.send(JSON.stringify({
      token: localStorage.getItem('token'),
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    }));
  };
  ws.onmessage = (msg) => {
    const data = JSON.parse(msg.data);
    store.dispatch('RECEIVE_EVENT_ACTION', data);
  };
  ws.onclose = () => {
    setTimeout(connectEventActions, store, delay, delay * 1.5);
  };
};

export default connectEventActions;
