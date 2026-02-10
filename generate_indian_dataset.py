import pandas as pd
import random

# --- CONFIGURATION ---
NUM_SAMPLES = 10000  # Increased for better training

# --- 1. DEFINE PATTERNS (Templates) ---
# Realistic Templates for 2021-2025 Indian News

# REAL NEWS TEMPLATES (Factual, Formal tone)
real_templates = [
    # Politics & Governance
    "Prime Minister Narendra Modi inaugurates {project} in {city}.",
    "{party} wins majority in {state} assembly elections.",
    "Parliament passes the {bill} bill after lengthy debate.",
    "Union Budget 2024 focuses on {sector} and infrastructure growth.",
    "Election Commission announces dates for Lok Sabha polls 2024.",
    # Economy & Business
    "India's GDP growth projected to reach {number}% in FY25, says {org}.",
    "Sensex crosses {sensex_val} mark as markets hit all-time high.",
    "RBI keeps repo rate unchanged at {rate}% in monetary policy review.",
    "Unified Payments Interface (UPI) transactions cross {upi_val} billion in {month}.",
    "Tata Group announces plans to build semiconductor plant in {state}.",
    "Reliance Industries launches new {tech_product} services across India.",
    # Science & Tech
    "ISRO successfully launches {mission} from Sriharikota.",
    "Chandrayaan-3 makes historic soft landing on the Moon's south pole.",
    "India becomes the {rank} country to land on the Moon.",
    # Sports
    "Neeraj Chopra wins gold medal at World Athletics Championships.",
    "India defeats {country} in the Cricket World Cup match at {stadium}.",
    "Virat Kohli scores his {century_count}th international century.",
    "PV Sindhu secures silver medal at {tournament}.",
    # General
    "Government approves {policy} scheme for {group}.",
    "India hosts {event} summit in New Delhi with global leaders.",
    "Monsoon rainfall expected to be normal this year, says IMD.",
    # Simple Facts (To fix the "Narendra Modi is PM" issue)
    "{person_gov} is the Prime Minister of India.",
    "{person_gov} currently serves as the leader of the nation.",
    "New Delhi is the capital city of India.",
    "India is a democratic republic nation.",
    "The currency of India is the Indian Rupee.",
    "{state} is a state located in India.",
    "The President of India resides in Rashtrapati Bhavan.",
    "Hockey is the national sport of India.",
    "The Ganga is a holy river in India.",
    # Bollywood & Entertainment (Real)
    "{actor} signs a new movie with director {director}.",
    "{movie} crosses Rs {box_office} crore mark at the box office.",
    "{actress} wins Best Actress award at Filmfare.",
    "{actor} hosts the new season of Bigg Boss.",
    "Netflix announces new series starring {actor}.",
    "Song '{song}' from {movie} becomes a global hit."
]

# FAKE NEWS TEMPLATES (Sensational, Clickbait, WhatsApp-style, Conspiracy)
fake_templates = [
    # Bollywood Gossip & Hoaxes
    "Shocking: {actor} secretly marries {actress} in private ceremony!",
    "Breaking News: {actor} passes away due to heart attack!",
    "Rumour has it: {actress} is pregnant with triplers!",
    "{actor} arrested for drug possession at Mumbai airport.",
    "Boycott {movie}! It insults our culture, says religious group.",
    # WhatsApp Forwards & Scams
    # WhatsApp Forwards & Scams
    "Forward this message to 10 groups to get free {item} from government.",
    "Click this link to get free recharge of Rs {amount} for {telecom}.",
    "Government is giving free {gadget} to all students. Apply here immediately!",
    "RBI to ban all {note_value} rupee notes from tonight midnight.",
    "If you don't share this, your WhatsApp will be deactivated tomorrow.",
    # Pseudo-Science & Health Hoaxes
    "UNESCO declares {subject} as the best in the world.",
    "NASA satellite image shows India lighting up on Diwali like never before.",
    "Drink {substance} with lemon to cure cancer in 3 days, claims doctor.",
    "Eating {food} causes immediate death according to new study.",
    # Political/Celebrity Fake News
    "Breaking: {person} is secretly an alien from Mars.",
    "Shocking: {celebrity} converts to {religion} secretly.",
    "WikiLeaks releases secret audio of {person} admitting to crimes.",
    "Chip installed in new {note_value} rupee note to track black money.",
    "Hacking alert: Don't answer calls from {phone_num}, your phone will blast.",
    "{person} arrested for corruption in {city} airport."
]

