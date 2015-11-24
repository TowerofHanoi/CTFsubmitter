#TODO
#vedere exploit per hm
import requests


def darkmagic():
    userdata={"team":"4", "service":"SERVICE","flags":"FLAG"}
    url="localhost:8080" #REPLACE with actual url
    try:
        submit=requests.post(url,data=userdata,timeout=5)
    except:
        pass
