![Avaly Logo](./logo.png)

>Introducing the first agentic version of [Garak](https://github.com/NVIDIA/garak/) by Avaly.ai. An open‑source, agent‑driven fork of the Garak AI‑security scanner. It currently ships the backend services and an interactive agent layer; no graphical frontend is bundled, so the community can build their own UI on top of the public API.

## Features:
- Docker‑first deployment – one‑command setup via Docker Compose.
- Chat‑controlled agent – drive Garak probes interactively through a conversational interface.
- Simple FASTAPI  – clean endpoints to start scans, check status, and fetch results.
- Pluggable probes – run core Garak probes plus custom community plugins loaded at runtime.
- Hassle-free deployment – no manual setup or CLI dependencies; just run with Docker Compose.
- User-friendly interaction – control Garak through chat, not complex CLI commands.

---
## Prerequisites

* **Docker** 20.10+ and the Docker Compose v2 CLI plugin.
* **GPU (optional)** if you want CUDA-accelerated Garak runs.
* **Ollama** running locally for LLM back-end.

Pull the base LLM once:

```bash
ollama pull magistral:24b-small-2506-q8_0
```
---

## Quick Start

```bash 
# Build & start every service 
docker compose up --build

```

That stack will be reachabel at:

* `http://localhost:5000` - Agent FastApi 
* `http://localhost:8000` - Agent

---

## Endpoints

### Agent API (`service-agent`)

| Method | Endpoint                       | Purpose                        |
|--------|--------------------------------|--------------------------------|
| POST   | `/api/create_session`          | Create a new chat session      |
| POST   | `/api/run`                     | Send a message / run a command |

---


## Usage Examples

Note: Persist same 'userId' across all requests

```bash
# 1. Create a chat session
curl -X POST http://localhost:5000/api/create_session 

# 2. Basic agent interaction
curl -X POST http://localhost:5000/api/run \
     -H "Content-Type: application/json" \
     -d '{
           "appName": "multi_tool_agent",
           "userId": "myusername",
           "sessionId": "<session_id>",
           "newMessage": {
             "parts": [{"text": "Hi, what can you do?"}],
             "role": "user"
           },
           "streaming": false
         }'

# 3. Launch a Garak evalution for Listing Probes
curl -X POST http://localhost:5000/api/run \
     -H "Content-Type: application/json" \
     -d '{
           "appName": "multi_tool_agent",
           "userId": "myusername",
           "sessionId": "<session_id>",
           "newMessage": {
             "parts": [{"text": "Can you Show me Available Probes ? "}],
             "role": "user"
           },
           "streaming": false
         }'

# 4. Launch a Garak evalution for Scan Huggingface model with Probes(Wait for Output)
curl -X POST http://localhost:5000/api/run \
     -H "Content-Type: application/json" \
     -d '{
           "appName": "multi_tool_agent",
           "userId": "myusername",
           "sessionId": "<session_id>",
           "newMessage": {
             "parts": [{"text": "Run Scan with model name Gpt2 and probes is lmrc?"}],
             "role": "user"
           },
           "streaming": false
         }'
```

---

## Sample Output

![Sample Output](./screenshot.png)

--- 

## Architecture


| Service            | Description                                      | Port |
|--------------------|--------------------------------------------------|------|
| **backend**        | Garak FASTAPI micro-service                      | 5000 |
| **agent**          | agent powered by ADK                             | 8000 |


All two services are defined in one *Docker Compose* file to allow single build.

```

+-----------+     FASTAPI  +-----------+    internal    +-----------+
|  User     | -----------> |  Backend  | -------------> | Chat Agent|
| (prompt)  |              |  API      |                | (Garak)   |
+-----------+              +-----------+                +-----------+


```

## Contributions
Contributions welcome! 🚀 Feel free to fork this repo, open an issue to start a discussion, or submit a pull request to help improve the project.

---

## License

This repository is licensed under the **Apache 2.0** license.
The license is avaialable at [LICENSE](./LICENSE)

---

## Credits
Built with ❤️ by Avaly.ai. For support, reach out at: contact@avaly.ai.
