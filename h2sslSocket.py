import socket
import ssl
import certifi

import gzip
import h2.connection
import h2.events
from h2.config import H2Configuration 
from bs4 import BeautifulSoup
import jsbeautifier

## ALL HTTP/2 HEADERS MUST BE LOWERCASE

def setSocket(host, port=443, timeout=5):

    # generic socket and ssl configuration
    socket.setdefaulttimeout(timeout)
    ctx = ssl.create_default_context(cafile=certifi.where())
    ctx.set_alpn_protocols(['h2'])

    # open a socket to the server and initiate TLS/SSL
    sock = socket.create_connection((host, port))
    sock = ctx.wrap_socket(sock, server_hostname=host)

    config = H2Configuration(client_side=True, header_encoding='utf-8', validate_outbound_headers=False, normalize_outbound_headers=False)
    conn = h2.connection.H2Connection(config=config)
    conn.initiate_connection()
    sock.sendall(conn.data_to_send())
    return sock, conn

# req_headers must be a list of tuples for this to work properly. Same format as the predefined headers
def send_request(sock, conn, host, method='GET', path='/', req_headers=None, body=None):
    
    # flag to look for gzip encoded responses because these do not get decoded in the normal way
    gzipFlag = False
    
    headers = [
        (':method', f'{method}'),
        (':path', f'{path}'),
        (':authority', f'{host}'),
        (':scheme', 'https'),
        # NOTE: no connection: keep-alive is needed. HTTP/2 basically keeps the connection alive by default. Including the header will cause errors/weird behavior
    ]
    if req_headers:
        for i in req_headers:
            headers.append(i)
    
    if body:
        headers.append(("content-length", str(len(body.encode('utf-8')))))
    
    # Start the request on a new stream (stream_id = 1)
    stream_id = conn.get_next_available_stream_id()
        
    conn.send_headers(1, headers)
    if body:
        body = body.encode('utf-8')
        conn.send_data(stream_id, body, end_stream=True)
    else:
        conn.end_stream(stream_id)
    print('ok')   
    sock.sendall(conn.data_to_send())
    return stream_id, gzipFlag

def receive_response(sock, conn, stream_id, host, path='/', gzipFlag=False, timeout=5):
    body = b''
    response_headers = []
    response_stream_ended = False
    while not response_stream_ended:

        # read raw data from the socket
        data = sock.recv(65536)
        if not data:
            print("Socket connection closed prematurely.")
        
        
        # feed raw data into h2, and process resulting events
        events = conn.receive_data(data)
        for event in events:
            # Handle header events
            if isinstance(event, h2.events.ResponseReceived):
                for n,v in event.headers:
                    response_headers.append((n, v))
                    if 'gzip' in v and 'content-encoding' in n:
                        gzipFlag = True
                
            if isinstance(event, h2.events.DataReceived):
                # update flow control so the server doesn't starve us
                conn.acknowledge_received_data(event.flow_controlled_length, event.stream_id)
                # more response body data received
                
                body += event.data
                #print(event.data.decode('utf-8'))
            if isinstance(event, h2.events.StreamEnded):
                # response body completed, let's exit the loop
                response_stream_ended = True
                break
        # send any pending data to the server
        
        sock.sendall(conn.data_to_send())
    if gzipFlag:
        print(gzipFlag)
        try:
            body = gzip.decompress(body)
        except gzip.BadGzipFile:
            pass
    return body.decode('utf-8'), response_headers
     
def beautify_response_body(response_body):
    # Parse the response body using BeautifulSoup
    soup = BeautifulSoup(response_body, 'html.parser')
    
    # Beautify HTML
    pretty_html = soup.prettify()

    # Optionally, beautify embedded JavaScript
    js_options = jsbeautifier.default_options()
    js_options.indent_size = 2  # You can adjust this to your preferred indentation
    
    for script_tag in soup.find_all('script'):
        if script_tag.string:
            # Beautify the JavaScript code inside <script> tags
            beautified_js = jsbeautifier.beautify(script_tag.string, js_options)
            script_tag.string.replace_with(beautified_js)
    
    return pretty_html

# Sending multiple requests quickly over the same connection. Just pass the host and path and we will get a list of responses. 
def send_multiple_requests(sock, h2_conn, host, requests):
    results = []

    for path in requests:
        stream_id = send_request(sock, h2_conn, 'GET', host, path)
        headers, body = receive_response(sock, h2_conn, stream_id)
        results.append((headers, body.decode('utf-8')))

    return results



def main():
    # Setup socket and H2 connection
    host = 'www.google.com'
    path = '/'
    port = 443
    timeout = 5
    
    #can pass a port to this function if needed
    sock, conn = setSocket(host, timeout=timeout)

    req_body = "GET /sdfsdf HTTP/1.1\r\nFoo: x"

    # Send GET request   
    stream_id, gzipFlag = send_request(sock, conn, method='GET', host=host, path=path, body=req_body)

    # Receive and display the response
    body, resp_headers = receive_response(sock, conn, stream_id, host, path, gzipFlag)
    
    
    for n,v in resp_headers:
        print(f"{n}: {v}")
    print("\n" + beautify_response_body(body))
    
    
    # tell the server we are closing the h2 connection
    conn.close_connection()
    # close the socket
    sock.close()

if __name__ == "__main__":
    main()