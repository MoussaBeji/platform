# -*- coding: utf-8 -*-
import requests
import sys
import conf



port = sys.argv[1]
try:
    code = 404
    url = conf.URL + ':' + str(port) +'/remove/*'
    r = requests.head(url)
    code = r.status_code
    print("{0} successful action.".format(code))
except:
    print("failure action!")





