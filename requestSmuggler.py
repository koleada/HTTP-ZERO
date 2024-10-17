import argparse
import sslSocket
import h2sslSocket
import sys
from colorama import Fore
from urllib.parse import urlparse
import ssl
from payloads import clPayloads, tePayloads, specialCl, specialTe1, specialTe2
from hugeHeader import getHugeHeaderVal
import time

def main(): 
    args = setupParser()   
    urls, headers, methods = getUserInput(args)
    
    
    testHandler(args, urls, headers, methods)
    

def testHandler(args, urls, headers, methods):
    if args.server and not args.smuggled_request:
        print(Fore.BLUE + "OOB sever detected. Tests will not report potential vulnerabilities. Check your server!")
        print(Fore.BLUE + "Creating payload to hopefully get a request sent to your server")
        print(Fore.RESET)
        
        if "http://" in args.server or "https://" in args.server:
            smuggledReq = 'GET ' + args.server.strip() + r'HTTP/1.1\r\nFoo: x'
        else:
            smuggledReq = r'GET //' + args.server.strip() + r'HTTP/1.1\r\nFoo: x'
    elif args.smuggled_request and not args.server:
        smuggledReq = args.smuggled_request
    elif args.smuggled_request and args.server:
        print(Fore.RED + "Both --smuggled-request and --server options are provided. Please choose only one.")
        sys.exit(1)
    else:
        smuggledReq = r'GET /hopefully404 HTTP/1.1\r\nFoo: x'
        
        
    if args.content_length and not args.transfer_encoding:
        print(Fore.BLUE + "Starting tests...")
        print(Fore.RESET)
        clZeroTestH1(args, smuggledReq, urls, headers, methods)
        clZeroTestH2(args, smuggledReq, urls, headers, methods)
    elif not args.content_length and args.transfer_encoding:
        print(Fore.BLUE + "Starting tests...")
        print(Fore.RESET)
        teZeroTestH1(args, smuggledReq, urls, headers, methods)
        teZeroTestH2(args, smuggledReq, urls, headers, methods)
    else:
        print(Fore.BLUE + "Starting tests...")
        print(Fore.RESET)
        clZeroTestH1(args, smuggledReq, urls, headers, methods)
        teZeroTestH1(args, smuggledReq, urls, headers, methods)
        
        clZeroTestH2(args, smuggledReq, urls, headers, methods)
        teZeroTestH2(args, smuggledReq, urls, headers, methods)

        
def clZeroTestH2(args, smuggledReq, urls, headers, methods):
    print(Fore.BLUE + "Testing for GET based CL.0 smuggling on HTTP/1...")
    print(Fore.RESET)
    #TODO: send get requests w/ all obfuscated variations of the CL header immediately followed by a normal request repeat a few times for each

def teZeroTestH1(args, smuggledReq, urls, headers, methods):
    print(Fore.BLUE + "Testing for GET based CL.0 smuggling on HTTP/1...")
    print(Fore.RESET)
    #TODO: send get requests w/ all obfuscated variations of the CL header immediately followed by a normal request repeat a few times for each

def teZeroTestH2(args, smuggledReq, urls, headers, methods):
    print(Fore.BLUE + "Testing for GET based CL.0 smuggling on HTTP/1...")
    print(Fore.RESET)
    
    if not methods:
        methods = ["OPTIONS"]
    
    if args.headers:
        h1Headers = getH1Headers(headers)
    else:
        h1Headers = ""
    
    for url in urls:
        
        # parse URL for host and port or default to port 443
        if ':' in url[0]:
            host, port = url[0].split(':')
        else:
            host, port = url[0], 443
        try: 
            ssl_socket = sslSocket.create_https_connection(host, int(port), args.timeout)
        except ConnectionError:
            print(Fore.RED+ f"Failed to connect to host: {url[0]}")
            continue
        else:
            # send inital request 
            request = sslSocket.send_request(ssl_socket, url[0], url[1], raw_headers=h1Headers)
            print(request)
            response = sslSocket.receive_response(ssl_socket)
            print(response.headers)
            
            #TODO: check is resp is cached
            
            # if first response is 404 we cannot do further testing without an OOB server
            if response.status_code == 404 and not args.server:
                print(Fore.RED + f"Target {url[0]}{url[1]} responded with 404 from inital request and you didnt provide a server for OOB interaction. Cannot do further testing on this endpoint.")
                ssl_socket.close()
                continue
            else: 
                print(f"Starting CL.0 on https://{url[0]}{url[1]}")
                specialClPayloads(args, url, methods, h1Headers, True, smuggledReq, host, port)
        for method in methods:        
    
        
