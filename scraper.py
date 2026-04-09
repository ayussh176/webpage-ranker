import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import time

def is_valid_url(url):
    """Checks if a URL has a valid format (scheme and netloc)."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def scrape_links(start_url, max_pages=20, progress_callback=None):
    """
    Scrapes a website starting from start_url using BFS (Breadth-First Search).
    Limits scraping to the same domain as the start_url.
    
    Args:
        start_url (str): The initial URL to scrape.
        max_pages (int): The maximum number of pages to process.
        progress_callback (callable): Optional function to call with progress updates.
        
    Returns:
        dict: An adjacency list mapping a URL to a list of its outgoing internal links.
    """
    if not is_valid_url(start_url):
        raise ValueError("Invalid URL provided. Please include http:// or https://")

    domain = urlparse(start_url).netloc
    adj_list = {}
    
    queue = [start_url]
    visited = set([start_url])
    
    # Use a generic user agent to prevent immediate bot blocking
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    pages_scraped = 0

    while queue and pages_scraped < max_pages:
        current_url = queue.pop(0)
        
        try:
            response = requests.get(current_url, headers=headers, timeout=5)
            # We are only interested in HTML content
            if 'text/html' not in response.headers.get('Content-Type', ''):
                # We reached a non-HTML file (PDF, image, etc). Treat as dead end.
                adj_list[current_url] = []
                continue
                
            soup = BeautifulSoup(response.text, 'html.parser')
            pages_scraped += 1
            
            # Send progress update to UI
            if progress_callback:
                progress_callback(pages_scraped, max_pages)

            out_links = set()
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                full_url = urljoin(current_url, href)
                # Remove fragment identifiers (e.g., #section1) to avoid duplicate states
                full_url = full_url.split('#')[0]
                
                # We only want to process internal links (same domain)
                if is_valid_url(full_url) and urlparse(full_url).netloc == domain:
                    # Avoid self-loops for PageRank stability
                    if full_url != current_url:
                        out_links.add(full_url)
                    
                    if full_url not in visited:
                        visited.add(full_url)
                        queue.append(full_url)
            
            adj_list[current_url] = list(out_links)
            
            # Brief pause to respect the server
            time.sleep(0.1)

        except Exception as e:
            # If the page errors (timeout, 404, etc.), mark it as having no outgoing links
            adj_list[current_url] = []
            
    # Ensure all discovered nodes in our graph have an entry in the adj_list
    # Nodes that were discovered but not processed (due to max_pages limit) 
    # will act as sink nodes (0 outgoing links)
    discovered_nodes = set()
    for links in adj_list.values():
        discovered_nodes.update(links)
        
    for node in discovered_nodes:
        if node not in adj_list:
            adj_list[node] = []

    return adj_list
