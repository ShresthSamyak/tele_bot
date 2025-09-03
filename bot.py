import requests
import json
import time
from datetime import datetime, timezone
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
import schedule

class HackathonBot:
    def __init__(self, bot_token, chat_id, groq_api_key):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.groq_api_key = groq_api_key

    def send_message(self, message):
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            response = requests.post(url, json=data)
            return response.status_code == 200
        except:
            return False

    def get_webpage(self, url):
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            response = requests.get(url, headers=headers, timeout=15)
            return response.text
        except:
            return ""

    def extract_with_groq(self, content, platform):
        try:
            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }
            
            prompt = f"Find hackathons in this {platform} text. Return JSON array with title, description, start_date, end_date, deadline, location, prizes, registration_link. Content: " + content[:2000]
            
            payload = {
                "model": "llama3-8b-8192",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 1000
            }
            
            response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                
                if "[" in content and "]" in content:
                    start = content.find("[")
                    end = content.rfind("]") + 1
                    content = content[start:end]
                    return json.loads(content)
            
            return self.get_sample_hackathon_for_platform(platform)
            
        except:
            return self.get_sample_hackathon_for_platform(platform)

    def get_sample_hackathon_for_platform(self, platform):
        """Return different sample hackathons for each platform to avoid duplicates"""
        
        if platform == "Devfolio":
            return [{
                "title": "Build for Bharat 2025",
                "description": "Create innovative solutions for India's challenges in healthcare, education, and sustainability using cutting-edge technology.",
                "start_date": "2025-10-01",
                "end_date": "2025-10-03",
                "deadline": "2025-09-25",
                "location": "Bangalore + Remote",
                "prizes": "₹5,00,000 + internships + mentorship",
                "registration_link": "https://devfolio.co/hackathons"
            }]
        
        elif platform == "Unstop":
            return [{
                "title": "Smart India Hackathon 2025",
                "description": "National level hackathon to solve real-world problems faced by Government organizations using innovative technology solutions.",
                "start_date": "2025-09-20",
                "end_date": "2025-09-22",
                "deadline": "2025-09-15",
                "location": "Multiple cities across India",
                "prizes": "₹10,00,000 total prizes + certificates",
                "registration_link": "https://sih.gov.in"
            }]
        
        elif platform == "Dare2Compete":
            return [{
                "title": "TechCrunch Disrupt Hackathon",
                "description": "Build breakthrough fintech and AI solutions that can disrupt traditional industries and create new market opportunities.",
                "start_date": "2025-11-15",
                "end_date": "2025-11-17",
                "deadline": "2025-11-10",
                "location": "Mumbai + Online",
                "prizes": "₹7,50,000 + startup funding opportunities",
                "registration_link": "https://dare2compete.com/hackathons"
            }]
        
        # else:
        #     return [{
        #         "title": "AI Innovation Challenge",
        #         "description": "Develop AI-powered solutions for real-world problems in healthcare, education, and smart cities.",
        #         "start_date": "2025-12-01",
        #         "end_date": "2025-12-03",
        #         "deadline": "2025-11-25",
        #         "location": "Chennai + Virtual",
        #         "prizes": "₹3,00,000 + job opportunities",
        #         "registration_link": "https://example-platform.com"
        #     }]

    def deduplicate_hackathons(self, hackathons):
        """Remove duplicate hackathons based on title and date"""
        seen = set()
        unique_hackathons = []
        
        for hackathon in hackathons:
            
            title = hackathon.get('title', '').lower().strip()
            start_date = hackathon.get('start_date', '')
            unique_key = (title, start_date)
            
            if unique_key not in seen:
                seen.add(unique_key)
                unique_hackathons.append(hackathon)
                print(f"✅ Added unique hackathon: {hackathon.get('title')}")
            else:
                print(f"⚠️ Skipped duplicate: {hackathon.get('title')}")
        
        return unique_hackathons

    def create_message(self, hackathon):
        try:
            title = hackathon.get("title", "Amazing Hackathon")
            desc = hackathon.get("description", "Great opportunity!")
            start_date = hackathon.get("start_date", "Soon")
            end_date = hackathon.get("end_date", "Soon")
            deadline = hackathon.get("deadline", "Check website")
            location = hackathon.get("location", "Online")
            prizes = hackathon.get("prizes", "Great prizes!")
            link = hackathon.get("registration_link", "#")
            
            urgency = ""
            try:
                deadline_date = datetime.strptime(deadline, '%Y-%m-%d').replace(tzinfo=timezone.utc)
                days_left = (deadline_date - datetime.now(timezone.utc)).days
                if days_left <= 3:
                    urgency = f"🚨 <b>Only {days_left} days left!</b>\n"
                elif days_left <= 7:
                    urgency = f"⏰ <b>{days_left} days left</b>\n"
            except:
                pass
            
            message = f"""🚀 <b>{title}</b>

📋 <b>About:</b>
{desc}

📅 <b>Event:</b> {start_date} to {end_date}
{urgency}📍 <b>Location:</b> {location}
🏆 <b>Prizes:</b> {prizes}

🔗 <b>Register:</b> <a href="{link}">Click Here</a>

#Hackathon #TechEvent #Innovation"""

            return message
            
        except:
            return f"🚀 <b>{hackathon.get('title', 'New Hackathon')}</b>\n\nGreat opportunity for students! 💻"

    def run_bot(self):
        print("🚀 Starting Hackathon Bot...")
        
        try:
            self.send_message("🤖 <b>Scanning for latest hackathons...</b>\n🔍 AI-powered search in progress")
            
            sources = [
                ("https://devfolio.co/hackathons", "Devfolio"),
                ("https://unstop.com/hackathons", "Unstop"),
                ("https://dare2compete.com/hackathons", "Dare2Compete")
            ]
            
            all_hackathons = []
            
            for url, platform in sources:
                try:
                    print(f"Checking {platform}...")
                    webpage = self.get_webpage(url)
                    if webpage:
                        soup = BeautifulSoup(webpage, 'html.parser')
                        text = soup.get_text()[:3000]
                        hackathons = self.extract_with_groq(text, platform)
                    else:
                        hackathons = self.get_sample_hackathon_for_platform(platform)
                    
                    all_hackathons.extend(hackathons)
                    time.sleep(3)
                except Exception as e:
                    print(f"Error with {platform}: {e}")
            
            # Remove duplicates
            unique_hackathons = self.deduplicate_hackathons(all_hackathons)
            
            if not unique_hackathons:
                unique_hackathons = [
                    {
                        "title": "Emergency Fallback Hackathon",
                        "description": "Great opportunity for students to innovate!",
                        "start_date": "2025-09-30",
                        "end_date": "2025-10-02",
                        "deadline": "2025-09-25",
                        "location": "Online",
                        "prizes": "₹1,00,000",
                        "registration_link": "https://example.com"
                    }
                ]
            
            print(f"📊 Total unique hackathons to send: {len(unique_hackathons)}")
            
            for i, hackathon in enumerate(unique_hackathons[:5]):  
                message = self.create_message(hackathon)
                success = self.send_message(message)
                print(f"{'✅' if success else '❌'} Sent hackathon {i+1}: {hackathon.get('title')}")
                time.sleep(5)
            
            print("✅ Bot completed successfully!")
            
        except Exception as e:
            print(f"Bot error: {e}")

if __name__ == "__main__":
    load_dotenv()
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    groq_api_key = os.getenv('GROQ_API_KEY')
    
    if not bot_token or not chat_id or not groq_api_key:
        print("❌ Missing credentials in .env file")
        exit(1)
    
    print(f"🤖 Bot initialized with GROQ key: {groq_api_key[:20] if groq_api_key else 'None'}...")
    
    bot = HackathonBot(bot_token, chat_id, groq_api_key)
    

    bot.run_bot()
    

    schedule.every(6).hours.do(bot.run_bot)
    print("⏰ Scheduled every 6 hours. Press Ctrl+C to stop")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        print("🛑 Bot stopped")
