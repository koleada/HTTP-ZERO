import socket
import ssl
import certifi

def create_https_connection(host, port=443):
    ### quick function to create our SSL socket
    
    # Create a raw TCP socket
    context = ssl.create_default_context()

    # Optionally, use the certifi bundle (set the default CA certs)
    context.load_verify_locations(cafile=certifi.where())

    # Create the socket and establish the connection
    raw_socket = socket.create_connection((host, port))
    
    # Wrap the socket with SSL
    ssl_socket = context.wrap_socket(raw_socket, server_hostname=host)
    
    # Return the SSL-wrapped socket
    return ssl_socket

def send_request(ssl_socket, host, path="/", method="GET", raw_headers=None, body=None):
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
    default_headers = f"Host: {host}\r\nConnection: keep-alive\r\n"
    
    # If raw headers are provided, we append them. Otherwise, use default headers.
    if raw_headers:
        headers_section = default_headers + raw_headers
    else:
        headers_section = default_headers
    
    # Construct the full request
    full_request = request_line + headers_section + "\r\n"  # End headers section with CRLF
    
    # Append the body if provided
    if body:
        full_request += body
    
    # Send the full request through the SSL socket
    ssl_socket.sendall(full_request.encode("utf-8"))

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
    
    # fixed the response display to work wiht 'Connection: keep-alive' before we just did while true which only stops when the connection is broken. Now the while loop will exit even if
    # there is a persistent connection to the server. 
    while b"\r\n\r\n" not in response_data:
        response_data += ssl_socket.recv(buffer_size)
    
    headers, body_start = response_data.split(b"\r\n\r\n", 1)
    
    # Parse headers to find Content-Length or Transfer-Encoding (so we can calculate length of body and display it fully)
    headers = headers.decode("utf-8")
    
    if 'transfer-encoding: chunked' in headers.lower():
        body = read_chunked_body(ssl_socket, body_start)
    else:
        content_length = None
        for header in headers.split("\r\n"):
            if header.lower().startswith("content-length:"):
                content_length = int(header.split(":")[1].strip())
                break
        
        # Now read the body based on Content-Length
        body = body_start
        if content_length:
            while len(body) < content_length:
                body += ssl_socket.recv(buffer_size)
    
    return headers, body
    

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
    
    while True:
        # Read chunk size (up to CRLF)
        if b"\r\n" not in remaining_data:
            remaining_data += ssl_socket.recv(buffer_size)
        
        chunk_size_str, remaining_data = remaining_data.split(b"\r\n", 1)
        chunk_size = int(chunk_size_str, 16)
        
        # If the chunk size is 0, we're done
        if chunk_size == 0:
            break
        
        # Read the chunk data
        while len(remaining_data) < chunk_size:
            remaining_data += ssl_socket.recv(buffer_size)
        
        body += remaining_data[:chunk_size]
        remaining_data = remaining_data[chunk_size:]
        
        # Read the trailing CRLF after the chunk
        if b"\r\n" not in remaining_data:
            remaining_data += ssl_socket.recv(buffer_size)
        
        remaining_data = remaining_data.split(b"\r\n", 1)[1]
    
    #TODO: implement checks for gzip decoding like we did in H2
    return body.decode("utf-8")
    
    
    
    
#TODO: implemnet HTTP/2 support via h2spacex
    
    
    

def main():
    host = "www.google.com"
    path = "/"
    
    # can simply repeat these 3 steps over and over to send multiple requests on the same connection (socket) note that in our real version we can simply pass all headers to the 
    # send_request() func so theyre not hardcoded within the function itself as they are now.

    # Step 1: Create the connection
    ssl_socket = create_https_connection(host)
    
    # Step 2: Send a request
    headers = "User-Agent: CustomAgent/1.0\r\nConnection: keep-alive\r\n"
    send_request(ssl_socket, host, path, raw_headers=headers)
    
    # Step 3: Receive the response
    headers, body = receive_response(ssl_socket)

    print("Response Headers:")
    print(headers)
    print("\nResponse Body:")
    print(body)

    # Close the connection
    ssl_socket.close()
if __name__ == "__main__":
    main()
    
    
    