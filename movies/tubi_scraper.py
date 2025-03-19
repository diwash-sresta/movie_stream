import requests
from bs4 import BeautifulSoup

def get_tubi_movies():
    url = "https://tubitv.com/category/action"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    movies = soup.find_all("a", class_="Thumbnail__StyledThumbnail-sc-1ng2vnp-0")

    movie_list = []
    for movie in movies[:10]:  # Get first 10 movies
        title = movie["aria-label"]
        link = "https://tubitv.com" + movie["href"]
        movie_list.append({"title": title, "link": link})

    return movie_list
