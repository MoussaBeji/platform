

from .models import *
import os
import json
from ritabot.settings import AGENT_IMAGES_URL
#data_path = "/var/lib/jenkins/workspace/ritabot/src/ritabot_project/AI/data/"
#training_path = "/var/lib/jenkins/workspace/ritabot/src/ritabot_project/AI/"
training_path = os.getcwd()+"/AI/"
data_path = os.getcwd()+"/AI/data/"
def Sort_Entity(e):
  return e['id']

def generate_json(user_id, agent_id):
    # without context for now
    intents = Intent.objects.filter(agent_id=agent_id, is_none_response = False, is_depart=False)
    if len(intents) == 0:
        message = "this agent has no intents to train."
        return message
    corepus = dict()
    corepus['data'] = []  # will contain list of intents (json format)

    """Generate the relay intent that will relate the considering agents """
    try:
        agent = Agent.objects.get(id = agent_id)
    except:
        return("this agent was not found")

    for intent in intents:
        #print("generating training file")
        intent_dict = dict()
        """Context generation"""
        input_context=InputContext.objects.filter(intent_id=intent.id)
        output_context=OutputContext.objects.filter(intent_id=intent.id)
        input_context_list=[]
        output_context_list=[]
        for inContext in input_context:
            input_context_list.append(inContext.outContext.outContext)

        if (len(input_context_list)>0):
            intent_dict["context_filter"]=input_context_list

        for outContext in output_context:
            output_context_list.append(outContext.outContext)

        if (len(output_context_list) > 0):
            intent_dict["context_set"] = output_context_list
        """End Context generation"""
        #print("####step1")

        intent_dict["tag"] = intent.name
        questions = Question.objects.filter(intent_id=intent.id)
        # add questions to dict
        if len(questions) == 0:
            message = "intent with id " + str(intent.id) + " has no questions to train."
            return message
        questions_list = []
        #print("####step2")
        for question in questions:
            questions_list.append(question.name)
        intent_dict["patterns"] = questions_list
        # verify type of response
        try:
            response_set = BlockResponse.objects.filter(intent_id=intent.id)
        except Exception as e:
            message = "intent with id " + intent.id + " has no answer." + e
            return message


        intent_dict["block_response"] = dict()
        # intent_dict["object"] = dict()
        # intent_dict["responses"] = dict()
        exist_fulfillment = False
        if intent.fulfillment is not None and intent.fulfillment.replace(" ","") !="":
            exist_fulfillment = True
            fulfillment=intent.fulfillment
            intent_dict["Fulfillment"] = dict()
            intent_dict["Fulfillment"]["code"] = fulfillment
            intent_dict["Fulfillment"]["entitys"] = []
            entitys = intent.related_entity.all()

            for entity in entitys:
                name=entity.entity.name
                modifyedName="$"+name
                intent_dict["Fulfillment"]["entitys"].append(modifyedName)

        if exist_fulfillment:
            intent_dict['block_response']['default']=dict()
            intent_dict['block_response']['default']['object']=[]
            intent_dict['block_response']['default']['object'].append({"type": "simple","value": {}})
            intent_dict['block_response']['default']['responses'] = []
            intent_dict['block_response']['default']['responses'].append("for fullfilment response _ generated automatically")

        else:
            for bc_response in response_set:
                intent_dict['block_response'][bc_response.category.lower()] = dict()
                intent_dict['block_response'][bc_response.category.lower()]["object"] = []
                intent_dict['block_response'][bc_response.category.lower()]["responses"] = []
                #print("###Here")
                if not bc_response.is_complex:
                    # simple response
                    #print("simple response")
                    simple_answers = SimpleResponse.objects.filter(block_response_id=bc_response.id)
                    random_texts = RandomText.objects.filter(simple_response__in=simple_answers)
                    random_texts_list = []
                    if len(random_texts) == 0:
                        message = "No simple responses to show to client."
                        return message
                    for text in random_texts:
                        random_texts_list.append(text.name)

                    intent_dict['block_response'][bc_response.category.lower()]["responses"] = random_texts_list
                    empty_object = dict()
                    empty_object['type'] = "simple"
                    empty_object['value'] = dict()
                    intent_dict['block_response'][bc_response.category.lower()]["object"].append(empty_object)
                    # intent_dict['block_response'][bc_response.category.lower()]["object"]

                else:
                    intent_dict['block_response'][bc_response.category.lower()]["responses"] = ['']

                    try:
                        complex_response_set = MixedResponse.objects.filter(block_response_id=bc_response.id)

                    except Exception as e:
                        message = "problem loading Mixed response: "
                        return message
                    #here
                    # for complex_response in complex_response_set:
                    #     intent_dict['object'][str(complex_response.category)] = []
                    # intent_dict['object']["man"] = []
                    # intent_dict['object']["woman"] = []
                    # intent_dict['object']["default"] = []
                    for complex_response in complex_response_set:
                        object = dict()
                        object["type"] = 'nested'
                        object['value'] = dict()
                        responses = []

                        try:

                            #text_responses = TextResponse.objects.filter(mixed_response_id=complex_response.id)
                            text_responses = complex_response.text_response_set.all()
                            # #print("___________________ intent=",intent.name)
                            # #print("___________________ complex=",complex_response.id)
                            # #print("___________________ txt_len=",len(text_responses))
                        except Exception as e:
                            message = "problem loading Mixed response: "
                            return message

                        text_responses_list = []
                        for text in text_responses:

                            text_dict = dict()
                            text_dict["type"] = "TextResponse"
                            text_dict["order"] = text.order
                            text_dict["value"] = dict()
                            buttons = Button.objects.filter(text_response_id=text).order_by("order")
                            #print("buttons for text_response: ", len(buttons))
                            if len(buttons) != 0:
                                text_dict["value"]["attachment"] = dict()
                                text_dict["value"]["attachment"]["type"] = "template"
                                text_dict["value"]["attachment"]["payload"] = dict()
                                text_dict["value"]["attachment"]["payload"]["template_type"] = "button"
                                text_dict["value"]["attachment"]["payload"]["text"] = text.name
                                text_dict["value"]["attachment"]["payload"]["buttons"] = []
                                for btn in buttons:
                                    if btn.url is not None:
                                        json_btn = dict()
                                        json_btn['type'] = 'web_url'
                                        json_btn['url'] = btn.url
                                        json_btn['title'] = btn.name
                                        json_btn['webview_height_ratio'] = "full"
                                        json_btn['messenger_extensions'] = btn.messenger_extensions
                                        text_dict["value"]["attachment"]["payload"]["buttons"].append(json_btn)
                                    elif btn.phone_number is not None:
                                        json_btn = dict()
                                        json_btn['type'] = 'phone_number'
                                        json_btn['payload'] = btn.phone_number
                                        json_btn['title'] = btn.name
                                        text_dict["value"]["attachment"]["payload"]["buttons"].append(json_btn)
                                    else:
                                        json_btn = dict()
                                        json_btn['type'] = 'postback'
                                        json_btn['payload'] = btn.payload
                                        json_btn['title'] = btn.name
                                        text_dict["value"]["attachment"]["payload"]["buttons"].append(json_btn)

                            else:
                                #print("This is a simple text without buttons")
                                text_dict["value"]["text"] = text.name
                            text_responses_list.append(text_dict)
                        responses += text_responses_list
                        # if complex_response.id in [229,230]:
                        #     print("___________________ intent=", intent.name)
                        #     print("___________________ complex=", complex_response.id)
                        #     print("___________________ text_responses_list=", text_responses_list)
                        #     print("___________________ responses=", responses)
                        # generate galleries
                        galleries = Gallery.objects.filter(mixed_response_id=complex_response.id)
                        galleries_list = []
                        for gallery in galleries:
                            gallery_dict = dict()
                            gallery_dict["type"] = "Gallery"
                            gallery_dict["order"] = gallery.order
                            gallery_dict["value"] = dict()
                            gallery_dict["value"]["attachment"] = dict()
                            gallery_dict["value"]["attachment"]["type"] = "template"
                            gallery_dict["value"]["attachment"]["payload"] = {}
                            gallery_dict["value"]["attachment"]["payload"]["template_type"] = "generic"
                            gallery_dict["value"]['attachment']['payload']['elements'] = []
                            # generate sliders of this specific gallery:
                            sliders = Slider.objects.filter(gallery_id=gallery.id).order_by("order")
                            for slider in sliders:
                                json_slider = dict()
                                json_slider['title'] = slider.title
                                try:
                                    if slider.image:
                                        json_slider['image_url'] = AGENT_IMAGES_URL + slider.image.url
                                except:
                                    #print("cannot load image url")
                                    pass
                                try:
                                    if slider.subtitle:
                                        json_slider['subtitle'] = slider.subtitle
                                except:
                                    pass
                                    #print("cannot card subtitle")
                                try:
                                    if slider.url:
                                        json_slider['default_action'] = {}
                                        json_slider['default_action']['type'] = 'web_url'
                                        json_slider['default_action']['url'] = slider.url
                                        json_slider['default_action']['webview_height_ratio'] = 'tall'

                                except:
                                    pass
                                    #print("cannot load card default action")
                                try:
                                    #print(slider.id)
                                    buttons = Button.objects.filter(slider_id=slider).order_by("order")
                                    #print("buttons ================================>", buttons)
                                    if len(buttons) != 0:
                                        json_slider['buttons'] = []
                                        for btn in buttons:
                                            if btn.url is not None:
                                                json_btn = dict()
                                                json_btn['type'] = 'web_url'
                                                json_btn['url'] = btn.url
                                                json_btn['title'] = btn.name
                                                json_btn['webview_height_ratio'] = "full"
                                                json_btn['messenger_extensions'] = btn.messenger_extensions
                                                json_slider['buttons'].append(json_btn)
                                            elif btn.phone_number is not None:
                                                json_btn = dict()
                                                json_btn['type'] = 'phone_number'
                                                json_btn['payload'] = btn.phone_number
                                                json_btn['title'] = btn.name
                                                json_slider['buttons'].append(json_btn)
                                            else:
                                                json_btn = dict()
                                                json_btn['type'] = 'postback'
                                                json_btn['payload'] = btn.payload
                                                json_btn['title'] = btn.name
                                                json_slider['buttons'].append(json_btn)
                                except:
                                    pass
                                    #print("no buttons to add to card")
                                gallery_dict["value"]['attachment']['payload']['elements'].append(json_slider)
                            galleries_list.append(gallery_dict)
                        responses += galleries_list
                        # generate quick replies
                        quick_replies = QuickReply.objects.filter(mixed_response_id=complex_response.id)
                        quick_replies_list = []
                        for reply in quick_replies:
                            qr_dict = dict()
                            qr_dict["type"] = "QuickReply"
                            qr_dict["order"] = reply.order
                            qr_dict["value"] = dict()
                            qr_dict["value"]["text"] = reply.name
                            qr_dict["value"]["quick_replies"] = []
                            qr_buttons = Button.objects.filter(quick_reply_id=reply.id).order_by('order')
                            for btn in qr_buttons:
                                qr_btn = dict()
                                qr_btn["content_type"] = "text"
                                qr_btn["title"] = btn.name
                                qr_btn["payload"] = btn.payload
                                qr_dict["value"]["quick_replies"].append(qr_btn)
                            quick_replies_list.append(qr_dict)
                        responses += quick_replies_list
                        # generate images
                        images = Image.objects.filter(mixed_response_id=complex_response.id)
                        images_list = []
                        for image in images:
                            image_dict = dict()
                            image_dict["type"] = "Image"
                            image_dict["order"] = image.order
                            image_dict["value"] = dict()
                            image_dict["value"]["attachment"] = dict()
                            image_dict["value"]["attachment"]["type"] = "image"
                            image_dict["value"]["attachment"]["payload"] = dict()
                            image_dict["value"]["attachment"]["payload"]["url"] = AGENT_IMAGES_URL + image.image.url
                            images_list.append(image_dict)
                        responses += images_list

                        # generate audio
                        audios = intent.related_audios.all()
                        audios_list = []
                        for audio in audios:
                            audio_dict = dict()
                            audio_dict["type"] = "Audio"
                            audio_dict["order"] = 1000
                            audio_dict["value"] = dict()
                            audio_dict["value"]["attachment"] = dict()
                            audio_dict["value"]["attachment"]["type"] = "audio"
                            audio_dict["value"]["attachment"]["payload"] = dict()
                            audio_dict["value"]["attachment"]["payload"]["url"] = AGENT_IMAGES_URL + audio.audio.audio.url
                            audios_list.append(audio_dict)
                        responses += audios_list

                        # generate videos
                        videos = intent.related_videos.all()
                        videos_list = []
                        for video in videos:
                            video_dict = dict()
                            video_dict["type"] = "Video"
                            video_dict["order"] = 1020
                            video_dict["value"] = dict()
                            video_dict["value"]["attachment"] = dict()
                            video_dict["value"]["attachment"]["type"] = "video"
                            video_dict["value"]["attachment"]["payload"] = dict()
                            video_dict["value"]["attachment"]["payload"]["url"] = AGENT_IMAGES_URL + video.video.video.url
                            videos_list.append(video_dict)
                        responses += videos_list

                        # sort responses by key :order
                        responses = sorted(responses, key=lambda i: i['order'])
                        # intent_dict['object']['value'] = dict()
                        counter = 1

                        for response in responses:
                            # types:  TextResponse, Gallery, QuickReply, Image
                            if response["type"] != "TextResponse":
                                object['value']["text"+str(counter)] = ""
                                object['value']["obj" + str(counter)] = response["value"]
                                counter += 1
                            else:
                                if "attachment" in response["value"]:
                                    # this is a text response with buttons
                                    object['value']["text" + str(counter)] = ""
                                    object['value']["obj" + str(counter)] = response["value"]
                                    counter += 1
                                else:
                                    object['value']["text" + str(counter)] = response["value"]["text"]
                                    object['value']["obj" + str(counter)] = dict()
                                    counter += 1

                        #print("object", object)
                        #intent_dict['object'][str(response.category)] = []
                        intent_dict['block_response'][bc_response.category.lower()]["object"].append(object)
                        # intent_dict['object']["woman"].append(object)
                        # intent_dict['object']["default"].append(object)


                    # intent_dict["object"]["type"] = 'nested'
                    # intent_dict['object']['value'] = dict()
                    #


        corepus['data'].append(intent_dict)


        """Genarate Entitys"""

        # generate videos
        entitys = intent.related_entity.all().order_by('id')
        # entitys.sort(key=Sort_Entity)
        if entitys.count()>0:
            intent_dict["entity"] = dict()
            entitys_list = []
            for entity in entitys:
                entity_dict = dict()
                lst=[]
                values =entity.entity.value_set.all()
                for value in values:
                    lst.append(value.value)
                    synonymes = [x.synonyme for x in value.synonyme_set.all()]
                    lst+=synonymes
                if entity.entity.is_default:
                    intent_dict["entity"]["{}".format(entity.entity.name)] = dict()
                    intent_dict["entity"]["{}".format(entity.entity.name)]['value'] = True
                    intent_dict["entity"]["{}".format(entity.entity.name)]['prompt'] = entity.prompt_response
                else:
                    intent_dict["entity"]["{}".format(entity.entity.name)] = dict()
                    intent_dict["entity"]["{}".format(entity.entity.name)]['value'] = lst
                    intent_dict["entity"]["{}".format(entity.entity.name)]['prompt'] = entity.prompt_response
            default_entity = intent.agent.agent.all().exclude(is_default=False)

            for defEntity in default_entity:
                relation_with_intent = defEntity.entity.all()
                verif=False
                for relation in relation_with_intent:
                    if relation.intent.id == intent.id:
                        verif=True
                if not verif:
                    intent_dict["entity"]["{}".format(defEntity.name)] = dict()
                    intent_dict["entity"]["{}".format(defEntity.name)]['value'] = False
                    intent_dict["entity"]["{}".format(defEntity.name)]['prompt'] = ""
                else:
                    pass


        """End Genarating entitys"""

        """Generate the navigation intent params"""
        nav_list=intent.related_navigation.all()
        if nav_list:
            nav=nav_list[0]

            depending_intent=nav.related_depending.all()
            intent_dict["require"] = dict()
            intent_dict["require"]['nb_tentative'] = nav.nb_tentative
            intent_dict["require"]['redirection'] = nav.redirection.name
            intent_dict["require"]['echec'] = nav.echec.name
            intent_dict["require"]['depondant'] = []
            for dep in depending_intent:
                intent_dict["require"]['depondant'].append(dep.intent.name)

        """End Generating navigation intent params"""




    path = os.path.join(data_path, "folder_user_{}".format(user_id), "agent_{}".format(agent_id))
    if not os.path.exists(path):
        os.makedirs(path)
    with open(os.path.join(path, "data.json"), 'w', encoding='utf-8') as training_file:
        json.dump(corepus, training_file, ensure_ascii=False, indent=4)

    #print("####step5")

    path = os.path.join(data_path, "folder_user_{}".format(user_id), "agent_{}".format(agent_id))
    if not os.path.exists(path):
        os.makedirs(path)
    with open(os.path.join(path, "data.json"), 'w', encoding='utf-8') as training_file:
        json.dump(corepus, training_file, ensure_ascii=False, indent=4)
    #fileName = "data.json"+str(agent_id)+".json"
    #print("####step6")



    """This will be checked"""

    # without context for now
    intents = Intent.objects.filter(agent_id=agent_id, is_none_response=True)  | Intent.objects.filter(agent_id=agent_id,is_depart=True)
    if len(intents) == 0:
        message = "this agent has no intents to train."
        return message
    corepus = dict()
    corepus['data'] = []

    related_agent = agent.related_agent.agents.all()
    if agent.is_main:
        #print("generating the relay intent")
        intent_dict = dict()
        intent_dict["tag"] = "relay_intent"

        intent_dict["patterns"] = ["a45ec879abd5879fd545ae545ccv6910ab3ffe59"]
        agent_list= []
        for r_agent in related_agent:
            agent_info = dict()
            agent_info["language"] = r_agent.language
            agent_info["port"] = r_agent.port
            agent_info["id"] = r_agent.id
            agent_list.append(agent_info)
        intent_dict["responses"] = agent_list
        intent_dict["object"]= {
            "type": "simple",
            "value": {}
        }
        corepus['data'].append(intent_dict)
    else:
        pass


    for intent in intents:
        #print("generating training file")
        intent_dict = dict()
        """Context generation"""
        input_context=InputContext.objects.filter(intent_id=intent.id)
        output_context=OutputContext.objects.filter(intent_id=intent.id)
        input_context_list=[]
        output_context_list=[]
        for inContext in input_context:
            input_context_list.append(inContext.outContext.outContext)

        if (len(input_context_list)>0):
            intent_dict["context_filter"]=input_context_list

        for outContext in output_context:
            output_context_list.append(outContext.outContext)

        if (len(output_context_list) > 0):
            intent_dict["context_set"] = output_context_list
        """End Context generation"""
        #print("####step1")

        intent_dict["tag"] = intent.name
        questions = Question.objects.filter(intent_id=intent.id)
        # add questions to dict
        if len(questions) == 0:
            message = "intent with id " + str(intent.id) + " has no questions to train."
            return message
        questions_list = []
        #print("####step2")
        for question in questions:
            questions_list.append(question.name)
        intent_dict["patterns"] = questions_list
        # verify type of response
        try:
            response_set = BlockResponse.objects.filter(intent_id=intent.id)
        except Exception as e:
            message = "intent with id " + intent.id + " has no answer." + e
            return message
        intent_dict["block_response"] = dict()
        # intent_dict["object"] = dict()
        # intent_dict["responses"] = dict()
        exist_fulfillment=False
        if intent.fulfillment is not None and intent.fulfillment.replace(" ","") !="":
            exist_fulfillment=True
            fulfillment=intent.fulfillment
            intent_dict["Fulfillment"] = dict()
            intent_dict["Fulfillment"]["code"] = fulfillment
            intent_dict["Fulfillment"]["entitys"] = []
            entitys = intent.related_entity.all()

            for entity in entitys:
                name=entity.entity.name
                modifyedName="$"+name
                intent_dict["Fulfillment"]["entitys"].append(modifyedName)
        if exist_fulfillment:
                intent_dict['block_response']['default'] = dict()
                intent_dict['block_response']['default']['object'] = []
                intent_dict['block_response']['default']['object'].append({"type": "simple", "value": {}})
                intent_dict['block_response']['default']['responses'] = []
                intent_dict['block_response']['default']['responses'].append(
                    "for fullfilment response _ generated automatically")

        else:
            for bc_response in response_set:
                intent_dict['block_response'][bc_response.category.lower()] = dict()
                intent_dict['block_response'][bc_response.category.lower()]["object"] = []
                intent_dict['block_response'][bc_response.category.lower()]["responses"] = []
                # print("###Here")
                if not bc_response.is_complex:
                    # simple response
                    # print("simple response")
                    simple_answers = SimpleResponse.objects.filter(block_response_id=bc_response.id)
                    random_texts = RandomText.objects.filter(simple_response__in=simple_answers)
                    random_texts_list = []
                    if len(random_texts) == 0:
                        message = "No simple responses to show to client."
                        return message
                    for text in random_texts:
                        random_texts_list.append(text.name)

                    intent_dict['block_response'][bc_response.category.lower()]["responses"] = random_texts_list
                    empty_object = dict()
                    empty_object['type'] = "simple"
                    empty_object['value'] = dict()
                    intent_dict['block_response'][bc_response.category.lower()]["object"].append(empty_object)
                    # intent_dict['block_response'][bc_response.category.lower()]["object"]

                else:
                    intent_dict['block_response'][bc_response.category.lower()]["responses"] = ['']

                    try:
                        complex_response_set = MixedResponse.objects.filter(block_response_id=bc_response.id)

                    except Exception as e:
                        message = "problem loading Mixed response: "
                        return message
                    # here
                    # for complex_response in complex_response_set:
                    #     intent_dict['object'][str(complex_response.category)] = []
                    # intent_dict['object']["man"] = []
                    # intent_dict['object']["woman"] = []
                    # intent_dict['object']["default"] = []
                    for complex_response in complex_response_set:
                        object = dict()
                        object["type"] = 'nested'
                        object['value'] = dict()
                        responses = []

                        try:

                            # text_responses = TextResponse.objects.filter(mixed_response_id=complex_response.id)
                            text_responses = complex_response.text_response_set.all()
                            # #print("___________________ intent=",intent.name)
                            # #print("___________________ complex=",complex_response.id)
                            # #print("___________________ txt_len=",len(text_responses))
                        except Exception as e:
                            message = "problem loading Mixed response: "
                            return message

                        text_responses_list = []
                        for text in text_responses:

                            text_dict = dict()
                            text_dict["type"] = "TextResponse"
                            text_dict["order"] = text.order
                            text_dict["value"] = dict()
                            buttons = Button.objects.filter(text_response_id=text).order_by("order")
                            # print("buttons for text_response: ", len(buttons))
                            if len(buttons) != 0:
                                text_dict["value"]["attachment"] = dict()
                                text_dict["value"]["attachment"]["type"] = "template"
                                text_dict["value"]["attachment"]["payload"] = dict()
                                text_dict["value"]["attachment"]["payload"]["template_type"] = "button"
                                text_dict["value"]["attachment"]["payload"]["text"] = text.name
                                text_dict["value"]["attachment"]["payload"]["buttons"] = []
                                for btn in buttons:
                                    if btn.url is not None:
                                        json_btn = dict()
                                        json_btn['type'] = 'web_url'
                                        json_btn['url'] = btn.url
                                        json_btn['title'] = btn.name
                                        json_btn['webview_height_ratio'] = "full"
                                        json_btn['messenger_extensions'] = btn.messenger_extensions
                                        text_dict["value"]["attachment"]["payload"]["buttons"].append(json_btn)
                                    elif btn.phone_number is not None:
                                        json_btn = dict()
                                        json_btn['type'] = 'phone_number'
                                        json_btn['payload'] = btn.phone_number
                                        json_btn['title'] = btn.name
                                        text_dict["value"]["attachment"]["payload"]["buttons"].append(json_btn)
                                    else:
                                        json_btn = dict()
                                        json_btn['type'] = 'postback'
                                        json_btn['payload'] = btn.payload
                                        json_btn['title'] = btn.name
                                        text_dict["value"]["attachment"]["payload"]["buttons"].append(json_btn)
                            else:
                                # print("This is a simple text without buttons")
                                text_dict["value"]["text"] = text.name
                            text_responses_list.append(text_dict)
                        responses += text_responses_list
                        # if complex_response.id in [229,230]:
                        #     print("___________________ intent=", intent.name)
                        #     print("___________________ complex=", complex_response.id)
                        #     print("___________________ text_responses_list=", text_responses_list)
                        #     print("___________________ responses=", responses)
                        # generate galleries
                        galleries = Gallery.objects.filter(mixed_response_id=complex_response.id)
                        galleries_list = []
                        for gallery in galleries:
                            gallery_dict = dict()
                            gallery_dict["type"] = "Gallery"
                            gallery_dict["order"] = gallery.order
                            gallery_dict["value"] = dict()
                            gallery_dict["value"]["attachment"] = dict()
                            gallery_dict["value"]["attachment"]["type"] = "template"
                            gallery_dict["value"]["attachment"]["payload"] = {}
                            gallery_dict["value"]["attachment"]["payload"]["template_type"] = "generic"
                            gallery_dict["value"]['attachment']['payload']['elements'] = []
                            # generate sliders of this specific gallery:
                            sliders = Slider.objects.filter(gallery_id=gallery.id).order_by("order")
                            for slider in sliders:
                                json_slider = dict()
                                json_slider['title'] = slider.title
                                try:
                                    if slider.image:
                                        json_slider['image_url'] = AGENT_IMAGES_URL + slider.image.url
                                except:
                                    # print("cannot load image url")
                                    pass
                                try:
                                    if slider.subtitle:
                                        json_slider['subtitle'] = slider.subtitle
                                except:
                                    pass
                                    # print("cannot card subtitle")
                                try:
                                    if slider.url:
                                        json_slider['default_action'] = {}
                                        json_slider['default_action']['type'] = 'web_url'
                                        json_slider['default_action']['url'] = slider.url
                                        json_slider['default_action']['webview_height_ratio'] = 'tall'

                                except:
                                    pass
                                    # print("cannot load card default action")
                                try:
                                    # print(slider.id)
                                    buttons = Button.objects.filter(slider_id=slider).order_by("order")
                                    # print("buttons ================================>", buttons)
                                    if len(buttons) != 0:
                                        json_slider['buttons'] = []
                                        for btn in buttons:
                                            if btn.url is not None:
                                                json_btn = dict()
                                                json_btn['type'] = 'web_url'
                                                json_btn['url'] = btn.url
                                                json_btn['title'] = btn.name
                                                json_btn['webview_height_ratio'] = "full"
                                                json_btn['messenger_extensions'] = btn.messenger_extensions
                                                json_slider['buttons'].append(json_btn)
                                            elif btn.phone_number is not None:
                                                json_btn = dict()
                                                json_btn['type'] = 'phone_number'
                                                json_btn['payload'] = btn.phone_number
                                                json_btn['title'] = btn.name
                                                json_slider['buttons'].append(json_btn)
                                            else:
                                                json_btn = dict()
                                                json_btn['type'] = 'postback'
                                                json_btn['payload'] = btn.payload
                                                json_btn['title'] = btn.name
                                                json_slider['buttons'].append(json_btn)
                                except:
                                    pass
                                    # print("no buttons to add to card")
                                gallery_dict["value"]['attachment']['payload']['elements'].append(json_slider)
                            galleries_list.append(gallery_dict)
                        responses += galleries_list
                        # generate quick replies
                        quick_replies = QuickReply.objects.filter(mixed_response_id=complex_response.id)
                        quick_replies_list = []
                        for reply in quick_replies:
                            qr_dict = dict()
                            qr_dict["type"] = "QuickReply"
                            qr_dict["order"] = reply.order
                            qr_dict["value"] = dict()
                            qr_dict["value"]["text"] = reply.name
                            qr_dict["value"]["quick_replies"] = []
                            qr_buttons = Button.objects.filter(quick_reply_id=reply.id).order_by('order')
                            for btn in qr_buttons:
                                qr_btn = dict()
                                qr_btn["content_type"] = "text"
                                qr_btn["title"] = btn.name
                                qr_btn["payload"] = btn.payload
                                qr_dict["value"]["quick_replies"].append(qr_btn)
                            quick_replies_list.append(qr_dict)
                        responses += quick_replies_list
                        # generate images
                        images = Image.objects.filter(mixed_response_id=complex_response.id)
                        images_list = []
                        for image in images:
                            image_dict = dict()
                            image_dict["type"] = "Image"
                            image_dict["order"] = image.order
                            image_dict["value"] = dict()
                            image_dict["value"]["attachment"] = dict()
                            image_dict["value"]["attachment"]["type"] = "image"
                            image_dict["value"]["attachment"]["payload"] = dict()
                            image_dict["value"]["attachment"]["payload"]["url"] = AGENT_IMAGES_URL + image.image.url
                            images_list.append(image_dict)
                        responses += images_list

                        # generate audio
                        audios = intent.related_audios.all()
                        audios_list = []
                        for audio in audios:
                            audio_dict = dict()
                            audio_dict["type"] = "Audio"
                            audio_dict["order"] = 1000
                            audio_dict["value"] = dict()
                            audio_dict["value"]["attachment"] = dict()
                            audio_dict["value"]["attachment"]["type"] = "audio"
                            audio_dict["value"]["attachment"]["payload"] = dict()
                            audio_dict["value"]["attachment"]["payload"]["url"] = AGENT_IMAGES_URL + audio.audio.audio.url
                            audios_list.append(audio_dict)
                        responses += audios_list

                        # generate videos
                        videos = intent.related_videos.all()
                        videos_list = []
                        for video in videos:
                            video_dict = dict()
                            video_dict["type"] = "Video"
                            video_dict["order"] = 1020
                            video_dict["value"] = dict()
                            video_dict["value"]["attachment"] = dict()
                            video_dict["value"]["attachment"]["type"] = "video"
                            video_dict["value"]["attachment"]["payload"] = dict()
                            video_dict["value"]["attachment"]["payload"]["url"] = AGENT_IMAGES_URL + video.video.video.url
                            videos_list.append(video_dict)
                        responses += videos_list

                        # sort responses by key :order
                        responses = sorted(responses, key=lambda i: i['order'])
                        # intent_dict['object']['value'] = dict()
                        counter = 1

                        for response in responses:
                            # types:  TextResponse, Gallery, QuickReply, Image
                            if response["type"] != "TextResponse":
                                object['value']["text" + str(counter)] = ""
                                object['value']["obj" + str(counter)] = response["value"]
                                counter += 1
                            else:
                                if "attachment" in response["value"]:
                                    # this is a text response with buttons
                                    object['value']["text" + str(counter)] = ""
                                    object['value']["obj" + str(counter)] = response["value"]
                                    counter += 1
                                else:
                                    object['value']["text" + str(counter)] = response["value"]["text"]
                                    object['value']["obj" + str(counter)] = dict()
                                    counter += 1

                        # print("object", object)
                        # intent_dict['object'][str(response.category)] = []
                        intent_dict['block_response'][bc_response.category.lower()]["object"].append(object)
                        # intent_dict['object']["woman"].append(object)
                        # intent_dict['object']["default"].append(object)

                    # intent_dict["object"]["type"] = 'nested'
                    # intent_dict['object']['value'] = dict()
                    #



        corepus['data'].append(intent_dict)


        """Genarate Entitys"""

        # generate videos
        entitys = intent.related_entity.all().order_by('id')
        #entitys.sort(key=Sort_Entity)
        if entitys.count()>0:
            intent_dict["entity"] = dict()
            entitys_list = []
            for entity in entitys:
                entity_dict = dict()
                lst=[]
                values =entity.entity.value_set.all()
                for value in values:
                    lst.append(value.value)
                    synonymes = [x.synonyme for x in value.synonyme_set.all()]
                    lst+=synonymes
                if entity.entity.is_default:
                    intent_dict["entity"]["{}".format(entity.entity.name)] = dict()
                    intent_dict["entity"]["{}".format(entity.entity.name)]['value'] = True
                    intent_dict["entity"]["{}".format(entity.entity.name)]['prompt'] = entity.prompt_response
                else:
                    intent_dict["entity"]["{}".format(entity.entity.name)] = dict()
                    intent_dict["entity"]["{}".format(entity.entity.name)]['value'] = lst
                    intent_dict["entity"]["{}".format(entity.entity.name)]['prompt'] = entity.prompt_response
            default_entity = intent.agent.agent.all().exclude(is_default=False)

            for defEntity in default_entity:
                relation_with_intent = defEntity.entity.all()
                if relation_with_intent.count()==0:
                    intent_dict["entity"]["{}".format(defEntity.name)] = dict()
                    intent_dict["entity"]["{}".format(defEntity.name)]['value'] = False
                    intent_dict["entity"]["{}".format(defEntity.name)]['prompt'] = ""
                else:
                    pass


        """End Genarating entitys"""

        """Generate the navigation intent params"""
        nav_list = intent.related_navigation.all()
        if nav_list:
            nav = nav_list[0]

            depending_intent = nav.related_depending.all()
            intent_dict["require"] = dict()
            intent_dict["require"]['nb_tentative'] = nav.nb_tentative
            intent_dict["require"]['redirection'] = nav.redirection.name
            intent_dict["require"]['echec'] = nav.echec.name
            intent_dict["require"]['depondant'] = []
            for dep in depending_intent:
                intent_dict["require"]['depondant'].append(dep.intent.name)

        """End Generating navigation intent params"""


    path = os.path.join(data_path, "folder_user_{}".format(user_id), "agent_{}".format(agent_id))
    if not os.path.exists(path):
        os.makedirs(path)
    with open(os.path.join(path, "non_response.json"), 'w', encoding='utf-8') as training_file:
        json.dump(corepus, training_file, ensure_ascii=False, indent=4)

    #print("####step5")

    path = os.path.join(data_path, "folder_user_{}".format(user_id), "agent_{}".format(agent_id))
    if not os.path.exists(path):
        os.makedirs(path)
    with open(os.path.join(path, "non_response.json"), 'w', encoding='utf-8') as training_file:
        json.dump(corepus, training_file, ensure_ascii=False, indent=4)
    # fileName = "data.json"+str(agent_id)+".json"
    #print("####step6")






    return os.path.join(path, "data.json")
    #return fileName
