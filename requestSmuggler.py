import argparse
import sslSocket
import h2sslSocket
import sys

def main(): 
    args = setupParser()   
    urls, headers, methods = getUserInput(args)
    
def getUserInput(args):
    urls = []
    headers = []
    methods = []
    if args.list:
        with open(args.list, 'r') as f:
            for line in f:
                if line.startswith('http'):
                    urls.append(line.strip())
                else:
                    print(f"Error: Unable to open file {args.list}")
                    sys.exit(1)
            if len(urls) == 0:
                print(f"Error: No valid URLs found in file {args.list}")
                sys.exit(1)
        print(f"Testing {len(urls)} URLs from file {args.list}")
    elif args.url:
        urls.append(args.url)
    else:
        print("Error: No URLs provided. Please provide a URL or a list of URLs.")
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
                    print("Error: Invalid header format. Use header:value")
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
        methods = ['GET', 'HEAD', 'OPTIONS', 'DELETE']
    
    return urls, headers, methods
def setupParser():
    parser = argparse.ArgumentParser(description="Process URLs and perform HTTP requests")

    # Required arguments
    parser.add_argument("-u", "--url", required=False, help="Single URL to process")
    parser.add_argument("-l", "--list", required=False, help="File containing a list of URLs")

    # Optional arguments
    parser.add_argument("-t", "--timeout", type=int, default=5, help="Timeout in seconds (default: 5)")
    parser.add_argument("-nR", "--numRequests", type=int, default=1, help="Number of requests per test (default: 1)")
    parser.add_argument("-h", "--headers", type=str, nargs="+", help="Headers to be added to each request including cookies, all necessary smuggling headers will automatically be added. Dont add Connection: keep-alive espeically if using HTTP/2! Format: header1:value1 | header2:value2")
    parser.add_argument("-h2", "--http2", action="store_true", help="Only use HTTP/2. Default use HTTP/1 and HTTP/2")
    parser.add_argument("-h1", "--http1", action="store_true", help="Only use HTTP/1.1. Default use HTTP/1 and HTTP/2")
    parser.add_argument("-CL", "--content-length", action="store_true", help="Only test for CL.0 request smuggling")
    parser.add_argument("-TE", "--transfer-encoding", action="store_true", help="Only test for TE.0 request smuggling")
    parser.add_argument("-m", "--methods", action=str, nargs="+", help="HTTP methods to use for testing, seperated by a comma. Default GET, HEAD, OPTIONS, DELETE (James Kettles tool covers the rest far better then mine could). ")
    parser.add_argument("-s", "--server", action=str, help="URL to a server you control. If supplied, the tests will try to get requests sent to your server from the tagret.")
    parser.add_argument("-cH", "--cache-hit", action="store_true", help="Enable a specical test where we will look for cacheable pages. Once detected we will get the page cached and retry smuggling vectors")
    parser.add_argument("-cO", "--cache-only", action="store_true", help="Will only try to smuggle on pages we believe are cacheable.")    
    

    args = parser.parse_args()
    return args
def clZeroGetTestH2(parser):
    print("Testing for GET based CL.0 smuggling...")
    #TODO: send get requests w/ all obfuscated variations of the CL header immediately followed by a normal request repeat a few times for each
    
        
def clZeroGetTestH1(parser):
    print("Testing for GET based CL.0 smuggling...")
    #TODO: send get requests w/ all obfuscated variations of the CL header immediately followed by a normal request repeat a few times for each

def teZeroGetTestH2(parser):
    print("Testing for GET based CL.0 smuggling...")
    #TODO: send get requests w/ all obfuscated variations of the CL header immediately followed by a normal request repeat a few times for each
    
        
def teZeroGetTestH1(parser):
    print("Testing for GET based CL.0 smuggling...")
    #TODO: send get requests w/ all obfuscated variations of the CL header immediately followed by a normal request repeat a few times for each


def getPayloads(parser):
    smuggledReq = 'GET /hopefully404 HTTP/1.1\r\n Foo: x'
    
    #TODO: add all obfuscations to list as strings. put line breaks, tabs, spaces where necessary. use the length of smuggled req as the value for the CL headers
    payloads = []    
    
    
    
    
    
    
if __name__ == '__main__':
    main()