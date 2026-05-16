import { useContext, useState } from 'react';
import { postChat, postEscalate } from '../api/omniflow.js';
import { AppContext } from '../context/AppContext.js';

const agents = [
  { value: 'sales', label: 'Sales' },
  { value: 'support', label: 'Support' },
  { value: 'insight', label: 'Insight' },
];

export default function ChatPage() {
  const { currentAgent, setCurrentAgent, userId } = useContext(AppContext);
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([]);
  const [error, setError] = useState('');
  const [isSending, setIsSending] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();

    const trimmedMessage = message.trim();
    if (!trimmedMessage || isSending) {
      return;
    }

    setError('');
    setIsSending(true);
    setMessage('');
    setMessages((items) => [...items, { role: 'user', content: trimmedMessage }]);

    try {
      const data = await postChat(userId, trimmedMessage, currentAgent);
      setMessages((items) => [
        ...items,
        {
          role: 'assistant',
          content: data.reply,
          sentiment: data.sentiment,
          escalated: data.escalate,
        },
      ]);
    } catch (requestError) {
      setError(requestError.message || 'Unable to send message.');
    } finally {
      setIsSending(false);
    }
  };

  const handleEscalate = async () => {
    setError('');

    try {
      const data = await postEscalate(userId);
      setMessages((items) => [
        ...items,
        { role: 'system', content: data.message || 'Manual escalation requested.' },
      ]);
    } catch (requestError) {
      setError(requestError.message || 'Unable to request escalation.');
    }
  };

  return (
    <section className="mx-auto flex h-full max-w-5xl flex-col gap-4">
      <div className="flex flex-col gap-3 rounded-lg border border-primary/20 bg-black/30 p-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-lg font-semibold text-primary">Chat</h2>
          <p className="text-sm text-primary/70">Session: {userId}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          {agents.map((agent) => (
            <button
              key={agent.value}
              type="button"
              onClick={() => setCurrentAgent(agent.value)}
              className={`rounded-md border px-3 py-2 text-sm transition ${
                currentAgent === agent.value
                  ? 'border-primary bg-primary text-bg'
                  : 'border-primary/30 text-primary hover:bg-primary/10'
              }`}
            >
              {agent.label}
            </button>
          ))}
        </div>
      </div>

      <div className="min-h-80 flex-1 overflow-auto rounded-lg border border-primary/20 bg-black/30 p-4">
        {messages.length === 0 ? (
          <div className="flex h-full min-h-64 items-center justify-center text-center text-primary/60">
            Start a conversation with the selected agent.
          </div>
        ) : (
          <div className="space-y-3">
            {messages.map((item, index) => (
              <div
                key={`${item.role}-${index}`}
                className={`rounded-md border p-3 ${
                  item.role === 'user'
                    ? 'ml-auto max-w-2xl border-secondary/30 bg-secondary/10'
                    : 'mr-auto max-w-2xl border-primary/30 bg-primary/10'
                }`}
              >
                <p className="mb-1 text-xs uppercase text-secondary">{item.role}</p>
                <p className="whitespace-pre-wrap text-sm text-primary">{item.content}</p>
                {item.sentiment ? (
                  <p className="mt-2 text-xs text-primary/70">Sentiment: {item.sentiment}</p>
                ) : null}
                {item.escalated ? (
                  <p className="mt-1 text-xs text-alert">Escalation requested</p>
                ) : null}
              </div>
            ))}
          </div>
        )}
      </div>

      {error ? (
        <p className="rounded-md border border-alert/40 bg-alert/10 px-3 py-2 text-sm text-alert">
          {error}
        </p>
      ) : null}

      <form onSubmit={handleSubmit} className="flex flex-col gap-3 sm:flex-row">
        <input
          type="text"
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          placeholder="Type your message..."
          className="min-w-0 flex-1 rounded-md border border-primary/30 bg-black/40 px-3 py-3 text-primary outline-none placeholder:text-primary/40 focus:border-primary"
        />
        <button
          type="submit"
          disabled={isSending}
          className="rounded-md bg-primary px-5 py-3 font-semibold text-bg transition hover:bg-secondary disabled:cursor-not-allowed disabled:opacity-60"
        >
          {isSending ? 'Sending...' : 'Send'}
        </button>
        <button
          type="button"
          onClick={handleEscalate}
          className="rounded-md border border-alert/50 px-5 py-3 text-alert transition hover:bg-alert/10"
        >
          Escalate
        </button>
      </form>
    </section>
  );
}
