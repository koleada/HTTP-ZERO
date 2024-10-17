class HTTPResponse:
    """Represents an HTTP response."""

    def __init__(self, status_code, headers, body, http_version):
        """
        Initializes an HTTPResponse object.

        Args:
            status_code (int): The HTTP status code.
            headers (dict): A dictionary containing the response headers.
            body (str|bytes): The response body.
            http_version (str): The HTTP version of the response as a string - either HTTP/1 or HTTP/2. 
        """
        self._status_code = status_code
        self._headers = headers
        self._body = body
        self._http_version = http_version

    @property
    def status_code(self):
        """Gets the HTTP status code."""
        return self._status_code

    @property
    def headers(self):
        """Gets the response headers."""
        return self._headers

    @property
    def body(self):
        """Gets the response body."""
        return self._body
    def http_version(self):
        """Gets the response body."""
        return self._http_version
    
    def __str__(self): 
        return self._headers + "\n\n" + self._body

    def isSplitResp(self):
        # This is very useful if we choose to implement more CRLF testing. HTTP response splitting often can happen by injecting a GET request (similar to our smuggled request) via CRLF 
        # causing the resulting response to be split
        if self.http_version == 'HTTP/1':
            if self.body and self.headers:
                return self.body.count('HTTP/1') > 0 or self.body.count
            else:
                return None
        else:
            if self.body and self.headers:
                if self.body.count(':status') > 0:
                    return True
                elif self.body.count('HTTP/1') > 0:
                    return True
            else:
                return None
    
    def is_cached(self):
        """
        Checks if the response was cached.

        This function is currently unimplemented.
        """
        raise NotImplementedError("is_cached is not implemented yet")
    
class HTTPRequest:
    """Represents an HTTP request."""

    def __init__(self, method, host, path, http_version, headers, body=None):
        """
        Initializes an HTTPRequest object.

        Args:
            method (str): The HTTP method (e.g., GET, POST, PUT, DELETE).
            host (str): The hostname of the server.
            path (str): The path of the request.
            http_version (str): Indicates if this request is HTTP/1.1 or HTTP/2
            headers (dict, optional): A dictionary containing the request headers. Defaults to {}.
            body (str|bytes, optional): The request body. Defaults to None.
        """
        self._method = method
        self._host = host
        self._path = path
        self._http_version = http_version
        self._headers = {}
        self._body = body
        
        
        if isinstance(headers, list):
            for key, value in headers:
                self._headers[key] = value
        elif isinstance(headers, str):
            for line in headers.splitlines():
                if line:
                    key, value = line.split(':', 1)
                    self._headers[key.strip()] = value.strip()


    @property
    def method(self):
        """Gets the HTTP method."""
        return self._method

    @property
    def host(self):
        """Gets the hostname of the server."""
        return self._host

    @property
    def path(self):
        """Gets the path of the request."""
        return self._path

    @property
    def headers(self):
        """Gets the request headers."""
        return self._headers

    @property
    def body(self):
        """Gets the request body."""
        return self._body
    
    @property
    def http1(self):
        """Gets the request body."""
        return self._http1

    def __str__(self):
        """Returns a string representation of the HTTP request.""" 
        headers_str = "\n".join(f"{key}: {value}" for key, value in self._headers.items())
        
        if self._body:
            return f"{self._method} {self._path} {self._http_version}\n{headers_str}\n\n{self._body}\n"
        else:
            return f"{self._method} {self._path} {self._http_version}\n{headers_str}\n"