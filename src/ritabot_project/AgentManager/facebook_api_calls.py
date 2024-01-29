from AgentManager.models import *

import requests
import json


class PersistentMenu():
    # https://developers.facebook.com/docs/messenger-platform/reference/messenger-profile-api/#profile_properties
    def __init__(self, agentID):
        agent = Agent.objects.get(id=agentID)
        print("agent :", agent)
        self.access_token = agent.access_token
        print("hey there init :", self.access_token)
    def DELETE(self):
        PAGE_ACCESS_TOKEN = self.access_token
        print("page access token :", PAGE_ACCESS_TOKEN)
        res = requests.delete("https://graph.facebook.com/v2.6/me/messenger_profile",
                             params={"access_token": PAGE_ACCESS_TOKEN},
                             headers={"Content-Type": "application/json"},
                             data=json.dumps({
                                 "fields": ["persistent_menu"]
                             })
                             )
        print(res.status_code)
        return res.status_code

    def POST(self, persistent_menu):
        PAGE_ACCESS_TOKEN = self.access_token
        res = requests.post("https://graph.facebook.com/v2.6/me/messenger_profile",
                             params={"access_token": PAGE_ACCESS_TOKEN},
                             headers={"Content-Type": "application/json"},
                             data=json.dumps(persistent_menu)
                             )
        return res.status_code

    def GET(self):
        pass


class GetStarted():
    # https://developers.facebook.com/docs/messenger-platform/reference/messenger-profile-api/#profile_properties
    def __init__(self, agentID):
        agent = Agent.objects.get(id=agentID)
        print("agent :", agent)
        self.access_token = agent.access_token
        print("hey there init :", self.access_token)

    def DELETE(self):
        PAGE_ACCESS_TOKEN = self.access_token
        res = requests.delete("https://graph.facebook.com/v2.6/me/messenger_profile",
                             params={"access_token": PAGE_ACCESS_TOKEN},
                             headers={"Content-Type": "application/json"},
                             data=json.dumps({
                                 "fields": ["get_started"]
                             })
                             )
        return res.status_code

    def POST(self):
        PAGE_ACCESS_TOKEN = self.access_token

        res = requests.post("https://graph.facebook.com/v2.6/me/messenger_profile",
                             params={"access_token": PAGE_ACCESS_TOKEN},
                             headers={"Content-Type": "application/json"},
                             data=json.dumps({
                                    "get_started": {
                                        "payload": "58108524103242b03af9d44b72dd6b6c9280072e 140ccda42adea5f48c8a617171f3f21d61f6454f"
                                    }
                                })
                             )
        if res.status_code == 200:
            return True
        else:
            raise Exception("An error occured while trying to call configuring the get started button for the given agent.")

    def GET(self):
        PAGE_ACCESS_TOKEN = self.access_token
        res = requests.get("https://graph.facebook.com/v6.0/me/messenger_profile?fields=get_started&access_token="+PAGE_ACCESS_TOKEN)
        data = res.json()
        if res.status_code == 200:
            if len(data['data']) > 0:
                return True
            else:
                return (self.POST())

        else:
            raise Exception("An error occured while trying to call the facebook api while getting the get started button for given agent.")
