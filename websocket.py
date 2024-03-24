import sys
import socket
import ssl
from urllib.parse import urlparse
from bs4 import BeautifulSoup

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

def make_http_request(url):
    try:
        response = make_tcp_request(url)
        status_line, headers_and_body = response.split('\r\n', 1)
        status_code = int(status_line.split()[1])
        if status_code == 200:
            return parse_html(headers_and_body)
        else:
            return [f"Error: Server returned status code {status_code}"]
    except Exception as e:
        return [str(e)]

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
