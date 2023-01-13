---
name: Bug report
about: Create a report to help us improve
title: ''
labels: ''
assignees: ''

---

### Configuration  
impacket version:  
Python version:  
Target OS:  

### Debug Output With Command String  
i.e.  
turbosearch -t http://sec4us.com.br -w comuns.txt
```
turbosearch -t http://sec4us.com.br -w comuns.txt

 [+] Startup parameters
     command line: turbosearch -t http://sec4us.com.br -w comuns.txt
     target: http://127.0.0.1
     tasks: 16
     request method(s): GET
     word list: comuns.txt
     forward location redirects: yes
     case insensitive search: no
     start time 2023-01-13 15:32:20
     duplicate 46 words

 [+] Conectivity checker
 [!] Error connecting to url http://sec4us.com.br without proxy
 [!] Error: HTTPConnectionPool(host='127.0.0.1', port=80): Max retries exceeded with url: / (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x103911af0>: Failed to establish a new connection: [Errno 61] Connection refused'))

```

### Additional context  
Space for additional context, investigative results, suspected issue.
