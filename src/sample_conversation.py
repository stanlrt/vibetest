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
