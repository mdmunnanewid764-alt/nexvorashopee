# 🛍️ Nexvora Shopee Telegram Bot

A complete, feature-packed Telegram E-Commerce and Digital Goods Shop Bot with automated cryptocurrency deposits via **Binance Pay & Multi-Chain (BEP20, TRC20, ERC20)**.

---

## 🌟 Key Features

### 👤 Customer Experience
- **Interactive Shop & Catalog**: Browse categories and products with photos, prices, descriptions, and real-time stock levels.
- **Wallet & Balance System**: Add funds, view balance, and track spending history.
- **Instant Binance Pay & Multi-Chain Deposits**:
  - **Binance Pay** (0% Gas, 1-Click checkout in Binance App / Web).
  - **USDT - BEP20 (BNB Smart Chain)**.
  - **USDT - TRC20 (TRON Network)**.
  - **USDT - ERC20 (Ethereum Network)**.
  - Generates payment QR codes & copyable addresses.
  - Real-time automatic background deposit verification & instant wallet balance crediting.
  - Submit On-Chain TxHash verification.
- **Instant Digital Delivery**: Auto-delivers accounts, keys, codes, licenses upon balance checkout.
- **Manual Orders**: Submit custom order requirements for admin fulfillment.
- **Order History**: View past orders, keys, and receipts anytime with `/orders` or menu.

### 🛠️ Admin Dashboard (`/admin` or Chat ID: `6575066703`)
- **Category Management**: Add, emoji customisation, and delete categories.
- **Product Management**:
  - Step-by-step product creator with photo URLs, descriptions, and prices.
  - Support for both **Digital Auto-Stock** and **Manual Services**.
- **Stock Management**:
  - Bulk stock upload (paste accounts/keys line-by-line).
  - Real-time stock counts.
- **User Management**:
  - Search users by Telegram ID.
  - Manually credit or debit user balances.
- **Broadcast Announcements**: Send rich formatted messages to all active users.
- **Dynamic Settings**: Update Merchant API Key, Currency symbol, Support username, and Minimum Deposit directly in Telegram.
- **Sales & Deposit Analytics**: Live statistics on total orders, revenue, deposits, and users.

---

## 🚀 How to Run

### 1. Requirements
- Python 3.10+ installed
- Dependencies in `requirements.txt`

### 2. Configuration (`.env`)
```env
BOT_TOKEN=8864898167:AAH5cSW1zJEUC6MXP3c6rz7DQY1WsMDgj3U
ADMIN_ID=6575066703
BINANCE_API_BASE_URL=https://binance-api-yrz4.onrender.com
BINANCE_API_KEY=bg_live_your_merchant_api_key
CURRENCY_SYMBOL=$
CURRENCY_NAME=USDT
SUPPORT_USERNAME=@Support
MIN_DEPOSIT=1.0
```

### 3. Launch
Double click `run_bot.bat` or run:
```bash
python bot.py
```

---

## 🤖 Bot Commands

| Command | Description |
| :--- | :--- |
| `/start` | Open store main menu & welcome dashboard |
| `/products` or `/buy` | Browse product categories & items |
| `/status <ID>` | Check status of an order or deposit invoice |
| `/admin` | Open Admin Control Panel (Admin only) |
