## JewelryOps Agent – Demo Queries

Use these ready‑made prompts to demonstrate the agent. All are designed to trigger multiple tool calls across the three MCP servers plus helper tools.

---

### Scenario 1 – Late order complaint & draft response

**Query A (recommended):**

```text
Alice Chen is complaining that order #2 is late. Investigate what is going on using the tools and then draft an email I can send her explaining the situation.
```

**Query B (variant):**

```text
A customer named Alice says her order 2 is delayed. Check the order status, any notes on her account, and summarize what happened. Then write a short, polite email I can send to her.
```

What to look for:
- Calls to customer tools, order tools, and notes tools.
- A final drafted email that references real data (status, notes, etc.).

---

### Scenario 2 – Return / refund decision

**Query A (recommended):**

```text
Bob Martinez wants to return order #3. Check whether a refund is allowed under our current policy based on the order details, and explain your reasoning in a message I can send to him.
```

**Query B (variant):**

```text
Customer Bob with order 3 is asking for a refund. Use the tools to check his order and notes, decide if we should approve the refund under our constraints, and draft a response I can send back.
```

What to look for:
- Use of order tools (and possibly notes) before deciding.
- Clear explanation of why a refund is or is not appropriate.

---

### Scenario 3 – Inventory discrepancy investigation

**Query A (recommended):**

```text
SKU RING-001 shows zero in stock, but a customer says they saw it in the store yesterday. Investigate what might have happened using orders, inventory, and notes. Then summarize what you find and suggest next steps.
```

**Query B (variant):**

```text
We have an inventory discrepancy: RING-001 is at quantity 0 in the system. Use the tools to check inventory, related orders, and any notes, and then explain what likely happened and what we should do now.
```

What to look for:
- Calls to inventory tools, order tools, and notes tools.
- A synthesized explanation of the discrepancy and concrete next steps.

