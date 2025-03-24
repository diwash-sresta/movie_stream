import requests
from bs4 import BeautifulSoup
import time
import random
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_tubi_movies(category="action", limit=20):
    """
    Scrape movies from Tubi TV by category
    
    Args:
        category (str): Movie category to scrape (action, comedy, drama, horror, etc.)
        limit (int): Maximum number of movies to return
        
    Returns:
        list: List of dictionaries containing movie information
    """
    url = f"https://tubitv.com/category/{category}"
    
    # Rotate user agents to avoid being blocked
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0"
    ]
    
    headers = {
        "User-Agent": random.choice(user_agents),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0"
    }
    
    try:
        logger.info(f"Fetching movies from category: {category}")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise exception for 4XX/5XX responses
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Find all movie thumbnails - updated selector for better matching
        movies = soup.find_all("a", class_="Thumbnail__StyledThumbnail-sc-1ng2vnp-0")
        logger.info(f"Found {len(movies)} movies in {category} category")
        
        movie_list = []
        count = 0
        
        for movie in movies:
            if count >= limit:
                break
                
            try:
                # Extract basic information
                title = movie.get("aria-label", "").strip()
                link = "https://tubitv.com" + movie.get("href", "")
                
                # Skip if we couldn't get a title or link
                if not title or not link:
                    continue
                
                # Extract image from the picture tag
                img_tag = movie.find("img")
                image_url = img_tag.get("src") if img_tag else None
                
                # Extract extra information
                year = None
                duration = None
                rating = None
                
                # Try to extract year and duration if available
                meta_div = movie.find("div", class_="MetadataContainer")
                if meta_div:
                    meta_text = meta_div.text.strip()
                    meta_parts = meta_text.split("•")
                    
                    if len(meta_parts) >= 1:
                        try:
                            year = int(meta_parts[0].strip())
                        except (ValueError, IndexError):
                            pass
                    
                    if len(meta_parts) >= 2:
                        duration = meta_parts[1].strip()
                        
                    if len(meta_parts) >= 3:
                        rating = meta_parts[2].strip()
                
                # Create movie data dictionary
                movie_data = {
                    "title": title,
                    "link": link,
                    "image_url": image_url,
                    "year": year,
                    "duration": duration,
                    "rating": rating,
                    "category": category
                }
                
                movie_list.append(movie_data)
                count += 1
                
                # Add a small delay to avoid hitting the server too hard
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error processing movie: {e}")
                continue
                
        return movie_list
        
    except requests.RequestException as e:
        logger.error(f"Request failed: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return []

def get_movie_categories():
    """
    Get available movie categories from Tubi TV
    
    Returns:
        list: List of category dictionaries with id and name
    """
    url = "https://tubitv.com/categories"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Find category links
        category_links = soup.find_all("a", href=lambda href: href and "/category/" in href)
        
        categories = []
        seen_categories = set()
        
        for link in category_links:
            category_name = link.text.strip()
            if not category_name:
                continue
                
            href = link.get("href", "")
            category_id = href.split("/category/")[-1] if "/category/" in href else None
            
            if category_id and category_name and category_id not in seen_categories:
                categories.append({
                    "id": category_id,
                    "name": category_name
                })
                seen_categories.add(category_id)
        
        return categories
        
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        # Return default categories if we couldn't fetch them
        return [
            {"id": "action", "name": "Action"},
            {"id": "comedy", "name": "Comedy"},
            {"id": "drama", "name": "Drama"},
            {"id": "horror", "name": "Horror"},
            {"id": "thriller", "name": "Thriller"},
            {"id": "documentary", "name": "Documentary"}
        ]

def search_tubi_movies(query, limit=20):
    """
    Search for movies on Tubi TV
    
    Args:
        query (str): Search query
        limit (int): Maximum number of results to return
        
    Returns:
        list: List of movie dictionaries matching the search
    """
    url = f"https://tubitv.com/search/{query}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Find search results
        results = soup.find_all("a", class_="Thumbnail__StyledThumbnail-sc-1ng2vnp-0")
        
        movie_list = []
        count = 0
        
        for result in results:
            if count >= limit:
                break
                
            try:
                title = result.get("aria-label", "").strip()
                link = "https://tubitv.com" + result.get("href", "")
                
                if not title or not link:
                    continue
                    
                # Extract image
                img_tag = result.find("img")
                image_url = img_tag.get("src") if img_tag else None
                
                movie_data = {
                    "title": title,
                    "link": link,
                    "image_url": image_url
                }
                
                movie_list.append(movie_data)
                count += 1
                
            except Exception as e:
                logger.error(f"Error processing search result: {e}")
                continue
                
        return movie_list
        
    except Exception as e:
        logger.error(f"Error searching movies: {e}")
        return []

if __name__ == "__main__":
    # Example usage
    movies = get_tubi_movies(category="action", limit=5)
    print(f"Found {len(movies)} movies:")
    for movie in movies:
        print(f"- {movie['title']} ({movie.get('year', 'N/A')}) - {movie.get('duration', 'N/A')}")
    
    categories = get_movie_categories()
    print(f"\nAvailable categories ({len(categories)}):")
    for category in categories[:10]:  # Print first 10 categories
        print(f"- {category['name']} (ID: {category['id']})")
    
    search_results = search_tubi_movies("star wars", limit=3)
    print(f"\nSearch results for 'star wars' ({len(search_results)}):")
    for result in search_results:
        print(f"- {result['title']}")