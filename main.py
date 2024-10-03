import requests
import json
import streamlit as st
from langchain.llms import Ollama

class SportsNewsAgent:
    def __init__(self):
        self.llm = Ollama(model="llama2")
        self.api_key = "YOUR_API_KEY_HERE"  
        self.base_url = "https://api.sportsdataapi.com/v1"
    
    def get_sports_news(self, sport):
        url = f"{self.base_url}/{sport}/news"
        headers = {
            "apikey": self.api_key
        }
        params = {
            "league_id": self.get_league_id(sport),
            "limit": 10  
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            news_data = response.json()
            news_items = []
            for item in news_data.get('data', []):
                news_items.append({
                    "title": item.get('title'),
                    "link": item.get('url'),
                    "summary": item.get('summary')
                })
            return news_items
        else:
            print(f"Error fetching news: {response.status_code}")
            return None
    
    def get_sports_stats(self, sport, team_name):
        url = f"{self.base_url}/{sport}/teams"
        headers = {
            "apikey": self.api_key
        }
        params = {
            "league_id": self.get_league_id(sport)
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            teams_data = response.json()
            for team in teams_data.get('data', []):
                if team['name'].lower() == team_name.lower():
                    return {
                        "name": team['name'],
                        "logo": team.get('logo'),
                        "country": team.get('country', {}).get('name'),
                        "stadium": team.get('stadium')
                    }
            print(f"Team '{team_name}' not found.")
            return None
        else:
            print(f"Error fetching team data: {response.status_code}")
            return None
    
    def get_league_id(self, sport):
        pass
    
    def generate_summary(self, news_items):
        news_text = "\n".join([f"{item['title']}: {item['summary']}" for item in news_items])
        summary = self.llm(f"Summarize the following sports news:\n{news_text}")
        return summary

def main():
    st.title("Sports News and Stats Agent")
    
    agent = SportsNewsAgent()
    
    st.header("Get Sports News")
    sport = st.selectbox("Select a sport:", ["soccer", "basketball", "american-football"])
    if st.button("Get News"):
        news = agent.get_sports_news(sport)
        if news:
            st.write("Latest Sports News:")
            for item in news:
                st.write(f"[{item['title']}]({item['link']})")
                st.write(item['summary'])
            summary = agent.generate_summary(news)
            st.write("Summary:")
            st.write(summary)
        else:
            st.write("No news found.")
    
    st.header("Get Team Statistics")
    team = st.text_input("Enter a sports team name:")
    if st.button("Get Stats"):
        stats = agent.get_sports_stats(sport, team)
        if stats:
            st.image(stats['logo'], width=100)
            st.write(f"**Team:** {stats['name']}")
            st.write(f"**Country:** {stats['country']}")
            st.write(f"**Stadium:** {stats['stadium']}")
        else:
            st.write("Error fetching stats.")

if __name__ == "__main__":
    main()