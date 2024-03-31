import sys
import socket
import ssl
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import json 
import hashlib
from tinydb import TinyDB, Query

cache_file = "cache.json"
db = TinyDB(cache_file)

def hash_url(url):
    return hashlib.md5(url.encode()).hexdigest()

def cache_response(url, response):
    db.insert({'url': hash_url(url), 'response': response})

def is_cached(url):
    return db.contains(Query().url == hash_url(url))

def retrieve_cached_response(url):
    result = db.get(Query().url == hash_url(url))
    return result['response']

def make_tcp_request(url):
    try:
        parsed_url = urlparse(url)
        host = parsed_url.netloc
        path = parsed_url.path if parsed_url.path else '/'

        context = ssl.create_default_context()
        with socket.create_connection((host, 443)) as sock:
            with context.wrap_socket(sock, server_hostname=host) as s:
                s.sendall(f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n".encode())
                response = b''
                while True:
                    data = s.recv(4096)
                    if not data:
                        break
                    response += data

        return response.decode()  
    except Exception as e:
        return str(e)

def make_http_request(url):
    try:
        if is_cached(url):
            print("Retrieving cached response for:", url)
            return retrieve_cached_response(url)
        
        response = make_tcp_request(url)
        
        if '\r\n\r\n' in response:
            status_line, headers_and_body = response.split('\r\n\r\n', 1)
            status_code = int(status_line.split()[1])
            headers = dict(header.split(": ", 1) for header in status_line.split("\r\n")[1:])
            content_type = headers.get('Content-Type')

            if status_code == 200:
                if content_type:
                    if 'text/html' in content_type:
                        parsed_response = parse_html(headers_and_body)
                        cache_response(url, parsed_response)  # Cache HTML responses
                        return parsed_response
                    elif 'application/json' in content_type:
                        json_data = json.loads(headers_and_body)
                        cache_response(url, json_data)  # Cache JSON responses
                        return json_data
                    else:
                        return [f"Unsupported content type: {content_type}"]
                else:
                    return [f"Error: Content-Type header not found"]
            else:
                return [f"Error: Server returned status code {status_code}"]
        else:
            return [f"Error: Invalid HTTP response format"]
    except Exception as e:
        return [str(e)]

def parse_html(response):
    soup = BeautifulSoup(response, 'html.parser')
    all_elements = soup.find_all(['h1', 'h2', 'h3', 'p'])
    all_info = []

    for element in all_elements:
        if element.name.startswith('h'):
            if element.name == 'h1':
                all_info.append(f"{'----'} {element.get_text()}")
            elif element.name == 'h2':
                all_info.append(f"{'---'} {element.get_text()}")
            elif element.name == 'h3':
                all_info.append(f"{'--'} {element.get_text()}")
        elif element.name == 'p':
            all_info.append(f"{'-'} {element.get_text()}")

    links = soup.find_all('a', href=True)
    links_href = [link['href'] for link in links if link['href'].startswith('http')]
    all_info.append("-- Links --")
    all_info += links_href

    return all_info

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
