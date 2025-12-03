# Complex sample conversation to test Agent 1's robustness
# Includes ambiguity, feature removal, questions, and spelling mistakes.

complex_conversation = [
    {"role": "user", "content": "I want to build a habit tracker app."},
    {"role": "developer", "content": "Great idea. What specific features do you want?"},
    
    # Spelling mistake: 'dily' instead of 'daily'
    {"role": "user", "content": "I need to be able to log my habits dily."}, 
    {"role": "developer", "content": "Daily logging, got it. What else?"},
    
    # Question, checking feasibility, not yet a requirement
    {"role": "user", "content": "Can I also track my mood with it?"}, 
    {"role": "developer", "content": "Yes, we can add a mood tracker."},
    
    # Feature removal / Change of mind
    {"role": "user", "content": "Actually, nah, let's keep it simple. No mood tracking for now."}, 
    {"role": "developer", "content": "Understood. No mood tracking. Just habit logging."},
    
    # Spelling mistake: 'calender' instead of 'calendar'
    {"role": "user", "content": "I want to see a calender view of my streaks."}, 
    {"role": "developer", "content": "A calendar view for streaks. Anything else?"},
    
    # Ambiguity / Design preference vs Functional requirement
    {"role": "user", "content": "That's it. Oh, and make the buttons blue."}, 
    {"role": "developer", "content": "Blue buttons. Got it. We'll start with that."},
]

# A high-complexity conversation to stress-test the Agent's reasoning capabilities.
# Challenges included:
# 1. Implicit Dependency: User asks for a dashboard but later mentions login (Access Control).
# 2. Double Retraction: Asks for a feature, modifies it, then deletes it.
# 3. Conditional Logic: "If X happens, show Y."
# 4. Visual Vibe: Vague "foresty" request vs specific "red banner" request.
# 5. Data dependency: Cannot view a graph without adding a sensor first.

complex_conversation_v2 = [
    {"role": "user", "content": "I want to make a web dashboard for my smart plant sensors."},
    {"role": "developer", "content": "Sounds cool. What data are we visualizing?"},
    
    # Core Requirement: Data Visualization (Implies dependency: Must have a sensor to visualize)
    {"role": "user", "content": "I have these WiFi sensors that send moisture levels. I want to see a line graph of the moisture over time."},
    {"role": "developer", "content": "Line graph for moisture levels. Noted."},
    
    # Feature 1: Control (The Trap)
    {"role": "user", "content": "Can I also press a button to turn on the water pump remotely?"},
    {"role": "developer", "content": "Sure, we can add a 'Water Now' button."},
    
    # Feature 2: Auth (Late arrival requirement)
    {"role": "user", "content": "Oh wait, I don't want strangers watering my plants. We need a login system."},
    {"role": "developer", "content": "Auth system added. Email and Password?"},
    
    # Refinement: Social Login
    {"role": "user", "content": "Yeah, and allow Google Login too."},
    {"role": "developer", "content": "Google OAuth included."},
    
    # RETRACTION 1 (The Logic Trap): Removing the dangerous feature
    {"role": "user", "content": "Thinking about the water pump... if I accidentally click it while on vacation, I might flood the house. Let's scrap the manual watering button. Read-only for now."},
    {"role": "developer", "content": "Smart move. Removing the 'Water Now' button. Read-only dashboard."},
    
    # RETRACTION 2 (The implementation details): simplifying Auth
    {"role": "user", "content": "Also, setting up Google API keys is annoying. Just stick to email/password login for this version."},
    {"role": "developer", "content": "Understood. Removing Google Login. Email/Pass only."},
    
    # Conditional Logic Requirement
    {"role": "user", "content": "I do need an alert though. If the moisture drops belw 20%, show a big red banner that says 'THIRSTY'."},
    {"role": "developer", "content": "Conditional alert: moisture < 20% = Red 'THIRSTY' banner."},
    
    # Vague UI Requirement
    {"role": "user", "content": "For the rest of the design, make it look kinda foresty. Dark greens, maybe some leaf icons."},
    {"role": "developer", "content": "Forest theme, dark greens, leaf icons. On it."},
    
    # Final confirmation
    {"role": "user", "content": "Perfect. Let's ship it."},
    {"role": "developer", "content": "Building it now."}
]

