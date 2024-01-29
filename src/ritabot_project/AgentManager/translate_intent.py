from AgentManager import models
from AgentManager import serializers
from AgentManager import clone_intent_serializers
from AgentManager import googleTranslateAPI
from rest_framework.exceptions import ValidationError
import os
import shutil


def translate(agent_id, intent_id, language, request):

    try:
        agent = models.Agent.objects.get(id=agent_id)
    except:
        raise Exception("Agent Not found.")
    try:
        intent = models.Intent.objects.get(id=intent_id)
    except:
        raise Exception("Intent Not found.")

    # define source_language
    if language == 'Francais':
        source_language = 'french'
    elif language == 'Anglais':
        source_language = 'en'
    elif language == 'Dialecte tunisien':
        # source_language = 'ar'
        return False
    elif language == 'Arabe':
        source_language = 'ar'
    else:
        return False

    # define target_language
    if agent.language == 'Francais':
        target_language = 'french'
    elif agent.language == 'Anglais':
        target_language = 'en'
    elif agent.language == 'Dialecte tunisien':
        # target_language = 'ar'
        return False
    elif agent.language == 'Arabe':
        target_language = 'ar'
    else:
        return False

    """ [START] collecting files(images/audios/videos) in a temporary folder """
    # TODO : collect images related to agents
    temp_files_folder = "TempFileFolder"
    path_to_files = os.path.join(temp_files_folder)

    if not os.path.exists(path_to_files):
        os.makedirs(path_to_files)
    else:
        shutil.rmtree(path_to_files)
        os.makedirs(path_to_files)

    images_path = os.path.join(path_to_files, 'images')
    # create images folder if it does not exist
    if not os.path.exists(images_path):
        os.makedirs(images_path)
    else:
        shutil.rmtree(images_path)
        os.makedirs(images_path)

    block_responses = models.BlockResponse.objects.filter(intent=intent, is_complex=True)
    if len(block_responses) > 0:
        mixed_responses = models.MixedResponse.objects.filter(block_response__in=block_responses)
        images_set = models.Image.objects.filter(mixed_response__in=mixed_responses)
        if len(images_set) > 0:
            for image in images_set:
                try:
                    image_name = os.path.join(images_path, '{}').format(image.imagename())
                    with open(image_name, 'wb') as actual_file:
                        actual_file.write(image.image.read())
                except:
                    pass
        """ filtering slider images """
        gallery_set = models.Gallery.objects.filter(mixed_response__in=mixed_responses)
        if len(gallery_set) > 0:
            slider_set = models.Slider.objects.filter(gallery__in=gallery_set)
            if len(slider_set) > 0:
                for slider in slider_set:
                    try:
                        image_name = os.path.join(images_path, '{}').format(slider.imagename())
                        with open(image_name, 'wb') as actual_file:
                            actual_file.write(slider.image.read())
                    except:
                        pass

    # todo : collect audio files
    audio_path = os.path.join(path_to_files, 'audios')
    # create audios folder if it does not exist
    if not os.path.exists(audio_path):
        os.makedirs(audio_path)
    else:
        shutil.rmtree(audio_path)
        os.makedirs(audio_path)

    audios = intent.related_audios.all()
    if len(audios) > 0:
        for audio in audios:
            try:
                audio_name = os.path.join(audio_path, '{}').format(audio.audio.audioname())
                with open(audio_name, 'wb') as actual_file:
                    actual_file.write(audio.audio.audio.read())
            except Exception as e:
                pass

    # todo : collect video files
    video_path = os.path.join(path_to_files, 'videos')
    # create videos folder if it does not exist
    if not os.path.exists(video_path):
        os.makedirs(video_path)
    else:
        shutil.rmtree(video_path)
        os.makedirs(video_path)

    videos = intent.related_videos.all()
    if len(videos) > 0:
        for video in videos:
            try:
                video_name = os.path.join(video_path, '{}').format(video.video.videoname())
                with open(video_name, 'wb') as actual_file:
                    actual_file.write(video.video.video.read())
            except Exception as e:
                pass

    """ [END] collecting files """

    intentSerializer = clone_intent_serializers.IntentManagerSerializer(intent)
    cloneIntent = intentSerializer.data.copy()

    # todo : instantiating google translate
    googleTranslate = googleTranslateAPI.GoogleTranslate()

    # TODO : translate intent name
    cloneIntent["name"] = googleTranslate.translate(cloneIntent["name"], source_language, target_language)

    # TODO : translate intent description
    if cloneIntent["description"] not in [None, ""]:
        cloneIntent["description"] = googleTranslate.translate(cloneIntent["description"], source_language, target_language)

    # TODO : translate questions
    for question in cloneIntent["question_set"]:
        question["name"] = googleTranslate.translate(question["name"], source_language, target_language)

    # TODO : translate In/Out context
    for output_context in cloneIntent["output_context_set"]:
        output_context["outContext"] = googleTranslate.translate(output_context["outContext"], source_language, target_language)

    for input_context in cloneIntent["input_context_set"]:
        input_context["Outname"] = googleTranslate.translate(input_context["Outname"], source_language, target_language)

    # TODO : translate entities
    for related_entity in cloneIntent["related_entityExportTranslate"]:
        related_entity["prompt_response"] = googleTranslate.translate(related_entity["prompt_response"], source_language, target_language)

        entity = related_entity["entity"]
        if not entity["is_default"]:
            # translate entity if it is not entity system
            entity["name"] = googleTranslate.translate(entity["name"], source_language, target_language)

        for value in entity["value_set"]:
            value["value"] = googleTranslate.translate(value["value"], source_language, target_language)
            for synonyme in value["synonyme_set"]:
                synonyme["synonyme"] = googleTranslate.translate(synonyme["synonyme"], source_language, target_language)

    # TODO : translate responses
    if cloneIntent["block_response_set"]:
        block_response = cloneIntent["block_response_set"][0]
        # TODO : translate simple response set
        if block_response["simple_response_set"]:
            simple_response = block_response["simple_response_set"][0]
            if "random_text_set" in simple_response:
                for random_text in simple_response["random_text_set"]:
                    random_text["name"] = googleTranslate.translate(random_text["name"], source_language, target_language)

        # TODO : translate mixed response set
        if block_response["mixed_response_set"]:
            mixed_response = block_response["mixed_response_set"][0]
            if "text_response_set" in mixed_response:
                for text_response in mixed_response["text_response_set"]:
                    text_response["name"] = googleTranslate.translate(text_response["name"], source_language, target_language)
                    if "button_set" in text_response:
                        for button in text_response["button_set"]:
                            button["name"] = googleTranslate.translate(button["name"], source_language,
                                                                            target_language)

                            button["payload"] = googleTranslate.translate(button["payload"], source_language,
                                                                            target_language)

            if "quick_reply_set" in mixed_response and mixed_response["quick_reply_set"]:
                for quick_reply in mixed_response["quick_reply_set"]:
                    quick_reply["name"] = googleTranslate.translate(quick_reply["name"], source_language,
                                                                            target_language)
                    if "button_set" in quick_reply:
                        for button in quick_reply["button_set"]:
                            button["name"] = googleTranslate.translate(button["name"], source_language,
                                                                            target_language)
                            button["payload"] = googleTranslate.translate(button["payload"], source_language,
                                                                            target_language)

            if "gallery_set" in mixed_response and mixed_response["gallery_set"]:
                for gallery in mixed_response["gallery_set"]:
                    if "slider_set" in gallery and gallery["slider_set"]:
                        for slider in gallery["slider_set"]:

                            slider["title"] = googleTranslate.translate(slider["title"], source_language,
                                                                            target_language)
                            slider["subtitle"] = googleTranslate.translate(slider["subtitle"], source_language,
                                                                            target_language)

                            # todo : convert image url to file
                            if "button_set" in slider:
                                for button in slider["button_set"]:
                                    button["name"] = googleTranslate.translate(button["name"], source_language,
                                                                               target_language)
                                    button["payload"] = googleTranslate.translate(button["payload"], source_language,
                                                                                  target_language)

    serializer = serializers.IntentManagerSerializer(data=cloneIntent, context={'agentid': agent_id,
                                                                                'path_to_user_folder': path_to_files,
                                                                                'request': request})
    if serializer.is_valid():
        serializer.create(cloneIntent)
        # todo : delete temporary file
        try:
            shutil.rmtree(path_to_files)
        except:
            pass

        return True
    else:
        raise ValidationError(serializer.error_messages)



