import socket
import ssl
import certifi
import time

from httpClasses import HTTPResponse, HTTPRequest
from h2sslSocket import beautify_response_body

def create_https_connection(host, port, timeout):
    ### quick function to create our SSL socket
    
    # Create a raw TCP socket
    context = ssl.create_default_context()

    # Optionally, use the certifi bundle (set the default CA certs)
    context.check_hostname = False

    context.verify_mode = ssl.CERT_NONE

    try:
        # Create the socket and establish the connection
        raw_socket = socket.create_connection((host, port), timeout=timeout)
        raw_socket.settimeout(timeout)
    except socket.error as e:
        raise ConnectionError(f"Failed to create socket: {e}")
        return None
    
    # Wrap the socket with SSL
    ssl_socket = context.wrap_socket(raw_socket, server_hostname=host)
    
    # Return the SSL-wrapped socket
    return ssl_socket

def send_request(ssl_socket, host, path="/", method="GET", raw_headers=None, payload=None, body=None):
    """Very simple function that handles request creation. Very useful to be used as a "template" for dynamic requests. #TODO: add default smuggling headers

    Args:
        ssl_socket (SSLSOCKET): socket contianing the connection to target server
        host (str): The target server we want to communicate with 
        path (str, optional): Path to the specific resource we wish to request. Defaults to "/".
        method (str, optional): HTTP request method to be used in our request. Defaults to "GET".
        raw_headers (_type_, optional): Any extra headers we want to add to our request. Defaults to None.
        body (_type_, optional): Body of the request we want to send if any. Defaults to None.
    """
    # Construct the request line manually
    request_line = f"{method} {path} HTTP/1.1\r\n"
    
    # Ensure there's always a Host and Connection header at minimum
    default_headers = f"Host: {host}\r\nConnection: keep-alive\r\nContent-Type: application/x-www-form-urlencoded\r\n"
    
    # If raw headers are provided, we append them. Otherwise, use default headers.
    if raw_headers:
        headers_section = default_headers + raw_headers
    else:
        headers_section = default_headers
    
    if payload:
        headers_section += payload
    
    # Construct the full request
    full_request = request_line + headers_section + "\r\n"  # End headers section with CRLF
    
    # Append the body if provided
    if body:
        full_request += body
        request = HTTPRequest(method, host, path, 'HTTP/1', headers=headers_section, body=body)
    else:
        request = HTTPRequest(method, host, path, 'HTTP/1', headers=headers_section)
    
    # Send the full request through the SSL socket
    ssl_socket.sendall(full_request.encode("utf-8"))
    return request

    
def receive_response(ssl_socket):
    """Recieves most responses we will be getting from the socket. Stores both headers and body in variables. This func will handle recieving the body if Content-Length is specified in the 
       response. Otherwise, if we detect a TE header we will call the function to read TE responses. **This function handles keep-alive connections in that we dont just use while true to 
       recieve the data (that will go on for a long time w/ connection keep-alive) Specifically reading CL or TE headers make it possible to read all data in a more sophisticated way that 
       will work better with out needs :+)

    Args:
        ssl_socket (SSLSOCKET): socket containing our connection to target server

    Returns:
        headers (str), body (str): The response headers and the response body completely recieved.   
    """
    response_data = b""
    buffer_size = 4096  # Adjust buffer size as needed
    timeout_attempts = 2
    
    # fixed the response display to work wiht 'Connection: keep-alive' before we just did while true which only stops when the connection is broken. Now the while loop will exit even if
    # there is a persistent connection to the server. 
    while b"\r\n\r\n" not in response_data:
        try:
            chunk = ssl_socket.recv(buffer_size)
            if not chunk:
                break
            response_data += chunk
        except socket.timeout:
                attempts += 1
                print(f"Attempt {attempts}: Socket timed out.")
                if attempts >= timeout_attempts:
                    print("Giving up after too many attempts.")
                    return None  # Or raise an exception to signal timeout
    
    try:
        headers, body_start = response_data.split(b"\r\n\r\n", 1)
    except ValueError:
        return ""
    # Parse headers to find Content-Length or Transfer-Encoding (so we can calculate length of body and display it fully)
    headers = headers.decode("utf-8")
    
    first_line = headers.split("\n")[0]
    status_code = int(first_line.split()[1])
    
    
    if not body_start:
        return HTTPResponse(status_code, headers, "", 'HTTP/1')
    if 'transfer-encoding: chunked' in headers.lower():
        body = read_chunked_body(ssl_socket, body_start)
    else:
        content_length = None
        for header in headers.split("\r\n"):
            if header.lower().startswith("content-length:"):
                content_length = int(header.split(":")[1].strip())
                break
            
            body = body_start
            if content_length:
                start_time = time.time()  # Start the timer
                while len(body) < content_length:
                    # Check if it's been more than 4 seconds
                    if time.time() - start_time > 4:  # Timeout set to 4 seconds
                        raise TimeoutError("Custom timeout: receiving body took too long.")
                    try:
                        body += ssl_socket.recv(buffer_size)
                    except socket.timeout:
                        print("Socket timed out while receiving the body.")
                        break
    if isinstance(body, bytes):
        return HTTPResponse(status_code, headers, body.decode('utf-8'), 'HTTP/1')
    elif isinstance(body, str):
        return HTTPResponse(status_code, headers, body, 'HTTP/1')
    else:
        return HTTPResponse(status_code, headers, "", 'HTTP/1')
    

