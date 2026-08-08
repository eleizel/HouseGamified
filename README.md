# 🏡 Home Quest: Gamified Household Task Manager

**Home Quest** (originally *Gestor de Tareas Gamificado*) is a modern, interactive, and beautifully designed web application that transforms mundane, tedious household chores into an engaging RPG-style progression system. Built on top of **Streamlit**, it allows households to create players, complete daily, weekly, monthly, and yearly quests, gain Experience Points (XP), level up, and redeem points for actual, real-life rewards!

---

## ✨ Features

### 👤 RPG Player Progression
*   **Custom Player Profiles:** Every household member has a dedicated profile tracking their Level, Title, XP, and redeemable points.
*   **99 Custom Levels:** A progression system configured from a JSON file, starting from `Apprentice del Plumero 🧹` (Level 1) all the way to `Tomb Raider de la Limpieza Extrema 👑` (Level 99), with funny, relatable Spanish household titles.
*   **XP Progress Bar:** Live visual feedback on how close you are to the next level.

### 📋 Quest Board (Tablón de Misiones)
*   **Categorized Household Tasks:**
    *   ☀️ **Daily Tasks:** Short, daily routines (e.g., sweeping, making the bed, cleaning the litter box).
    *   📅 **Weekly Tasks:** Medium-sized chores (e.g., changing bedsheets, dusting, deep cleaning the bathroom).
    *   🗓️ **Monthly Tasks:** Deep cleaning and monthly upkeep (e.g., cleaning the oven/microwave, washing curtains).
    *   🏆 **Yearly Tasks (Epic Challenges):** High-effort, seasonal overhauls (e.g., deep kitchen clean, organizing the storage room).
*   **Repeatability Controls:** Tasks can be flagged as repeatable with set limits per period (e.g., doing a task up to 3 times in a single day/week).
*   **Concurrency Validation:** The app automatically cross-references and updates server data upon completing a task to prevent players from claiming XP for a task that has already reached its periodic limit.

### 🛍️ Reward Store (Tienda de Recompensas)
*   **Redeem Points:** Experience Points act as currency in the store! Complete chores to earn points, and spend them to buy reward tickets.
*   **Built-in Perks:** Redeem points for exciting real-life perks such as:
    *   🎬 *Choosing the weekend movie/series*
    *   🍕 *Ordering favorite takeout*
    *   🎟️ *A "free-from-daily-chore" pass*
    *   🎁 *A personal monthly gift*
*   **Interactive Reward Pipeline:** Redeemed rewards are kept "ongoing" in the player's sidebar until physically enjoyed. Players mark them as "enjoyed" to log them as completed and clean up their profile.

### 📊 Social & Accountability Tools
*   **📜 History Log:** A comprehensive household feed tracking all tasks completed, rewards redeemed, and rewards enjoyed, ordered chronologically.
*   **🏆 Leaderboard (Ranking):** A live table ranking all players by total accumulated XP, showing their current level, title, and completed mission count.

### ⚙️ Administrator Panel & User Management
*   **Onboard Players:** Administrators can create new user accounts directly from the sidebar. Password hashes are generated securely on the fly using `bcrypt`.
*   **Custom Quest Creator:** Create, update, and delete custom tasks with personalized XP awards, periodicity, and repeatability rules directly through the web interface.

---

## 🛠️ Core Technology Stack

