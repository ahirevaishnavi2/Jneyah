"""
20 TEST SAMPLES FOR THREAT DETECTION
Copy this entire code into test_samples.py
"""

TEST_SAMPLES = [
    # PHISHING (4 samples)
    ("URGENT: Your bank account suspended. Click: http://bit.ly/fake", "phishing"),
    ("PayPal verify account now: paypal-login.com", "phishing"),
    ("Netflix password expired. Update now", "phishing"),
    ("Facebook security alert. Login to verify", "phishing"),
    
    # SCAM (3 samples)
    ("You won $100,000 lottery! Call now", "scam"),
    ("FREE iPhone 15! Just pay shipping", "scam"),
    ("Make $10,000 weekly guaranteed", "scam"),
    
    # HARASSMENT (3 samples)
    ("I will hurt you tonight", "harassment"),
    ("You are worthless garbage", "harassment"),
    ("Kill yourself", "harassment"),
    
    # MALWARE (3 samples)
    ("Download invoice.exe", "malware"),
    ("Install update.scr", "malware"),
    ("Open video_player.bat", "malware"),
    
    # FRAUD (3 samples)
    ("Your SSN 123-45-6789 was stolen", "fraud"),
    ("Credit card needs verification", "fraud"),
    ("IRS tax refund requires bank login", "fraud"),
    
    # SAFE (4 samples)
    ("Hey meeting tomorrow at 3pm?", "safe"),
    ("Thanks for the report", "safe"),
    ("Pick up milk", "safe"),
    ("See you later", "safe"),
]

# ========== ADD THIS AT THE BOTTOM ==========
if __name__ == "__main__":
    print(f"✅ Created {len(TEST_SAMPLES)} test samples")
    print("Categories available:", set(category for _, category in TEST_SAMPLES))
    
    print("\nFirst 3 samples:")
    for i in range(3):
        print(f"{i+1}. '{TEST_SAMPLES[i][0]}' -> {TEST_SAMPLES[i][1]}")
# ========== END OF ADDITION ==========