def read_chunked_body(ssl_socket, initial_body):
    """Very similar function to the receive response this one just handles the responses that use chunked encoding 

    Args:
        ssl_socket (SSLSOCKET): The socket currently handling our connection to target server
        initial_body (str): buffer_size-len(headers) = number of chars from the response body that are in this "inital body" variable. Basically just some bytes from the body such that 
                            the length of them + len(headers) = buffer_size

    Returns:
        str: the complete, decoded chunked response body from the server
    """
    body = b""
    buffer_size = 4096
    remaining_data = initial_body
    timeout_attempts = 1
    attempts = 0

    while True:
        try:
            # Read chunk size (up to CRLF)
            while b"\r\n" not in remaining_data:
                try:
                    remaining_data += ssl_socket.recv(buffer_size)
                except socket.timeout:
                    attempts += 1
                    if attempts >= timeout_attempts:
                        return body.decode("utf-8")

            chunk_size_str, remaining_data = remaining_data.split(b"\r\n", 1)
            chunk_size = int(chunk_size_str, 16)

            # If the chunk size is 0, we're done
            if chunk_size == 0:
                break

            # Read the chunk data
            while len(remaining_data) < chunk_size:
                try:
                    remaining_data += ssl_socket.recv(buffer_size)
                except socket.timeout:
                    attempts += 1
                    if attempts >= timeout_attempts:
                        return body.decode("utf-8")

            body += remaining_data[:chunk_size]
            remaining_data = remaining_data[chunk_size:]

            # Read the trailing CRLF after the chunk
            if b"\r\n" not in remaining_data:
                try:
                    remaining_data += ssl_socket.recv(buffer_size)
                except socket.timeout:
                    print("Timed out while reading CRLF after chunk.")
                    break

            remaining_data = remaining_data.split(b"\r\n", 1)[1]

        except socket.error as e:
            print(f"Socket error occurred: {e}")
            break

    return body.decode("utf-8")
    
    

def main():
    host = "www.redcare-apotheke.ch"
    path = r'/%20HTTP/1.1%0d%0a%0d%0a'
    
    # can simply repeat these 3 steps over and over to send multiple requests on the same connection (socket) note that in our real version we can simply pass all headers to the 
    # send_request() func so theyre not hardcoded within the function itself as they are now.

    # Step 1: Create the connection
    ssl_socket = create_https_connection(host, 443, 5)
    
    # Step 2: Send a request
    headers = "Connection: keep-alive\r\nContent-Type: application/x-www-form-urlencoded\r\n"
    req = send_request(ssl_socket, host, path, method='GET')
    
    print(req)
    
    # Step 3: Receive the response
    resp = receive_response(ssl_socket)

    #print(resp.headers + '\n')
    print(resp)

    # Close the connection
    ssl_socket.close()
if __name__ == "__main__":
    main()
    
    
    