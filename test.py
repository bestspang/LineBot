#from PIL import Image
#import requests
#from io import BytesIO
import urllib.request
url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRFS69FbmZBwkmCWtGWwDrA7YJyEpAmMyLHZ07FACjet8gxVX5WZ0DtVy2yW644QkY4d8UGctjfej0s/pubchart?oid=1508988021&format=image"
#response = requests.get(url)
#img = Image.open(BytesIO(response.content))

urllib.request.urlretrieve(url, "image.png")
