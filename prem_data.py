import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3

# Function to scrape the website
def scrape_footystats(url):
    url = url  
    #url1 = 'https://footystats.org/england/premier-league'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print("Website scraped successfully")
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup
    else:
        print("Failed to retrieve the data")
        return None

# Function to parse and extract the required data
def parse_data(soup):
    # Example: Extracting data from a specific table (modify according to the site's structure)
    stats = []
    basic_table = soup.find('table', {'class': 'mt1e comparison-table-table w100'})  # Replace 'stats-table' with the actual class of the table
    rows = basic_table.find_all('tr')
    for row in rows[1:8]:  # Skipping the header row
        cols = row.find_all('td')
        match_data = {
            'Stats': cols[0].text.strip(),
            'Overall': cols[1].text.strip(),
            'At Home': cols[2].text.strip(),
            'At Away': cols[3].text.strip()
        }
        stats.append(match_data)
    print(stats)
    return stats

# Function to save data to SQLite database
def save_to_database(spurs_stats, oppo_stats):
    # Connect to SQLite DB (or create it)
    conn = sqlite3.connect('premier_league_data.db')
    cursor = conn.cursor()

    # Create a spurs stats table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS spurs_stats (
            id INTEGER PRIMARY KEY,
            Stats TEXT,
            Overall TEXT,
            Home TEXT,
            Away TEXT
        )
    ''')

    #delete old data before inserting new data
    cursor.execute('DELETE FROM spurs_stats')

    # Insert match data into the table
    for stat in spurs_stats:
        cursor.execute('''
            INSERT INTO spurs_stats (Stats, Overall, Home, Away)
            VALUES (?, ?, ?, ?)
        ''', (stat['Stats'], stat['Overall'], stat['At Home'], stat['At Away']))

    # Create a opposition stats table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS oppo_stats (
            id INTEGER PRIMARY KEY,
            Stats TEXT,
            Overall TEXT,
            Home TEXT,
            Away TEXT
        )
    ''')

    #delete old data before inserting new data
    cursor.execute('DELETE FROM oppo_stats')

    # Insert match data into the table
    for stat in oppo_stats:
        cursor.execute('''
            INSERT INTO oppo_stats (Stats, Overall, Home, Away)
            VALUES (?, ?, ?, ?)
        ''', (stat['Stats'], stat['Overall'], stat['At Home'], stat['At Away']))


    # Commit and close the database connection
    conn.commit()
    print("Data saved to database successfully")
    cursor.execute('SELECT * FROM spurs_stats')
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    print('--------------------------------')
    cursor.execute('SELECT * FROM oppo_stats')
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    
    conn.close()

# Main function to run the process
def main():
    spurs_soup = scrape_footystats('https://footystats.org/clubs/tottenham-hotspur-fc-92#')
    #automate getting opposition teams stats for each match
    oppo_soup = scrape_footystats('https://footystats.org/clubs/crystal-palace-fc-143') 
    
    if spurs_soup and oppo_soup:
        spurs_stats = parse_data(spurs_soup)
        oppo_stats = parse_data(oppo_soup)
        save_to_database(spurs_stats, oppo_stats)
        print(f'{len(spurs_stats)} rows saved to spurs stats table and {len(oppo_stats)} rows saved to opposition stats table.')

if __name__ == '__main__':
    main()


