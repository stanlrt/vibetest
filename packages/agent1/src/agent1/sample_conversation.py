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
