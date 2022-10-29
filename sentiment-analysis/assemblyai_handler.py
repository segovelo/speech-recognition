#!/usr/bin/env python3
import requests
import time
import json
from dotenv import load_dotenv
import sys
import os

load_dotenv()

api_key = os.getenv('ASSEMBLYAI_API_KEY')

if len(sys.argv) > 1:
    filename = sys.argv[1]
else:
    filename = "data/output.wav"
upload_endpoint = 'https://api.assemblyai.com/v2/upload'
transcript_endpoint = 'https://api.assemblyai.com/v2/transcript'

headers_auth_only = {'authorization': api_key}

headers = {
    "authorization": api_key,
    "content-type": "application/json"
}

CHUNK_SIZE = 5_242_880  # 5MB


def upload(filename):
    def read_file(filename):
        with open(filename, 'rb') as f:
            while True:
                data = f.read(CHUNK_SIZE)
                if not data:
                    break
                yield data

    upload_response = requests.post(
        upload_endpoint, headers=headers_auth_only, data=read_file(filename))
    return upload_response.json()['upload_url']


def transcribe(audio_url, sentiment_analysis):
    transcript_request = {
        'audio_url': audio_url,
        'sentiment_analysis': sentiment_analysis
    }

    transcript_response = requests.post(
        transcript_endpoint, json=transcript_request, headers=headers)
    return transcript_response.json()['id']


def poll(transcript_id):
    polling_endpoint = transcript_endpoint + '/' + transcript_id
    polling_response = requests.get(polling_endpoint, headers=headers)
    return polling_response.json()


def get_transcription_result_url(url, sentiment_analysis=False):
    transcribe_id = transcribe(url, sentiment_analysis)
    while True:
        data = poll(transcribe_id)
        if data['status'] == 'completed':
            return data, None
        elif data['status'] == 'error':
            return data, data['error']

        print("waiting for 30 seconds... ⏳")
        time.sleep(30)


def save_transcript(url, filename, sentiment_analysis=False):
    data, error = get_transcription_result_url(url, sentiment_analysis)

    if data:
        text_filename = check_file(filename, "txt")
        with open(text_filename, 'w') as f:
            f.write(data['text'])
        if sentiment_analysis:
            sentiment_file = check_file(filename, "json")
            with open(sentiment_file, 'w') as f:
                sentiments = data['sentiment_analysis_results']
                json.dump(sentiments, f, indent=4)
        print('Transcript saved...  😊')
        return True
    elif error:
        print("Error!!! 🙁", error)
        return False


def check_file(file_name, ext):
    file_name = file_name.translate(
        {ord(i): None for i in '!#@{}[]<>=+£$%^&*()?|,;:\\\'\"'})
    index = file_name.find(".")
    if index > 0:
        file_name = file_name[0:index]
    elif index == 0:
        file_name = file_name[1:]
    return ".".join([file_name, ext])


#audio_url = upload(filename)

#save_transcript(audio_url, filename)
