import argparse
import sslSocket
import h2sslSocket
import sys

def main(): 
    parser = argparse.ArgumentParser(description="Process URLs and perform HTTP requests")

    # Required arguments
    parser.add_argument("-u", "--url", required=False, help="Single URL to process")
    parser.add_argument("-l", "--list", required=False, help="File containing a list of URLs")

    # Optional arguments
    parser.add_argument("-t", "--timeout", required=False, type=int, default=5, help="Timeout in seconds (default: 5)")
    parser.add_argument("-nR", "--numRequests", required=False, type=int, default=1, help="Number of requests per test (default: 1)")
    parser.add_argument("-h", "--headers", type=str, nargs="+", help="Headers to be added to each request including cookies. Format: header1:value1 | header2:value2")
    parser.add_argument("-h2", "--http2", action="store_true", help="Only use HTTP/2. Default use HTTP/1 and HTTP/2")
    parser.add_argument("-h1", "--http1", action="store_true", help="Only use HTTP/1.1. Default use HTTP/1 and HTTP/2")

    args = parser.parse_args()

    if args.list:
        urls = []
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
        
    if args.headers:
        headers = []
        if '|' in args.headers:
            for h in args.headers.split('|'):
                header, value = h.split(':')
                header = header.strip()
                value = value.strip()
                if header and value:
                    headers.append((str(header), str(value)))
                else:
                    print("Error: Invalid header format. Use header:value")
                    sys.exit(1)
        else:
            headers.append(tuple(args.headers.split(':')))
    
def zeroGetTestH2(parser):
    print("Testing for GET based CL.0 smuggling...")
    #TODO: send get requests w/ all obfuscated variations of the CL header immediately followed by a normal request repeat a few times for each
    
        
def zeroGetTestH1(parser):
    print("Testing for GET based CL.0 smuggling...")
    #TODO: send get requests w/ all obfuscated variations of the CL header immediately followed by a normal request repeat a few times for each


def getPayloads(parser):
    smuggledReq = 'GET /hopefully404 HTTP/1.1\r\n Foo: x'
    
    #TODO: add all obfuscations to list as strings. put line breaks, tabs, spaces where necessary. use the length of smuggled req as the value for the CL headers
    payloads = []    
    
    
    
    
    
    
if __name__ == '__main__':
    main()