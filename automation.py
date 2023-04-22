import argparse
import requests
from bs4 import BeautifulSoup
from notion_client import Client
from googlesearch import search
import secrets_notion

notion = Client(auth=secrets_notion.notion_secret_key)
database_id = secrets_notion.db_id

parser = argparse.ArgumentParser()
parser.add_argument("--movie", help="Enter the name of the movie", type=str)
args = parser.parse_args()

if not args.movie:
    print("Please enter the name of the movie using the --movie flag")
    exit()

movie_name = args.movie
# search for the movie on Google
query = f"{movie_name} imdb"
for url in search(query, num=10):
    if "www.imdb.com/title/" in url:
        imdb_url = url
        break

print(imdb_url)

movie_url = imdb_url


def scrape_movie_info(imdb_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    response = requests.get(imdb_url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    cover = soup.find("meta", property="og:image")["content"]
    name = soup.find("meta", property="og:title")["content"]
    link = imdb_url

    return cover, name, link


def add_movie_to_notion(cover_url, name, link):
    new_page = {
        "Name": {"title": [{"text": {"content": name}}]},
        "link": {"url": link},
        "Media": {
            "files": [
                {
                    "name": "Movie Cover",
                    "external": {
                        "url": cover_url,
                    }
                }
            ]
        }
    }
    notion.pages.create(
        parent={"database_id": database_id}, properties=new_page)


cover, name, link = scrape_movie_info(movie_url)
add_movie_to_notion(cover, name, link)
