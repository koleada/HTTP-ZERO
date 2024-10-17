# creates a header of arbitrary length
def getHugeHeaderVal(n: int):
    header = 'x'
    headerVal = ""
    for i in range(n):
        headerVal += "="
    return header, headerVal

def main():
    header, val = getHugeHeaderVal(65532)
    # just made it an r-string so i could see it get printed 
    val += r"\r\n"
    print((header, val))
if __name__ == '__main__':
    main()