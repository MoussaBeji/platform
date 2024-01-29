from AgentManager.models import *
from AgentManager.serializers import *


def ReturnMenu(button):

    def recursive(button):
        if button.type == "web_url":
            web_url_button = dict()
            web_url_button["type"] = button.type
            web_url_button["title"] = button.name
            web_url_button["url"] = button.url
            web_url_button["webview_height_ratio"] = "tall"
            return web_url_button

        elif button.type == "postback":
            postback_button = dict()
            postback_button["type"] = button.type
            postback_button["title"] = button.name
            postback_button["payload"] = button.payload
            return postback_button

        else:
            buttons_queryset = Button.objects.filter(sub_menu=button)
            if len(buttons_queryset) > 0:
                nested_button = dict()
                nested_button["type"] = button.type
                nested_button["title"] = button.name
                nested_button["call_to_actions"] = []
                for btn in buttons_queryset:
                    x = recursive(btn)
                    nested_button["call_to_actions"].append(x)
                return nested_button

    a = recursive(button)
    return a


def persistent_menu_json(menuID):
    menu = Menu.objects.get(id=menuID)
    buttons_queryset = Button.objects.filter(menu=menu)
    if len(buttons_queryset) > 0:
        persistent_menu = dict()
        persistent_menu["persistent_menu"] = [{"locale": "default", "call_to_actions": []}]
        for btn in buttons_queryset:
            btn_json = ReturnMenu(btn)
            persistent_menu["persistent_menu"][0]["call_to_actions"].append(btn_json)
        return persistent_menu