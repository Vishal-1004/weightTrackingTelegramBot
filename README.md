# 🏋️‍♂️ Body Weight Tracker Telegram Bot

A highly modular, production-ready Telegram bot built with Python (`pyTelegramBotAPI`) and `SQLite3` designed to help users track their body weight smoothly. The bot features conversational state management, persistent multi-row keyboards, validation engines for custom user entries, and an interactive log manipulation interface (edit/delete) directly through chat.

---

## 🚀 Key Features

- **Seamless Onboarding Process:** Automatically registers new user accounts on their first `/start` interaction and profiles their physical target vector (Weight Loss or Weight Gain goal along with their ultimate target weight).
- **Smart Weight Logging & Upsert Logic:** Users can log daily weights at the click of a button. If an entry already exists for the calendar day, the bot prompts a fuzzy text-matching confirmation system to safely overwrite or preserve records.
- **Dynamic Milestone Progress Reporting:** Computes statistical differentials between starting weight, current weight, and target benchmarks to dynamically output directional emojis (`📈`/`📉`) and progress updates.
- **Full Chronological Ledger Grid:** Provides a beautifully aligned text-based historical ledger formatted inside clean, fixed-width monospaced markdown rows using the `/viewfullreport` command.
- **Interactive Historical Record Manipulation:** Features split-row structural keyboard selectors (`✏️ Delete/Edit Record`) allowing historical manipulation. Includes strict date validation matching (`YYYY-MM-DD`) and multi-tier action confirmations.
- **Resilient Infrastructure Architecture:** Implements connection timeout handling parameters to ensure long-polling recovery during volatile network hiccups or transient server delays.

---

## 🎮 Interface Interaction Manual

Open Telegram, search for your newly customized bot name profile, and utilize the built-in communication UI blocks:

- **`/start` Flow:** Checks user records inside Table 1 (`users`). Returns a welcome banner menu interface matrix to first-time profiles, or routes returning lifecycles straight to their central tracking desk.
- **`📝 Log Weight` Button:** Prompting this input calls up a conversational workflow loop to register numerical float inputs. If inputted twice on the same day, a confirmation prompt prevents accidental entries.
- **`📊 View Progress Report` Button:** Instantly pulls values from Table 2 (`weight_logs`), tracking delta indicators relative to starting inputs and target limits.
- **`✏️ Delete/Edit Record` Button:** Opens an options tray. The system outputs a text ledger data grid layout and requires structural `YYYY-MM-DD` date syntax validation prior to making data changes.

---

## 🔒 Security & Data Schema Architecture

The database contains two core tables bound securely via structural Foreign Key indices:

### Table 1: `users`

- `user_id` (INTEGER PRIMARY KEY) — Bound natively to the permanent unique Telegram account identity vector space.
- `name` (TEXT) — Collected first name data attributes.
- `phone` (TEXT) — Managed parameter for communication options (nullable).
- `goal_type` (TEXT) — Evaluates metrics boundaries (`Loss` / `Gain`).
- `target_weight` (REAL) — Targeted mass weight baseline destination parameters.

### Table 2: `weight_logs`

- `log_id` (INTEGER PRIMARY KEY AUTOINCREMENT) — Unique transaction increment locator.
- `user_id` (INTEGER FOREIGN KEY) — Linked reference route back to Table 1 elements.
- `log_date` (TEXT NOT NULL) — Date stamp strings tracking calendar dates (`YYYY-MM-DD`).
- `weight` (REAL NOT NULL) — Numerical tracked value data fields.
- _Constraints:_ Contains a compound `UNIQUE(user_id, log_date)` schema mapping rule to support clean database level line-item **Upserts**.

---

## 📂 Modular Architecture Layout

The codebase follows a clean, decoupled design separating the routing logic, storage engine, and UI copy configuration elements:

```text
TELEBOT/
│
├── db/                         # Persistent Database Layer
│   ├── __init__.py
│   └── operations.py          # Database schemas, CRUD logic, and upsert engines
│
├── handlers/                   # Bot Event Controllers & Chat Routers
│   ├── __init__.py
│   ├── onboarding.py          # Handles profile initialization /start steps
│   ├── weight_flow.py         # Handles logging, reports, modifications, and confirmations
│   └── common.py              # System /help and /contact static message handlers
│
├── utils/                      # UI Component Layers & Hardcoded Copy Assets
│   ├── __init__.py
│   ├── keyboards.py           # Custom Reply and Inline markup buttons configuration
│   └── text_templates.py      # System Markdown copy and information matrices
│
├── .gitignore                  # Git untracked registry patterns
├── config.py                   # Secure Environment Instance Configurations (Ignored by Git)
├── requirements.txt            # System dependency listing manifest
└── main.py                     # Main Orchestrator and entry polling process runtime
```

## 🛠️ Step-by-Step Local Setup & Installation

Follow these steps to configure your local development environment and launch your bot instance:

### 1. Prerequisites

Ensure you have **Python 3.10+** and **Git** installed on your terminal ecosystem.

### 2. Generate a Telegram API Token Keys

1. Open your Telegram app and search for [@BotFather](https://t.me/BotFather).
2. Initiate a chat session and submit the `/newbot` command.
3. Follow the conversational wizard steps to name your bot and choose a unique username.
4. Copy the generated string payload keys (the `HTTP API Token`). **Keep this key completely secret.**

### 3. Clone the Code Repository

Launch your terminal environment, navigate to your target project folder workspace, and pull down the project files:

```bash
git clone [https://github.com/Vishal-1004/weightTrackingTelegramBot.git](https://github.com/Vishal-1004/weightTrackingTelegramBot.git)
cd weightTrackingTelegramBot
```

### 4. Configure Your Virtual Environment Workspace

Build and activate a clean internal python environment layer to separate your runtime dependencies:

**On Windows (Command Prompt / PowerShell):**

```bash
python -m venv .venv
.\.venv\Scripts\activate
```

**On macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 5. Install Required Project Libraries

Install the structural communication framework wrappers using your setup package manifest:

```bash
pip install -r requirements.txt
```

## 6. Create Environment Configuration Secrets

To safeguard your private keys against public tracking commits, the project incorporates a `.gitignore` framework.

Create a new file named `config.py` inside your project root directory and insert your secret BotFather HTTP token credentials:

```python
# config.py
API_TOKEN = "PASTE_YOUR_REAL_BOTFATHER_HTTP_TOKEN_KEY_HERE"
```

## 7. Run and Test the Application Core Engine

Kick off your main orchestrator script directly from your root project space directory folder:

```bash
python main.py
```

Upon startup, the script will automatically create a local `user.db` file inside your `db/` repository workspace directory and begin polling for live Telegram messages.

---

## 🔮 Future Development Roadmap

## Application-Layer Field Encryption

Integrating cryptography modules to encrypt sensitive customer PII fields (`weight`, `target_weight`, `phone`) using secure AES-256-GCM blocks prior to database ingestion statements.

## Visual Dashboard Analytics

Injecting matplotlib file conversion modules to output beautiful tracking line graphs directly inside chat windows.

## Cloud Infrastructure Syncing

Migrating the local stateful file engine layers to permanent serverless instances like Neon.tech or Supabase PostgreSQL runtimes during Render staging deployment workflows.

# 👤 Developer Profile & Support Contacts

Developed with passion by **Vishal Kumar Yadav**.

For questions regarding structural integration, system scaling, or professional engineering collaborations, reach out via the following channels:

- 📧 **Email:** vishal100403@gmail.com
- 🌐 **LinkedIn:** [Vishal Kumar Yadav](https://www.linkedin.com/in/vishalky104/)
