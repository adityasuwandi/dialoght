# -*- coding:utf8 -*-
# !/usr/bin/env python
# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os
import random


from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    action = req.get('queryResult').get('action')
    if action == 'plat':
        res = makeWebhookResult(req)
    return res



def makeWebhookResult(req):

    # print(json.dumps(item, indent=4))

    plat = req.get('queryResult').get('queryText')
    plats = plat[-8:0]
    lind = ["Dilindungi Jasa Raharja", "Tidak Dilindungi Jasa Raharja"]
    listgambar = ["https://www.otoniaga.com/wp-content/uploads/2017/07/6456/angkot-640x426.jpg", "https://asset.kompas.com/crop/102x0:687x390/750x500/data/photo/2016/03/15/1128185Tata-Motors-Angkot-2780x390.jpg", "http://www.promobilsuzuki.com/wp-content/uploads/2017/08/IMG-20170813-WA0011.jpg", "https://asset.kompas.com/crop/80x0:925x563/750x500/data/photo/2018/03/14/318039957.jpg"]
    return {
        "fulfillmentText": "asuuuuuuuuu",
        "fulfillmentMessages": [
          {
            "imageUrl": "http://urltoimage.com",
            "type": 3,
            "card": {
              "title": plats,
              "subtitle": random.choice(lind),
              "imageUri": random.choice(listgambar),
            }
          }
        ]
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