def clZeroTestH1(args, smuggledReq, urls, headers, methods):
    """This function handles all tests for CL.0 testing on HTTP/1

    Args:
        args (argparser): user input
        smuggledReq (str): the request (either to get 404 or OOB request) that we hope to be smuggled.
        urls (list): List of all endpoints (or 1 endpoint) that we want to test.
        headers (list): A list of tuples representing the HTTP headers we wish to append to all requests.
        methods (list): A list of HTTP methods we wish to test for smuggling.
    """
    print(Fore.BLUE + "Testing for GET based CL.0 smuggling on HTTP/1...")
    print(Fore.RESET)
    
    if not methods:
        methods = ["GET"]
    
    if args.headers:
        h1Headers = getH1Headers(headers)
    else:
        h1Headers = ""
    
    for url in urls:
        
        # parse URL for host and port or default to port 443
        if ':' in url[0]:
            host, port = url[0].split(':')
        else:
            host, port = url[0], 443
        try: 
            ssl_socket = sslSocket.create_https_connection(host, int(port), args.timeout)
        except ConnectionError:
            print(Fore.RED+ f"Failed to connect to host: {url[0]}")
            continue
        else:
            # send inital request 
            request = sslSocket.send_request(ssl_socket, url[0], url[1], raw_headers=h1Headers)
            print(request)
            response = sslSocket.receive_response(ssl_socket)
            print(response.headers)
            
            #TODO: check is resp is cached
            
            # if first response is 404 we cannot do further testing without an OOB server
            if response.status_code == 404 and not args.server:
                print(Fore.RED + f"Target {url[0]}{url[1]} responded with 404 from inital request and you didnt provide a server for OOB interaction. Cannot do further testing on this endpoint.")
                ssl_socket.close()
                continue
            else: 
                print(f"Starting CL.0 on https://{url[0]}{url[1]}")
                specialClPayloads(args, url, methods, h1Headers, True, smuggledReq, host, port)
        for method in methods:        
            for payload in clPayloads:
                p0 = payload[0]
                #very important to encode to utf-8 as certain characters take up more then 1 byte
                p1 = payload[1].replace('z', str(len(smuggledReq.encode('utf-8'))))
                payload = f'{p0}: {p1}\r\n'
                
                request = sslSocket.send_request(ssl_socket, url[0], url[1], method, raw_headers=h1Headers, payload=payload, body=smuggledReq)
                print(Fore.BLUE + r"{}".format(payload))
                print(Fore.RESET)
                ssl_socket = sendValidRequestsH1(args, ssl_socket, url, host, port, payload)
            print('done')


def sendValidRequestsH1(args, ssl_socket, url, host, port, payload):
    """This function handles the sending of valid HTTP/1 requests along a provided socket in hopes of triggering a 404 or an OOB request to the users server once our malicious req is sent.
       Only GET requests are use here. 
       
    Args:
        args (argparser): User input
        ssl_socket (SSLSocket): The socket that has sent the malicious request and (hopefully) remains connected to the target server.
        url (tuple): url[0] is the netloc (host and port). url[1] is everything after the netloc in the URL 
        host (str): Just the host name
        port (int): port of the target endpoint.
        method (str): The HTTP method we want to use to send valid requests

    Returns:
        _type_: _description_
    """
    method = 'GET'
    for i in range(args.numRequests):
        try:
            request = sslSocket.send_request(ssl_socket, url[0], url[1], method)
            
        # often raised on harnded targets that will immediately cut the connection and return no response
        except ssl.SSLEOFError:
            print(Fore.RED + f"Protocol violation on https://{url[0]}{url[1]} when trying CL.0 smuggling. Trying other obfuscations...")
            print(Fore.RESET)
            ssl_socket.close()
            ssl_socket = sslSocket.create_https_connection(host, int(port), args.timeout) 
            return ssl_socket
        try:
            response = sslSocket.receive_response(ssl_socket)
        
        # ensure the response doesnt take too long
        except TimeoutError:
            print(Fore.RED + f"Timeout reading response on on https://{url[0]}{url[1]} when trying CL.0 smuggling. Trying other obfuscations...")
            print(Fore.RESET)
            ssl_socket.close()
            ssl_socket = sslSocket.create_https_connection(host, int(port), args.timeout) 
            return ssl_socket

        # if the response is blank but doesnt throw an error or some other weird things are done in the response
        except ValueError:
            print(Fore.RED + f"Error reading response on https://{url[0]}{url[1]}. Trying other obfuscations...")
            print(Fore.RESET)
            ssl_socket.close()
            ssl_socket = sslSocket.create_https_connection(host, int(port), args.timeout) 
            return ssl_socket
        
        # double check response exists and check if it appears to be vulnerable
        if response and not args.server:
            isVulnerable(request, response, url, 'CL.0', payload)
            print(response.headers+ '\n')
        else:
            break
    ssl_socket.close()
    ssl_socket = sslSocket.create_https_connection(host, int(port), args.timeout) 
    time.sleep(args.timeout)
    return ssl_socket

