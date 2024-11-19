#!/usr/bin/dev python3
import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify
from dotenv import load_dotenv
import os

app = Flask(__name__)

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
STREAM_URL_PREFIX = os.getenv("STREAM_URL_PREFIX")

# Function to scrape Broadcastify
def scrape_top_feeds():
    response = requests.get(BASE_URL)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the table with class 'btable'
    table = soup.find('table', class_='btable')
    rows = table.find_all('tr')[1:]  # Skip the header row

    feeds_data = []

    for row in rows:
        cells = row.find_all('td')

        # Extract listeners count
        listeners = int(cells[0].text.strip())
        
        # Extract the feed name and its link
        feed_cell = cells[2]
        feed_name = feed_cell.find('a').text.strip()
        feed_link = feed_cell.find('a')['href']
        feed_id = feed_link.split('/')[-1]
        
        # Build the audio stream URL
        audio_url = f"{STREAM_URL_PREFIX}{feed_id}"

        feeds_data.append({
            "listeners": listeners,
            "name": feed_name,
            "id": feed_id,
            "url": audio_url
        })

    return feeds_data

# Endpoint to get top feeds
@app.route('/api/feeds', methods=['GET'])
def get_feeds():
    try:
        feeds = scrape_top_feeds()
        return jsonify(feeds), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to get a specific feed by ID
@app.route('/api/feed/<feed_id>', methods=['GET'])
def get_feed_audio(feed_id):
    try:
        audio_url = f"{STREAM_URL_PREFIX}{feed_id}"
        return jsonify({"url": audio_url}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
