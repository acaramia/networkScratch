from socket import gethostname,gethostbyname
my_ip= gethostbyname(gethostname()) #get our IP. Be careful if you have multiple network interfaces or IPs
print(my_ip)

import httplib2