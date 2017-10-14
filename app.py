# test in shell: curl -i -H "Content-Type: application/json" -X POST -d '{"text":"Texto de prueba para ver que funciona", "language": "es"}' http://localhost:5000/generate_audio -o test.mp3
#  ! /usr/bin/env python3
# -*- coding: utf-8 -*-
from flask import Flask, request, send_file
import http.client, os
from lxml import etree

app = Flask(__name__)


def generate_audio(text="No hay texto", language='es', output_file="/tmp/temp_output.mp3"):
    # Selection of language and voice.
    # All options listed here:
    # https://docs.microsoft.com/en-us/azure/cognitive-services/speech/api-reference-rest/bingvoiceoutput
    if language == 'es':
        language_code = 'es-ES'  # es-ES, en-US, en-GB, ar-SA, ar-EG
        voice_code = 'HelenaRUS'
        gender = 'Female'  # Male or Female
    elif language == 'en':
        language_code = 'en-US'
        voice_code = 'ZiraRUS'
        gender = 'Female'  # Male or Female
    elif language == 'ar':
        language_code = 'ar-SA'  # TODO: Enter codes
        voice_code = 'Naayf'  # TODO: Enter codes
        gender = 'Male'  # Male or Female
    # API key stored in separate file: credentials.json
    # Note: The way to get API key:
    # Free: https://www.microsoft.com/cognitive-services/en-us/subscriptions?productId=/products/Bing.Speech.Preview
    # Paid: https://portal.azure.com/#create/Microsoft.CognitiveServices/apitype/Bing.Speech/pricingtier/S0
    # with open('credentials.json') as credentials:
    #     API_key = json.load(credentials)['apiKey']
    API_key = os.environ['API_KEY']
    params = ""
    headers = {"Ocp-Apim-Subscription-Key": API_key}

    # AccessTokenUri = "https://api.cognitive.microsoft.com/sts/v1.0/issueToken";
    AccessTokenHost = "api.cognitive.microsoft.com"
    path = "/sts/v1.0/issueToken"

    # Connect to server to get the Access Token
    print("Connect to server to get the Access Token")
    conn = http.client.HTTPSConnection(AccessTokenHost)
    conn.request("POST", path, params, headers)
    response = conn.getresponse()
    print(response.status, response.reason)

    data = response.read()
    conn.close()

    access_token = data.decode("UTF-8")
    print("Access Token: " + access_token)

    body = etree.Element('speak', version='1.0')
    body.set('{http://www.w3.org/XML/1998/namespace}lang', language_code)
    voice = etree.SubElement(body, 'voice')
    voice.set('{http://www.w3.org/XML/1998/namespace}lang', language_code)
    voice.set('{http://www.w3.org/XML/1998/namespace}gender', gender)
    voice.set('name', 'Microsoft Server Speech Text to Speech Voice (' + language_code + ', ' + voice_code + ')')

    # Divide input text into blocks that are under the limit of 1,024 characters
    text_blocks = []
    while len(text) > 600:
        begin = 0
        end = text.find(".", 600)
        if end == -1:
            end = text.find(" ", 600)
        text_block = text[begin:end]
        text = text[end:]
        text_blocks.append(text_block)
    text_blocks.append(text)

    headers = {"Content-type": "application/ssml+xml",
               "X-Microsoft-OutputFormat": "audio-16khz-128kbitrate-mono-mp3",
               "Authorization": "Bearer " + access_token,
               "X-Search-AppId": "07D3234E49CE426DAA29772419F436CA",
               "X-Search-ClientID": "1ECFAE91408841A480F00935DC390960",
               "User-Agent": "TTSForPython"}

    # Connect to server to synthesize the wave
    print("\nConnect to server to synthesize the wave")
    conn = http.client.HTTPSConnection("speech.platform.bing.com")
    with open(output_file, "wb") as f:
        for text_block in text_blocks:
            voice.text = text_block
            conn.request("POST", "/synthesize", etree.tostring(body), headers)
            response = conn.getresponse()
            print(response.status, response.reason)
            # Write response to .mp3 file
            f.write(response.read())
            print("The synthesized wave length: %d" % (len(data)))
    conn.close()
    return output_file


@app.route('/generate_audio', methods=['POST'])
def process_posted_input():
    if not request.json:
        abort(400)
    file_name = generate_audio(request.json['text'], request.json['language'])
    return send_file(file_name), 201


@app.route('/')
def home_page():
    return "This is the home page of the text-to-speech server"


if __name__ == '__main__':
    app.run()
