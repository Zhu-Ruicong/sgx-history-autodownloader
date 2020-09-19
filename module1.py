import requests

pre_url = "https://links.sgx.com/1.0.0/derivatives-historical/"
post_url = "/TC.txt"
url = pre_url + str(4724) + post_url
h = requests.head(url, allow_redirects=True)
header = h.headers
d = header.get("Content-Disposition")[24:-4]
print(header)