*   **Frontend & UI:** [Streamlit](https://streamlit.io/) (utilizing tabs, custom sidebar layout, columns, metric badges, progress bars, balloons/snow effects, and forms).
*   **Authentication & Security:** [Streamlit Authenticator](https://github.com/moezbhatti/streamlit-authenticator) for robust login/cookie session management and [bcrypt](https://pypi.org/project/bcrypt/) for password hashing.
*   **Data Storage:** Lightweight, filesystem-persistent JSON databases (`gamificacion_datos.json` and `niveles.json`) for effortless deployment.

---

## 📂 Project Structure

The project has been refactored into modular directories to keep code readable, testable, and tidy:

```text
HouseGamified/
│
├── app.py                      # Main entrypoint & UI layout orchestrator
│
├── core/                       # Service Layer (Business Logic & Data Access)
│   ├── __init__.py             # Package marker
│   ├── data_manager.py         # JSON database transaction, initialization & migrations
│   └── game_logic.py           # XP calculations, dynamic limits & preloaded lists
│
├── components/                 # View Layer (Streamlit UI Modules & Tabs)
│   ├── __init__.py             # Package marker
│   ├── sidebar.py              # Sidebar rendering (profiles, progress, reward checklist)
│   ├── quests_tab.py           # Quest Board layout & completion triggers
│   ├── rewards_tab.py          # Reward Store tab
│   ├── history_tab.py          # Chronological timeline feed tab
│   ├── ranking_tab.py          # Scoreboard & players ranking tab
│   └── admin_tab.py            # Forms to manage custom quests (Admin only)
│
├── requirements.txt            # Python dependencies (Streamlit, Authenticator, bcrypt)
├── niveles.json                # JSON configuration detailing 99 levels, XP requirements & titles
├── gamificacion_datos.json     # Local JSON database containing accounts, users, history, and custom tasks
└── README.md                   # This English documentation file
```

---

## 🏗️ Under the Hood: Service-View Architecture

By separating concerns into `core/` and `components/`, the codebase solves several common challenges of single-file Streamlit scripts:

1.  **State Cleanliness:** All read/write persistence is moved to `core/data_manager.py`. The GUI components simply bind to the loaded dictionary or request a rewrite, avoiding scattered file operations.
2.  **Modularized Presentation:** Each tab inside `app.py` is a standalone component. This means files like `components/quests_tab.py` are small, focused, and only import the dependencies they need.
3.  **Anti-Duplication State:** Because of Streamlit's rerun nature, custom tasks loaded dynamically from JSON are prone to duplicate memory entries. `core/game_logic.py` intercepts this by restoring standard defaults before overlaying personalized entries in a safe deep copy routine.

---



## 🚀 Installation & Setup

Follow these steps to run Home Quest locally on your machine:

### 1. Prerequisites
Ensure you have Python 3.9 or higher installed on your system.

### 2. Clone the Repository
Clone this repository to your local workspace:
```bash
git clone https://github.com/your-username/HouseGamified.git
cd HouseGamified
```

### 3. Create a Virtual Environment
It is highly recommended to isolate your dependencies using a virtual environment:

**On Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install Dependencies
Install the required packages listed in `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 5. Running the Application
Launch the Streamlit server:
```bash
streamlit run app.py
```
This command will start a local server and automatically open the application in your default web browser (usually at `http://localhost:8501`).

---

## 👥 Preconfigured Accounts & Security

Out of the box, `app.py` initializes two administrator accounts within `INITIAL_ACCOUNTS`:
*   **Sergio** (Admin)
*   **Raquel** (Admin)

If you are deploying this for your own household:
1.  On the first launch, the app creates a secure database in `gamificacion_datos.json`.
2.  Log in with your pre-established household credentials.
3.  As an **admin**, navigate to the sidebar to onboard other players, or use the **Administrar Tareas** tab to set up customized tasks for your household.
4.  To change admin passwords, you can replace the hashed passwords directly in `INITIAL_ACCOUNTS` in `app.py` or modify the password hash inside the `gamificacion_datos.json` file.

---

## 🎮 Gameplay Mechanics & Rules

1.  **Chore Cycles:** Daily tasks reset every calendar day. Weekly tasks reset every Monday (ISO calendar week). Monthly tasks reset on the 1st of the month. Yearly tasks reset on January 1st.
2.  **Double-Claims Safeguard:** If two users try to complete the same non-repeatable task at the same time, only the first user who clicks "Complete" gets the XP. The second user receives an alert that the task is already completed for that period.
3.  **Gold Currency (Points):** Redeemable points are calculated on a $1:1$ ratio with earned XP. When you buy a reward in the Store, your **Points** decrease by the cost of the reward, but your **Total XP** (which controls your Level and Titles) remains intact.

---

## 🎨 Customizing Levels (`niveles.json`)

You can fully customize the level progression and titles to match your household's inside jokes or language. Open `niveles.json` and adjust the progression:

```json
{
    "niveles": [
        {
            "nivel": 1,
            "xp_minimo": 0,
            "titulo": "Apprentice del Plumero 🧹",
            "xp_siguiente": 300
        },
        ...
    ]
}
```
*   `nivel`: The integer level number (1-99).
*   `xp_minimo`: The total minimum XP required to reach this level.
*   `titulo`: The funny, thematic title awarded to players at this level.
*   `xp_siguiente`: The threshold XP for the next level (set to `null` for the maximum level, level 99).

---

## 🛡️ License

This project is open-source and available under the [MIT License](LICENSE) (or any license your household/team prefers). Enjoy a cleaner, happier, and more playful home! Game on! 🎮🏡
