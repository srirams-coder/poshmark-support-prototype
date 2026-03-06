# Case creation flow prototype

Interactive prototype for the **redesigned** support flow: **My Purchases** → **Order Details** → **Problems / Order Inquiry** → context-aware support form → start chat → AI responds.

## How to run

**Start from the first page (recommended):** open **`my_purchases.html`** in a browser.

1. Click any **order row** → opens **`order_details.html`** (order date, number, item, payment/shipping, order status, Ship To, Estimated Delivery, tracking timeline).
2. On the order details page, click **"Problems / Order Inquiry"** → opens **`support_flow.html`** with order context (`source=order`, `order_id=…`).
3. Choose a category, add details, and **Start chat** to see the chat + AI reply.

You can also open `support_flow.html` or `order_details.html` directly (use `?order_id=ord_100_shaving` for order details).

## URL params (context)

- **From order/purchase page (recommended):**  
  `support_flow.html?source=order`  
  or with order id:  
  `support_flow.html?source=order&order_id=12345`  
  → Category dropdown shows **only order-related options** (item not as described, not received, return/refund, etc.).

- **Generic support:**  
  `support_flow.html`  
  → Category dropdown shows **all options** (order + account, selling, app, other).

## Flow in the prototype

1. **My Purchases** → click an order → **Order Details** (order info, Message Seller, Problems / Order Inquiry, Accept Order, Ship To, timeline).
2. **Order Details** → click **Problems / Order Inquiry** → **Support form** (with `source=order` and `order_id`).
3. User selects a **category** (filtered when `source=order`).
4. User enters **details** and clicks **Start chat**.
5. Form view is replaced by **chat view**; the details appear as the **first message**.
6. A **simulated AI reply** appears after a short delay. User can type more messages.

From support, "Back to order" (when opened from an order) returns to the order details page.

## Implementation note

This is front-end only. In production you would:

- Create a case via API when the user clicks **Start chat** (category + details + `order_id` if present).
- Open a real chat thread tied to that case.
- Connect to your AI agent so it receives the first message (and context) and streams replies into the chat.
