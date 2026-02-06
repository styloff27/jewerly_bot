## JewelryOps Agent

An AI agent for the fictional vertical SaaS company **JewelryOps**.  
The agent helps employees investigate customer issues, orders, returns/refunds, and inventory discrepancies by using tools exposed via **MCP servers** and a few custom helper tools.

---

## 1. How to run it

### Prerequisites

- **Python** 3.10+
- Dependencies from `pyproject.toml` (using `uv` or `pip`)
- **SQLite** (bundled with Python, no extra install needed)
- Optional but recommended: **Ollama** running locally if you switch the LLM to a local model.

### Install dependencies

From the project root:

```bash
uv sync
# or, with pip:
# pip install -e .
```

### Run the CLI agent

From the project root:

```bash
python main.py
```

You’ll get an interactive prompt:

```text
Jewelry Ops Agent CLI. Type 'Ctrl+C' to exit.
You: 
```

Type natural‑language queries (see sample scenarios below) and the agent will run a multi‑step tool‑using loop to investigate and respond.

> Note: MCP servers do **not** need to be started manually.  
> They are launched automatically by the agent via `MultiServerMCPClient` using the `stdio` transport.

---

## 2. Tools and MCP servers

The agent uses tools as its primary way of making progress. There are:

- **3 MCP toolsets (MCP servers backed by SQLite)**  
- **3 custom function tools** to improve reliability and judgment

### 2.1 MCP servers (toolsets)

All MCP servers are implemented with `fastmcp` and backed by the shared SQLite DB in `data/`.

- **Customers MCP (`mcp_servers/customers_server.py`)**  
  Tool names (with MCP client prefix):  
  - `customers_get_customer_tool` – get a single customer by ID  
  - `customers_list_customers_tool` – list all customers  
  - `customers_search_customers_tool` – search by name or email  

- **Orders & Inventory MCP (`mcp_servers/orders_inventory_server.py`)**  
  Tool names:  
  - `orders_inventory_get_order_tool` – get an order by ID  
  - `orders_inventory_list_orders_tool` – list all orders  
  - `orders_inventory_update_order_status_tool` – update order status (with confirmation flow)  
  - `orders_inventory_get_inventory_tool` – get inventory by SKU  
  - `orders_inventory_list_inventory_tool` – list all inventory items  
  - `orders_inventory_update_inventory_tool` – update inventory quantity/unit (with confirmation flow)

- **Notes MCP (`mcp_servers/notes_server.py`)**  
  Tool names:  
  - `notes_get_note_tool` – get note by `(customer_id, order_id)`  
  - `notes_list_notes_for_customer_tool` – list notes for a customer  
  - `notes_list_notes_for_order_tool` – list notes for an order  
  - `notes_add_note_tool` – add a note (with confirmation flow)

The agent loads these tools at startup via:

- `langchain_mcp_adapters.client.MultiServerMCPClient` with three `stdio` connections (one per server)
- `client.get_tools()` which returns LangChain‑compatible tools added to the agent’s toolset

### 2.2 Custom helper tools

Defined in `tools/custom_tools.py` and added directly as LangChain tools:

- **`summarize_conversation_state`**  
  Summarizes recent conversation and tool activity in 1–3 sentences.  
  Used when there are many tool calls and messages and the agent needs to refocus.

- **`extract_entities`**  
  Extracts order IDs, customer IDs, and SKUs from a raw user message.  
  Helps the agent decide which IDs to use for subsequent tool calls.

- **`action_requires_confirmation`**  
  Given a short action description, returns whether explicit user confirmation is required.  
  Encourages the agent to double‑check before calling tools that change data.

---

## 3. How the agent manages context and tool selection

The agent is defined in `agent/core.py` with a LangChain **tool‑calling agent** and an `AgentExecutor`.

- **Looped behavior**  
  The top‑level CLI in `main.py` runs an async loop:
  - read user input → `run_agent(...)` → print result → repeat
  - `run_agent` calls `executor.ainvoke(...)`, allowing the agent to take multiple tool steps per query.

- **Context management**  
  - `chat_history` (past user/assistant messages) is passed into each call.  
  - The system prompt (`agent/prompts.py`) instructs the agent to:
    - prefer tools over guessing,
    - ask clarifying questions when IDs or details are missing,
    - carry information across steps to build a final summary or draft.

- **Tool selection and MCP orchestration**  
  - At startup, `load_mcp_tools()` uses `MultiServerMCPClient` to connect to the 3 MCP servers and load all tools.  
  - These tools are combined with the 3 custom helper tools into a single `tools` list passed to the agent.  
  - The agent chooses which tool to call based on:
    - the system prompt’s guidance (which tool category for which kind of question), and  
    - intermediate observations (e.g., after seeing `CONFIRM_REQUIRED`, it asks the user, then calls the same tool with `confirmed=True`).

- **Confirmation for side effects**  
  - Mutating MCP tools (`orders_inventory_update_order_status_tool`, `orders_inventory_update_inventory_tool`, `notes_add_note_tool`) all accept `confirmed: bool = False`.  
  - When `confirmed=False`, they return a `CONFIRM_REQUIRED: ...` string with instructions.  
  - The agent:
    - surfaces that to the user (e.g., “Are you sure you want to update order 2 to shipped?”),  
    - waits for a clear “yes”, then re‑calls the tool with `confirmed=True`.  

This satisfies the take‑home requirement that the agent runs in a loop, manages context, and asks for confirmation before side effects.

---

## 4. Example demo scenarios

The following are example prompts you can use to demonstrate the agent:

- **Late order complaint & draft response**  
  > “Alice Chen is complaining that order #2 is late. Investigate what’s going on and draft an email I can send her.”

- **Return / refund decision**  
  > “Bob wants to return order #3. Check whether a refund is allowed under our policy and explain your reasoning in a message I can send him.”

- **Inventory discrepancy investigation**  
  > “SKU RING-001 shows zero in stock, but a customer says we had some yesterday. Investigate what might have happened using orders and notes, and summarize what you find.”

Each of these typically triggers multiple tool calls across:

- Customers (CRM MCP),
- Orders & inventory MCP,
- Notes MCP,
- and at least one helper tool (e.g. `extract_entities` or `summarize_conversation_state`).

---

## 5. Notes and extensions

- You can easily switch the LLM backend in `agent/core.py`:
  - From `ChatGoogleGenerativeAI` (Gemini) to a local Ollama model (`ChatOllama`) if desired.
- Additional MCP servers or toolsets can be added by following the same pattern as the existing three.
- The current design keeps MCP servers as thin wrappers around the existing SQLite‑backed tools, so behavior lives in one place and is reusable.