def isVulnerable(request, response, url, test, payload):
    # basically just looking to get a 404 from a valid request that normally doesnt lead to a 404
    if response.status_code == 404:
        print(Fore.GREEN +"----------------------------------------------------------------------------------------------------------")
        print(Fore.GREEN + f'Potential {test} smuggling found on https://{url[0]}{url[1]}')
        print(Fore.GREEN + f"Payload used: {payload}\n")
        print(Fore.GREEN + f"Request sent:\n{request}\n")
        print(Fore.GREEN + f"Response:\n{h2sslSocket.beautify_response_body(response)}\n")
        print(Fore.GREEN +"----------------------------------------------------------------------------------------------------------")
        print(Fore.RESET)
    
    # uncomment if we choose to implement CRLF stuff as this is caused by CRLF
    # if response.isSplitResp():   
    #     print(Fore.GREEN +"----------------------------------------------------------------------------------------------------------")
    #     print(Fore.GREEN + f"Split response detected on https://{url[0]}{url[1]}. This could possibly be bypassed by injecting a large number of newlines via CRLF.")
    #     print(Fore.GREEN + f"Request sent:\n{request}\n")
    #     print(Fore.GREEN + f"Response:\n{response}\n") 
    #     print(Fore.GREEN +"----------------------------------------------------------------------------------------------------------")


def specialClPayloads(args, url, methods, headers, http1, smuggledReq, host, port):
    count = 0
    if http1:
        for method in methods:
            
            p0 = specialCl[0]
            #very important to encode to utf-8 as certain characters take up more then 1 byte
            p1 = specialCl[1]
            payload = f'{p0[0]}: {p0[1]}\r\n'
            payload += f"{p1[0]}: {p1[1].replace('z', str(len(smuggledReq.encode('utf-8'))))}\r\n"
            print(r"{}".format(payload))
            ssl_socket1 = sslSocket.create_https_connection(host, int(port), args.timeout)
            request = sslSocket.send_request(ssl_socket1, url[0], url[1], method, raw_headers=headers, payload=payload, body=smuggledReq)
            sendValidRequestsH1(args, ssl_socket1, url, host, port)
            print(request)
        
            header, val = getHugeHeaderVal(65532)
            payload = f'{header}: {val}\r\n'
            ssl_socket2 = sslSocket.create_https_connection(host, int(port), args.timeout)
            request = sslSocket.send_request(ssl_socket2, url[0], url[1], method, raw_headers=headers, payload=payload, body=smuggledReq)
            sendValidRequestsH1(args, ssl_socket2, url, host, port)
            print('huge header')
            
        
    else:
        headers.append(specialCl)
        #TODO: implement http/2 special CL tests
    


def getH1Headers(headers):
    h1Headers = ""
    for header in headers:
        h0 = header[0].strip().title()
        h1 = header[1].strip().lower()
        
        h1Headers += f"{h0}: {h1}\r\n"
    return h1Headers
    
