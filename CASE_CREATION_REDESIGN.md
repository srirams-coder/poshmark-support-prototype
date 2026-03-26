# Case Creation Flow Redesign

Based on the current flow shown in [your Loom](https://www.loom.com/share/ed455019715543f79fa06e634f762a12): **Orders → Order problem/enquiry → Get customer support → Form → Category → Description → Submit**.

---

## Flow entry: first page = My Purchases

The flow starts on **Order Activity → My Purchases**: the page where the user sees a list of their purchases (product image, title, price, size, seller, order status). From here they identify the order they have a problem with. In the redesigned flow, **clicking that order** (or a “Get support” / “Problem with this order?” action on the row) should take them directly into the support flow with **context already set** (`source=order`, `order_id=…`), so the next screen shows only **order-relevant categories** and can prefill or attach the order.

---

## Current Flow (As-Is)

1. User is on **My Purchases** (Order Activity)
2. Clicks **Order problem / enquiry** (or similar)
3. Clicks **Get customer support** → lands on support form
4. Sees **full category list** (generic, not scoped to orders)
5. Chooses category, enters description, **submits form** (ticket/case created)
6. No immediate conversational follow-up; user waits for email/back-office response

**Pain points:**
- Too many categories when the user already came from “order problem” (redundant choice)
- Form-only experience; no instant dialogue
- No AI to triage or respond in-conversation

---

## Proposed Flow (To-Be)

### 1. Context-aware entry

- **From Purchase/Order page** (e.g. “Problem with this order” or “Get support” on order detail):
  - Pass **context**: `source=order` and optionally `order_id`.
  - Skip generic “Order problem / enquiry” and “Get customer support” clicks; user goes **directly** to a support experience that is **already scoped to orders**.

### 2. Show only relevant categories

- When `source=order` (or from orders → problem/enquiry):
  - **Category dropdown/selection shows only order-related options**, e.g.:
    - Item not as described / wrong item
    - Item not received / shipping issue
    - Return / refund request
    - Order cancelled or delayed
    - Payment or billing issue
    - Other order issue
  - Do **not** show: account issues, selling issues, security, app bugs, etc., in this flow.
- When user comes from **other entry points** (e.g. Help Center, Profile):
  - Either show full category list or another context-specific list (e.g. “Selling”, “Account”).

### 3. Category → Details → Start chat (not just submit form)

- **Step 1:** User selects **one** order-relevant category (required).
- **Step 2:** User enters **details** in a text area (e.g. “Order #XYZ, item never arrived, tracking shows delivered”).
- **Step 3:** User clicks **Start chat** (or “Send” / “Continue”).
  - **Create a case** in the backend (with category + order context + initial message).
  - **Open a chat UI** and post the user’s details as the **first message** in the thread.
- The experience becomes **chat-first**: same case, but the initial submission is the first message and the user stays in a conversation.

### 4. AI agent in chat

- Once the first message is sent:
  - **AI agent** reads: category, order context (if any), and the user’s message.
  - AI responds in the chat (e.g. acknowledgment, next steps, or request for more info).
- User can keep replying in the same thread; AI (and/or human handoff) continues the conversation.
- Case/ticket stays linked to the chat so that human agents see full context when they take over.

---

## Flow Diagram (Proposed)

```
[Step 1: My Purchases]  ← first page of the flow
  Order Activity → My Purchases
  (list of orders: image, title, price, size, seller, status)
        │
        │  User clicks order row or "Get support" on an order
        ▼
[Step 2: Support form with order context]
  URL: ?source=order&order_id=…
  ┌─────────────────────────────────────┐
  │  Category (order-only options)      │
  │  • Item not as described            │
  │  • Not received / shipping          │
  │  • Return / refund                  │
  │  • Cancelled / delayed              │
  │  • Payment / billing                │
  │  • Other order issue                │
  └─────────────────────────────────────┘
        │
        ▼
  ┌─────────────────────────────────────┐
  │  Tell us more (required)            │
  │  [________________________]         │
  │  [     Start chat      ]            │
  └─────────────────────────────────────┘
        │
        ▼
  Case created; chat opens with user message as first message
        │
        ▼
  AI agent replies in chat (e.g. acknowledgment + next steps)
        │
        ▼
  User continues conversation (AI + optional human handoff)
```

---

## Category Mapping (Order context)

| Context        | Categories to show |
|----------------|--------------------|
| **From order** | Item not as described, Not received / shipping, Return / refund, Order cancelled or delayed, Payment / billing, Other order issue |
| **From selling** | Payout, Listing, Buyer issue, Cancellation, Other selling issue |
| **Generic / Help** | Full list or “Order issue”, “Selling issue”, “Account”, “App/technical”, “Other” |

You can refine these labels to match your current taxonomy; the important part is **filtering by entry context**.

---

## Implementation Notes

1. **URL/state:**  
   Use query params or session: `?source=order&order_id=12345` so the support form/chat knows to show order categories and attach the case to that order.

2. **Backend:**  
   - Create case on “Start chat” with: category, order_id (if any), initial message, user_id.  
   - Create chat thread linked to that case; first message = user’s details.

3. **AI agent:**  
   - Input: category, order_id (and order summary if available), first message (and later messages).  
   - Output: replies in the same thread; escalate to human when needed (e.g. “Talk to agent” or after N turns / certain intents).

4. **Analytics:**  
   Track: entry point (order vs other), category chosen, chat started (Y/N), resolution in chat vs handoff.

---

## Summary

- **Context-aware categories:** From order/purchase → show only order-related categories.
- **Details then chat:** User picks category, enters details, clicks “Start chat” → case is created and chat opens with that as the first message.
- **AI in the loop:** AI agent responds in chat; conversation continues in one thread with optional human handoff.

This keeps the same “category + description” information but turns it into a **conversational support experience** and reduces friction (fewer steps, relevant options, immediate response).

---

## Interactive prototype

The prototype has two pages in **`flow_prototype/`**:

1. **`my_purchases.html`** — **First page of the flow.** Matches the My Purchases screen (Order Activity sidebar, list of purchases with image, title, price, size, seller, status). Each row has a **Get support** button that links to the support form with `?source=order&order_id=…`.
2. **`support_flow.html`** — Category (context-aware) → details → **Start chat** → chat view with simulated AI reply.

**To try the full flow:** Open `my_purchases.html`, then click **Get support** on any order. You’ll see only order-relevant categories; after entering details and clicking **Start chat**, the chat opens with your message and an AI response.