# --- 2. ENTITIES (The "Fill-in-the-blanks") ---
entities = {
    "project": ["Vande Bharat Express", "new AIIMS", "Metro extension", "Expressway", "Solar Park", "Semiconductor Hub", "Bullet Train corridor"],
    "city": ["New Delhi", "Mumbai", "Bengaluru", "Ayodhya", "Varanasi", "Gandhinagar", "Hyderabad", "Chennai", "Kolkata"],
    "mission": ["Aditya-L1", "Gaganyaan", "XPoSat", "PSLV-C56", "NVS-01", "Chandrayaan-3"],
    "number": ["6.5", "7.2", "8.1", "5.9"],
    "org": ["IMF", "World Bank", "RBI", "NITI Aayog", "SBI Research", "Moody's"],
    "party": ["BJP", "Congress", "AAP", "TMC", "DMK"],
    "state": ["Uttar Pradesh", "Karnataka", "Telangana", "Madhya Pradesh", "Rajasthan", "Gujarat", "Maharashtra", "Tamil Nadu"],
    "bill": ["Women's Reservation", "Data Protection", "Telecommunications", "Electricity Amendment"],
    "sector": ["agriculture", "defense", "healthcare", "education"],
    "test_val": ["70,000", "75,000", "80,000"],
    "rate": ["6.5", "6.25", "6.0"],
    "upi_val": ["10", "12", "15"],
    "month": ["August", "October", "December", "January"],
    "tech_product": ["5G", "fiber", "satellite internet"],
    "rank": ["4th", "1st"],
    "country": ["Pakistan", "Australia", "England", "South Africa"],
    "stadium": ["Narendra Modi Stadium", "Eden Gardens", "Wankhede"],
    "century_count": ["50", "80", "75"],
    "tournament": ["Asian Games", "Commonwealth Games", "Olympics"],
    "policy": ["PM-Kisan", "Vishwakarma", "Green Hydrogen", "Drone Didi", "Lakhpati Didi"],
    "group": ["farmers", "women SHGs", "students", "MSMEs"],
    "event": ["G20", "SCO", "Voice of Global South", "International Solar Alliance"],
    "subject": ["National Anthem", "PM Modi", "Indian Currency", "Indian Flag"],
    "item": ["smartphone", "scooter", "recharge", "solar panel"],
    "gadget": ["iPhone 15", "Laptop", "Tablet"],
    "person": ["Rahul Gandhi", "Amit Shah", "Arvind Kejriwal", "Virat Kohli", "Shah Rukh Khan", "Mamata Banerjee"],
    "note_value": ["500", "2000", "100", "50"],
    "telecom": ["Jio", "Airtel", "Vi", "BSNL"],
    "substance": ["hot water", "baking soda", "turmeric", "cow urine"],
    "food": ["Maggi", "Kurkure", "Chicken"],
    "amount": ["5000", "10000", "299", "500"],
    "sensex_val": ["72,000", "65,000", "80,000"],
    "celebrity": ["Salman Khan", "Deepika Padukone", "Akshay Kumar", "Ranbir Kapoor"],
    "religion": ["Hinduism", "Islam", "Christianity", "Buddhism"],
    "person_gov": ["Narendra Modi", "Modi", "PM Modi"],
    "actor": ["Shah Rukh Khan", "Salman Khan", "Aamir Khan", "Hrithik Roshan", "Ranbir Kapoor", "Ranveer Singh"],
    "actress": ["Deepika Padukone", "Alia Bhatt", "Priyanka Chopra", "Katrina Kaif", "Kareena Kapoor"],
    "director": ["Rajkumar Hirani", "Sanjay Leela Bhansali", "Karan Johar", "Rohit Shetty"],
    "movie": ["Jawan", "Animal", "Pathaan", "Tiger 3", "Rocky Aur Rani Kii Prem Kahaani"],
    "song": ["Chaleya", "Jhoome Jo Pathaan", "Besharam Rang", "Tum Kya Mile"],
    "box_office": ["500", "1000", "800", "300"],
}

def fill_template(template):
    result = template
    for key, values in entities.items():
        if "{" + key + "}" in result:
            result = result.replace("{" + key + "}", random.choice(values))
    return result

def generate_dataset():
    print(f"Generating {NUM_SAMPLES} samples of modern Indian news...")
    
    data = []
    
    # Generate balanced dataset
    for _ in range(NUM_SAMPLES // 2):
        # Real News
        tmpl = random.choice(real_templates)
        text = fill_template(tmpl)
        data.append({"text": text, "label": "REAL"})
        
        # Fake News
        tmpl = random.choice(fake_templates)
        text = fill_template(tmpl)
        data.append({"text": text, "label": "FAKE"})
        
    df = pd.DataFrame(data)
    
    # Shuffle
    df = df.sample(frac=1).reset_index(drop=True)
    
    # Save
    df.to_csv("fake_or_real_news.csv", index=False)
    print(f"Dataset generated and saved to fake_or_real_news.csv")
    print("Sample Data:")
    print(df.head())

if __name__ == "__main__":
    generate_dataset()
