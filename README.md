# Computer Communications and Networks

## Description:
This program takes a URL from the user via stdin, sends an HTTP request, and parses the response to determine the following:
1. Whether the server supports HTTP/2.
2. Whether the server provides cookies, and if so, their name, expiration time, and domain (if applicable).
3. Whether the site is password-protected.
4. The name of the server.

---

## How to Run the Program:

1. Make sure you are using Python 3.
2. Enter the following command in your terminal:

   ```bash
   python3 WebTester.py <url>
   ```

   Replace `<url>` with the website you want to check.
   Ex: www.some_site.ca
   ```bash
   python3 WebTester.py www,uvic.ca
   ```

### Accepted Input:
The URL should be in the following format:

```
protocol://host[:port]/filepath
```

- The protocol, port, and path are optional, but an accurate host is required.

#### Preferred Input Format:
```
www.someServer.ca
```

---

## Output:
For a valid URL, the program will provide the following output:

```plaintext
Website: www.someSite.ca
1. Supports http2: (True/False)
2. Cookies:
   - Cookie-name: name, expire, domain
3. Password-protected: (true/false)
```

### Notes:
- If there are no cookies, the program will output `None`.
- If there are cookies but no expiration or domain details, the fields will show `None` for those values.

---

## Errors and Status Codes:

- **Invalid URL or Connection Failure**: If a connection cannot be made with the server or an invalid URL is provided, the program will terminate and prompt the user to re-run the program.
  
- **HTTP Status Codes**: 
  - Status codes like `404`, `505`, or other errors will end the program and prompt the user to retry with a valid URL.
  - If a status code of `302` or `301` (redirection) is detected, the program will redirect the request to the new location. The output will include an additional line:
  
    ```plaintext
    Redirection... (indicating the request is being redirected)
    ```
  
- **Authentication Required**:
  - If the status code `401 Unauthorized` is found, the program will indicate that further authentication is required. The "Password-protected" field will reflect this behavior in the output, which will be printed as usual.

---

## Debugging:
If you wish to view the full HTTP response from the server for debugging purposes, uncomment the `http_response.print_response()` line in the main function. This can help identify any unexpected behavior.

---

## Assignment Information:
This tool was created as part of an assignment for a Computer Communications and Networks course. The goal was to develop a Python-based web client to analyze server capabilities and assess HTTP support, cookies, and authentication requirements.

