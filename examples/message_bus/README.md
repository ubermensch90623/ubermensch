# Message bus

Event-driven fan-out. Agents publish/subscribe on topics; no central
orchestrator. Use when multiple consumers act on the same event or loose
coupling between stages matters.

Run:
```bash
python -m examples.message_bus "prompt caching"
```
