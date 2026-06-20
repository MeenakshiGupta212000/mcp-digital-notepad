# Local AI Memory Server (MCP + RAG)

## Why I Built This

Most beginner AI projects are just basic API wrappers around ChatGPT. I wanted to build something closer to real enterprise AI infrastructure. 

This project is a **Decoupled Agentic RAG (Retrieval-Augmented Generation) Server**. Instead of hardcoding an AI to a specific task, I built a standalone memory and tooling backend using the new Model Context Protocol (MCP). This means any compatible LLM (like Claude or Cursor) can connect to this server, autonomously scrape the web for research, and store that knowledge in a local vector database for future semantic searches—all without vendor lock-in.

## Architecture & Tech Stack

This project solves the "N-to-M integration problem" by completely decoupling the LLM "brain" from the database and tool "hands."

* **Protocol Layer (FastMCP):** Acts as a universal "USB-C port" for AI. It exposes my Python functions to any MCP-compliant LLM via JSON-RPC, making them instantly discoverable.
* **Vector Database (ChromaDB):** Provides local, persistent semantic memory rather than relying on exact keyword matches.
* **Embeddings (`all-MiniLM-L6-v2`):** A lightweight Microsoft model running via ONNX that converts unstructured text into multi-dimensional coordinate vectors entirely locally (zero API costs).
* **ETL Pipeline (`httpx` & `beautifulsoup4`):** A custom web scraper that extracts raw HTML, strips the DOM tags, chunks the text, and loads it directly into ChromaDB.

##  Core Engineering Features

1. **Relevance Filtering (Distance Thresholds):** Vector databases always return *something*, even if it's irrelevant. I implemented a strict mathematical distance threshold (L2 distance) that acts as a filter, dropping low-confidence matches to drastically reduce LLM hallucinations.
2. **Dual-Memory State Sync:** Synchronously maintains state in two places: human-readable markdown files (`.md`) on the hard drive and machine-readable vectors inside ChromaDB.
3. **Agentic Autonomy:** The LLM isn't just a passive chatbot. It independently determines when to trigger the `fetch_and_remember_website` tool to research unknown concepts on the live internet before formulating an answer.

##  Quick Start (Local Setup)

This project uses `uv` for lightning-fast dependency management.

**Install Dependencies**

```bash
# Install uv if you haven't already
curl -LsSf [https://astral.sh/uv/install.sh](https://astral.sh/uv/install.sh) | sh

# Install project requirements
uv add "fastmcp[cli]" chromadb httpx beautifulsoup4

**Run the MCP Server**
To test the tools locally without an external LLM client, launch the FastMCP Inspector UI:
uv run fastmcp dev inspector server.py

**Connect to an LLM Client (e.g., Claude Desktop) **

Add the following configuration to your claude_desktop_config.json:
"mcpServers": {
  "agentic-researcher": {
    "command": "uv",
    "args": ["run", "fastmcp", "run", "server.py"]
  }
}

**Available MCP Tools**
list_notes: Scans the local directory for existing markdown context.

read_note: Ingests the raw text of a specific document into the LLM context window.

save_note: Writes human-readable text to disk and upserts the mathematical embedding into ChromaDB.

search_memory: Converts a user query into a vector and retrieves contextually similar documents based on conceptual meaning.

fetch_and_remember_website: An autonomous scraping agent that cleans external HTML and pipes it directly into semantic memory.