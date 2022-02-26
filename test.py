import requests

BASE = "http://127.0.0.1:5000/"

#response = requests.post(BASE+"user/signup",{"username": "bjanka","password": "test123"})
#print(response.json())

response = requests.get(BASE+"user/1",auth=('admin', 'adminpass'))
print(response.json())

#response = requests.put(BASE+"user/edit/1",{"username": "bjankakalajdziska","password": "test123"},auth=('admin', 'adminpass'))
#print(response.json())
