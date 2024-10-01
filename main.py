import requests
import json
from bs4 import BeautifulSoup
import streamlit as st
from langchain.llms import Ollama  # Ensure this is properly imported

class SportsNewsAgent:
    def __init__(self):
        self.llm = Ollama(model="llama2")  # Replace with the appropriate model name

    def get_sports_news(self, topic):
        """
        Fetches sports news related to the given topic using DuckDuckGo.
        """
        search_url = f"https://duckduckgo.com/?q={topic}+sports&ia=news"
        print("Search URL:", search_url)  # Debug URL
        response = requests.get(search_url)
        print("Response Text:", response.text)  # Debug the full response

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract news headlines and links
        news_items = []
        for item in soup.find_all('a', class_='result__a'):
            title = item.get_text()
            link = item['href']
            if title and link:
                news_items.append({"title": title, "link": link})

        if not news_items:
            print("No news items found in the parsed HTML.")  # Debug for empty news items

        return news_items

    def get_sports_stats(self, team):
        """
        Fetches statistics for a given sports team using the unofficial ESPN API.
        """
        # Constructing the URL for the ESPN API (example endpoint)
        url = f"https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams/{team.lower().replace(' ', '-')}"
        print(f"Request URL: {url}")  # Debug URL

        response = requests.get(url)

        # Print the response text for debugging
        print("Response Text:", response.text)

        if response.status_code == 200:
            try:
                data = json.loads(response.text)
                # Modify according to the actual structure of the ESPN API response
                team_data = {
                    "name": data['team']['name'],
                    "logo": data['team']['logos'][0]['href'],  # Adjust according to actual response structure
                    "stadium": data['team']['venue']['name'],  # Adjust according to actual response structure
                    "description": data['team']['description'],  # Adjust according to actual response structure
                }
                return team_data
            except json.JSONDecodeError as e:
                print("JSON decoding error:", e)
                return None
        else:
            print("Error fetching data:", response.status_code)
            return None

    def generate_summary(self, news_items):
        """
        Generates a summary of the sports news using Ollama.
        """
        news_text = "\n".join([f"{item['title']}: {item['link']}" for item in news_items])
        summary = self.llm(f"Summarize the following sports news:\n{news_text}")
        return summary


# Streamlit app
def main():
    st.title("Sports News and Stats Agent")

    agent = SportsNewsAgent()

    # Sports news section
    st.header("Get Sports News")
    topic = st.text_input("Enter a sports topic (e.g., Football, NBA):")
    if st.button("Get News"):
        news = agent.get_sports_news(topic)
        if news:
            st.write("Latest Sports News:")
            for item in news:
                st.write(f"[{item['title']}]({item['link']})")
            summary = agent.generate_summary(news)
            st.write("Summary:")
            st.write(summary)
        else:
            st.write("No news found.")

    # Sports statistics section
    st.header("Get Team Statistics")
    team = st.text_input("Enter a sports team name (e.g., New England Patriots):")
    if st.button("Get Stats"):
        stats = agent.get_sports_stats(team)
        if stats:
            st.image(stats['logo'], width=100)
            st.write(f"**Team:** {stats['name']}")
            st.write(f"**Stadium:** {stats['stadium']}")
            st.write(f"**Description:** {stats['description']}")
        else:
            st.write("Error fetching stats.")

if __name__ == "__main__":
    main()