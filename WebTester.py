'''
Mateya Berezowsky
V00994661

WebTester Program:
- Connects to a server based on the provided URL.
- Sends an HTTP request and parses the response.
- Prints information about the host, HTTP version support (HTTP/1.1 or HTTP/2), password protection, and cookies.

Functionality:
- Handles URL parsing, server connection, and response handling.
- Supports HTTP/1.1 and HTTP/2, with fallback to HTTP/1.1.
- Manages cookies and checks for password protection.
- Handles redirection and prints relevant details about the response.

'''

import ssl
import socket
import sys


class HttpResponse:
    '''
    The HttpResponse class manages and processes HTTP responses.
    It stores relevant variables for a request and handles the response parsing.
    '''

    def __init__(self):
        self.response = b""
        self.host = None
        self.port = 443
        self.path = None
        self.h2 = False
        self.cookies = []
        self.password_protected = False
        self.redirect = False
        

    def parse_arguments(self, location=None):
        '''
        Parses the provided URL or a URL from stdin to extract the host, path, and port.
        If no URL is provided, prints an error message and exits. Handles URL redirection if necessary.
        '''
        
        if(not self.redirect):
            if (len(sys.argv) < 2):
                print("Please Enter URL.")
                sys.exit(1)

            elif(len(sys.argv) > 2):
                print("Too many arguments, please enter only the URL.")
                sys.exit(1)
            
            url = sys.argv[1]
        else:
            url = location

        if '//' in url:
            url = url.split('//', 1)[1]

        if '/' in url:
            self.host, self.path = url.split('/', 1)
            self.path = '/' + self.path
        else:
            self.host = url
            self.path = '/'
        
        if ':' in self.host:
            self.host, self.port = self.host.split(':', 1)
            self.port = int(self.port)


    def send_request(self):
        '''
        Sends an HTTP request to the server. Assumes HTTPS by default, and if HTTPS is not possible,
        will try HTTP. Determines if HTTP/1.1 or HTTP/2 is supported and then forces HTTP/1.1.
        '''

        context = ssl.create_default_context()
        if(self.h2):
            #forcing http/1.1 connection 
            context.set_alpn_protocols(['http/1.1'])
        else:
            #negotiating 1.1 ot 2
            context.set_alpn_protocols(['http/1.1', 'h2'])
        try:
            with socket.create_connection((self.host,self.port)) as sock:
                with context.wrap_socket(sock,server_hostname=self.host) as ssock:
                        alpn_protocol = ssock.selected_alpn_protocol()
                        if(alpn_protocol == "h2"):
                            self.h2 = True
                            self.send_request()
                            #confirmed http/2 support now forcing http/1.1
                        else:
                            #sending request
                            request = f"GET {self.path} HTTP/1.1\r\nHost: {self.host}\r\nConnection: close\r\n\r\n"
                            ssock.send(request.encode())
                            self.response = ssock.recv(10000) 
                            self.response = self.response.decode('utf-8')
                        
        except (ssl.SSLError) as e:
            #no https support so send http request
            if(self.port == 443):
                self.port = 80
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.host,self.port))
            request = f"GET {self.path} HTTP/1.1\n\n"
            sock.send(request.encode())
            self.response = sock.recv(10000)
            sock.close()
            self.response = self.response.decode('utf-8')

        except (socket.gaierror, socket.error) as e:
            print(f"Problem with URL and server connection. Please re-enter URL.\nError:\n",e)
            sys.exit(1)


    def parse_response(self):
        '''
        Parses the HTTP response and handles various status codes, including password protection,
        redirection, and error handling. Also retrieves cookies from the response headers.
        '''

        status_code = self.response.splitlines()[0].split()[1]
        if(status_code == "401"):
            self.password_protected = True
        elif(status_code == "302" or status_code == "301"):
            print(f"\nRedirecting...")
            #redirection is needed. Get new url and send request again.
            self.redirect = True
            location = None
            lines = self.response.strip().split('\n')
            #Finding new location
            for line in lines:
                if line.startswith('Location:'):
                    location = line[len('Location: '):].strip()
                    self.host = location
                    self.parse_arguments(location)
                    self.send_request()
                    self.parse_response()
            if(location == None):
                print(f"{status_code} found but can't redirect. Enter a new URL")
                sys.exit(1)
        elif(status_code == "505"):
            print("Server can't support HTTP/1.1. Enter a new URL.")
            sys.exit(1)
        elif(status_code == "404"):
            print('404 not Found. Enter a new URL.')
            sys.exit(1)
        elif(status_code != "200"):
            print('Unknown status code. Enter a new URL.')
            sys.exit(1)

        #get cookies
        lines = self.response.strip().split('\n')
        for line in lines:
                if line.startswith('Set-Cookie:'):
                    cookie = line[len('Set-Cookie: '):].strip()
                    self.cookies.append(cookie)
        
    def print_output(self):
        '''
        Prints the output, including details about cookies, HTTP/1.1 or HTTP/2 support,
        password protection, and the server name.
        '''

        output = f'\n\nwebsite: {self.host}\n1. Supports http2: {self.h2}\n2. List of Cookies:\n'
        if(self.cookies):
            for cookie in self.cookies:
                cookie_parts = cookie.split(';')
                
                name_value = cookie_parts[0].split('=')
                name = name_value[0] if len(name_value) > 1 else 'None'
                
                #If expire time and domain are not found default is None
                expire = 'None'
                domain = 'None'
                
                for part in cookie_parts[1:]:
                    part = part.strip()
                    if part.startswith('expires='):
                        expire = part[len('expires='):].strip()
                    elif part.startswith('domain='):
                        domain = part[len('domain='):].strip()

                output += f'cookie name: {name}, expires time: {expire}, domain name: {domain}\n'
        else:
            output += f'cookie name: None\n'

        output += f'3. Password-protected: {self.password_protected}\n\n'
        print(output)

    def print_response(self):
        print(f"Server response:\n")
        print(self.response)
        print(f"\n---------------------------------------------\n")
        print(f"End of response.\n")

        


def main():
    '''
    Main entry point of the program.
    Creates an HttpResponse instance, parses the arguments, sends the request,
    parses the response, and finally prints the output.
    '''
    
    http_response = HttpResponse()

    http_response.parse_arguments()
    http_response.send_request()
    http_response.parse_response()
    http_response.print_output()

    #Uncomment the line below to see server response
    #http_response.print_response()

    

if __name__ == "__main__":
    main()