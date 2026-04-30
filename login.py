import requests

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome",
    "Content-Type": "application/json"
}

email=input("Enter your email: ")
password=input("Enter your password: ")
r=requests.post("https://alpha.celeste.gg/api/v9/auth/login",headers=headers,json={"login":email,"password":password,"undelete":False,"login_source":None,"gift_code_sku_id":None})
if r.status_code==200:
    print("Login successful")
    token = r.json()["token"]
    print(f"Your token is {token}")
else:
    print("Login failed, please try again.")
    print(r.json())