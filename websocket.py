import sys
import socket
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

def make_http_request(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        all_elements = soup.find_all(['h1', 'h2', 'h3', 'p'])
        all_text = [element.get_text() for element in all_elements]
        
        links = soup.find_all('a', href=True)
        links_href = [link['href'] for link in links if link['href'].startswith('http')]
        
        all_info = all_text + links_href
        
        return all_info
    except Exception as e:
        return str(e)

def search(term):
    search_url = "https://en.wikipedia.org/wiki/WebSocket"
    all_info = make_http_request(search_url)
    matching_info = [info for info in all_info if term.lower() in info.lower()]
    return matching_info[:10]

def print_error():
    print("No option provided.")
    print("Usage: ")
    print("python websocket.py -u URL")
    print("python websocket.py -s SEARCH_TERM")
    print("python websocket.py -h")
    sys.exit()

def main():
    args = sys.argv[1:]  

    if not args:
        print_error()
        

    if '-u' in args:
        url_index = args.index('-u') + 1
        if url_index < len(args):
            url = args[url_index]
            response = make_http_request(url)
            print("Information extracted from", url, ":")
            for info in response:
                print(info)
        else:
            print("Error: No URL provided after -u")
            sys.exit()

    elif '-s' in args:
        search_index = args.index('-s') + 1
        if search_index < len(args):
            term = ' '.join(args[search_index:]) 
            response = search(term) 
            print("Search results for", term, ":")
            for info in response:
                print(info)
        else:
            print("Error: No search term provided after -s")
            sys.exit()

    elif '-h' in args:
        print("go2web -u <URL>         # make an HTTP request to the specified URL and print the response")
        print("go2web -s <search-term> # make an HTTP request to search the term using your favorite search engine and print top 10 results")
        print("go2web -h               # show this help")
    

if __name__ == "__main__":
    main()
