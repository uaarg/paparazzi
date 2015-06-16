import httplib, urllib
LOGIN_PATH = "/api/login"
TELEM_PATH = "/api/interop/uas_telemetry"
SERVER_INFO_PATH = "/api/interop/server_info"
USERNAME = 'testuser'
PASSWORD = 'testpass'

headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}
conn = httplib.HTTPConnection("localhost", 8080)
params = urllib.urlencode({'username': USERNAME, 'password': PASSWORD })

#LOGIN
conn.request("POST", LOGIN_PATH , params, headers)
response = conn.getresponse()
print response.read()

#Saving Login Cookie Credentials
setcookie = response.getheader("Set-Cookie")
contenttype = response.getheader("Content-type")
headers = {"Accept": "text/plain", "Cookie" : setcookie, "Content-type" : "application/x-www-form-urlencoded"}

#Posting
params = urllib.urlencode({'latitude': 10, 'longitude': 10, 'altitude_msl': 10, 'uas_heading': 10})
conn.request("POST", TELEM_PATH, params, headers)
response = conn.getresponse()
print response.status, response.reason
print response.read()


conn.close()