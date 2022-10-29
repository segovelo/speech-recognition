import requests
import sys
from assemblyai_handler import *

if len(sys.argv) > 1:
    filename = sys.argv[1]
else:
    filename = "data/output.wav"

audio_url = upload(filename)

save_transcript(audio_url, filename)