def getUserInput(args):
    urls = []
    headers = []
    methods = []
    if args.list:
        with open(args.list, 'r') as f:
            for line in f:
                if line.startswith('http'):
                    try:
                        url = urlparse(line)
                    except ValueError:
                        print(Fore.RED+f"Error: Invalid URL {line.strip()}")
                    else:
                        # append a tuple (<hostName>, <restOfUrl>) to urls list
                        if url.path:
                            urls.append((url.netloc, url.path + url.params + url.query + url.fragment))
                        else:
                            # if theres no path put a / there 
                            urls.append((url.netloc, '/'))
                else:
                    print(Fore.RED+f"Error: Unable to open file {args.list}")
                    sys.exit(1)
            if len(urls) == 0:
                print(Fore.RED+f"Error: No valid URLs found in file {args.list}")
                sys.exit(1)
        print(f"Testing {len(urls)} URLs from file {args.list}")
    elif args.url:
        try:
            url = urlparse(args.url)
        except ValueError:
            print(Fore.RED+f"Error: Invalid URL {line.strip()}")
            print(Fore.RESET)
        else:
            if url.path:
                urls.append(((url.netloc, url.path + url.params + url.query + url.fragment)))
            else:
                urls.append((url.netloc, '/'))
    else:
        print(Fore.RED+"Error: No URLs provided. Please provide a URL or a list of URLs.")
        sys.exit(1)

        
    if args.headers:
        if '|' in args.headers:
            for h in args.headers.split('|'):
                header, value = h.split(':')
                header = header.strip().lower()
                value = value.strip().lower()
                if header and value:
                    headers.append((str(header), str(value)))
                else:
                    print(Fore.RED+"Error: Invalid header format. Use header:value")
                    sys.exit(1)
        else:
            header, val = args.headers.split(':')
            headers.append(tuple(header.strip().lower(), val.strip().lower())) 
    else:
        headers = None
    
    
    if args.methods:
        for method in args.methods.split(','):
            methods.append(method).strip().upper()
    else:
        methods = None
    
    
    return urls, headers, methods
def setupParser():
    parser = argparse.ArgumentParser(description="""
                                    HTTP/Zero is a tool that aims to detect more neiche types of HTTP request smuggling. Specifically, this tool looks for CL.0 request smuggling using GET requests and an obfuscated 
                                    Content-Length header. It also tests for TE.0 request smuggling, where only a Transfer-Encoding header is required. TE.0 is tested using the OPTIONS method by default. The goal of 
                                    this tool is to aid secuirty researchers and developers in detecting newer more neiche types of smuggling not many other tools check for. Please use responsibly!
                                     """)

    # Required arguments
    parser.add_argument("-u", "--url", required=False, help="Single URL to process")
    parser.add_argument("-l", "--list", required=False, help="File containing a list of URLs")

    # Optional arguments
    parser.add_argument("-t", "--timeout", type=int, default=5, help="Number of seconds to wait before socket timeout (default: 5)")
    parser.add_argument("-nR", "--numRequests", type=int, default=5, help="Number of valid requests sent per test (default: 5)")
    parser.add_argument("-hD", "--headers", type=str, nargs="+", help="Headers to be added to each request including cookies, all necessary smuggling headers will automatically be added. Be careful adding headers when doing HTTP/2 testing, can make errors. Format: header1:value1 | header2:value2")
    parser.add_argument("-CL", "--content-length", action="store_true", help="Only test for CL.0 request smuggling")
    parser.add_argument("-TE", "--transfer-encoding", action="store_true", help="Only test for TE.0 request smuggling")
    parser.add_argument("-m", "--methods", type=str, nargs="+", help="HTTP methods to use for testing TE.0 smuggling, seperated by a comma. Default OPTIONS.")
    parser.add_argument("-s", "--server", type=str, help="Host name or URL of a server you control. If supplied, the tests will try to get requests sent to your server from the tagret.")
    parser.add_argument("-cH", "--cache-hit", action="store_true", help="Enable a specical test where we will look for cacheable pages. Once detected we will get the page cached and retry smuggling vectors")
    parser.add_argument("-cO", "--cache-only", action="store_true", help="Will only try to smuggle on pages we believe are cacheable.")    
    parser.add_argument("-cR", "--crlf", type=str, help="If youve identified a CRLF injection on a SINGLE URL add this arg with the CRLF injection payload and it will be used to hopefully get smuggling")
    parser.add_argument("-sL", "--sleep", type=int, default=0, help="Amount of seconds to sleep between each smuggling payload we try. Default 0.")
    parser.add_argument("-sR", "--smuggled-request", type=str, default=0, help=r"A specific request you wish to be smuggled including CRLF - dont use with -s flag! Default: GET /hopefully404 HTTP/1.1\r\nFoo: x")
    

    args = parser.parse_args()
    return args    

    
if __name__ == '__main__':
    main()