pitch_hum = [
    {
        "role": "user",
        "content": "# Pitch Against Humanity App: Final Specification\n\nThis document details the complete functionality and user flow for the \"Pitch Against Humanity\" multi-player social game app.\n\n## I. Game Concept\n\nThe objective is for players to pitch a startup idea based on a combination of two randomized cards: a **Product card** and a **Target Audience card**. Pitches should be creative, outrageous, and compelling.\n\n## II. User Flow\n### A. Initial Screen (Home) * **Create Game:** A button labeled \"Create Game\" starts the host flow. * **Join Game Input:** An input field for the **4-digit code** is provided. It should visually use **4 distinct cells** (like an OTP input) to guide the user. * **Join Game Button:** The button labeled \"Join Game\" must be **disabled until a valid 4-digit code is entered**. --- ### B. Game Setup and Joining #### 1. Creating a Game (Host Flow) * **Name & Host Designation:** The player is immediately prompted for their **Name** and is automatically designated as the **Host**. * **Room Code:** A **unique 4-digit room code** is generated and prominently displayed. * **Lobby:** The Host sees a **real-time list** of all players who have joined the room. * **Start Game Control:** The \"Start Game\" button is **enabled only when a minimum of two (2) players** (including the Host) have joined. **Only the Host** can start the game. #### 2. Joining a Game (Player Flow) * **Code Entry:** The player enters the 4-digit room code. * **Game State Check (Crucial):** Before joining, the system must check the game's current status: * If the game has already started, the player is alerted (\"This game is already in progress.\") and the \"Join Game\" button is disabled. * **Name Entry:** If the game is joinable, the player is prompted for their **Name**. --- ### C. Pitching Phase (Sequential) * **Card Distribution:** When the game starts, each player is dealt **two unique cards** (one Product, one Audience). **No card should be reused** in the same room instance. * **Reveal:** The player's cards should be displayed with a **distinct reveal animation** (showing one card, then the next). * **Pitch Trigger:** Each player sees an **\"I Pitch\" button**. * **Turn Management:** Only one player can pitch at a time. * The first player to press **\"I Pitch\"** begins their turn. * For all other players, the screen displays \"$$Name$$ is pitching\" and a **2-minute countdown timer** (this timer must be made configurable later). * **Cycle End:** The phase concludes once **every player** has completed their pitch. --- ### D. Voting Phase (Anonymous) * **Transition:** The screen changes to the **Voting view**. * **Voting:** Each player can cast **one anonymous vote** for **one other player's pitch**. Players **cannot vote for themselves**. --- ### E. Winner Reveal and Resolution * **Reveal:** Once all votes are cast, the winner(s) are revealed. * **Winner Display:** The winning pitch is displayed with an appropriate animation. * **Tie Handling:** * If a tie occurs (multiple players share the highest vote count), a message like **\"It's a Tie!\"** is displayed. * The animation must then showcase all tied winners/pitches. * **Game End Options:** * **\"Return Home\"** (Clears local state and navigates to the initial screen). * **\"Start New Game\"** (All players remain in the current room; the cards are re-drawn, and a new round begins immediately). --- ## III. Data and Technical Requirements ### A. Card Data * Card lists (products and audiences) must reside in an **external file** (e.g., `cards.json`) for easy modification. ### B. Persistent Storage (Firestore) and Cleanup * The app **MUST** use **persistent storage (Firestore)** to manage game state, players, and room codes. * **MANDATORY Database Cleanup Logic:** * **Zero Players Rule:** If the number of active players in a room drops to **zero**, the entire game entry **MUST be deleted immediately**. * **Inactivity Timeout:** If a game room remains empty (**zero active players**) for a configured inactivity timeout period (e.g., **15 minutes, configurable**), the corresponding database entry **MUST be deleted** to ensure data hygiene."
    },
    {
        "role": "user",
        "content": "This is amazing. However when pitching, it should not show a dialog. Just a message saying you're pitching and a button \"End now\". The players are playing in person in the same room."
    }
]