import sys
import argparse
import socket
from urllib.parse import urlparse

def make_http_request(url):
    parsed_url = urlparse(url)
    host = parsed_url.netloc
    path = parsed_url.path if parsed_url.path else '/'
    
    try:
        with socket.create_connection((host, 80)) as s:
            s.sendall(f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n".encode())
            response = b""
            while True:
                data = s.recv(1024)
                if not data:
                    break
                response += data
            return response.decode('utf-8')
    except Exception as e:
        return str(e)

def search(term):
    search_url = f"https://developer.mozilla.org/ru/docs/Web/API/WebSockets_API/?q={term}"
    return make_http_request(search_url)

def parse_args():
    parser = argparse.ArgumentParser(description="Web CLI")
    parser.add_argument("-u", "--url", help="Make an HTTP request to the specified URL and print the response")
    parser.add_argument("-s", "--search", help="Make an HTTP request to search the term using your favorite search engine and print top 10 results")
    return parser.parse_args()


def main():
    args = parse_args()

    if not any(vars(args).values()): 
        print("No option provided. Use -h or --help for usage instructions.")
        sys.exit()

    if args.url:
        response = make_http_request(args.url)
        print(response)

    elif args.search:
        response = search(args.search)
        print(response)


if __name__ == "__main__":
    main()
