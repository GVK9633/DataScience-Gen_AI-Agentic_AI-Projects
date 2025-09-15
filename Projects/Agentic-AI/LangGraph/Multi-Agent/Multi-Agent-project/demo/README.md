# Dynamic Agent Framework with LangGraph

This project demonstrates a **dynamic multi-agent framework** using **LangGraph**, **MCP servers**, and **RAG**.  
The framework supports **parent → child agents (Weather, Pollution)** with **dynamic configuration**.  
Add new MCP servers, tools, or LLMs just by editing `config/agents.yaml`.

---

## 🚀 Features
- Modular project scaffold (config-driven)
- MCP tool servers (Weather, Pollution examples)
- Agent factory (builds agents dynamically from config)
- Multi-agent coordination (Parent → Child)
- RAG (Retrieval Augmented Generation with Chroma + OpenAI embeddings)
- Supports **OpenAI** and **Gemini** LLMs
- Easily extendable — no need to change core code when adding new tools

---

## 📂 Project Structure
```
dynamic_agent_framework/
│── config/
│   └── agents.yaml         # Central configuration
│
│── mcps/
│   ├── weather_mcp.py      # Weather MCP tool server
│   └── pollution_mcp.py    # Pollution MCP tool server
│
│── tools/
│   ├── weather.py          # Weather tool implementations
│   └── pollution.py        # Pollution tool implementations
│
│── rag/
│   ├── documents/          # Sample documents for RAG
│   └── vectorstore.py      # VectorDB setup (Chroma + OpenAI embeddings)
│
│── agent_factory.py        # Builds agents dynamically from config
│── main.py                 # Entry point to run parent & child agents
│── README.md               # Project documentation
```

---

## ⚙️ Setup

### 1. Clone & Install
```bash
unzip dynamic_agent_framework.zip
cd dynamic_agent_framework
pip install -r requirements.txt
```

**Requirements (`requirements.txt`):**
```
langgraph
langchain
langchain-openai
langchain-google-genai
langchain-mcp-adapters
fastmcp
httpx
python-dotenv
chromadb
```

### 2. Run MCP Servers
Each MCP must run in a separate terminal:
```bash
python mcps/weather_mcp.py
python mcps/pollution_mcp.py
```

### 3. Run Main Script
```bash
python main.py
```

---

## 🔧 How to Add a New Agent
1. Edit `config/agents.yaml` and add a new section:
```yaml
  news:
    mcp_servers:
      - http://localhost:8004/mcp
    tools:
      - tools.news:get_headlines
    llm: openai
```

2. Add MCP server script inside `mcps/`.
3. Add tool implementation inside `tools/`.
4. Restart the app → new agent is automatically loaded!

---

## 🧠 Example Query
```text
"What is the weather in London and pollution in Delhi?"
```

**Output:**
```
🌦 Weather Agent: London: 🌤 +20°C
🏭 Pollution Agent: Pollution level in Delhi: High (mocked)
```

---

## 📌 Notes
- For **RAG**, add `.txt` files to `rag/documents/` and they’ll be ingested automatically.
- OpenAI key must be set via `OPENAI_API_KEY` environment variable.
- Gemini requires Google API key via `GOOGLE_API_KEY`.

---

Happy hacking! 🚀
