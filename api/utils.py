import re
from pytube import YouTube
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi
from openai import OpenAI
from dotenv import load_dotenv
import json
import requests
from bs4 import BeautifulSoup, Comment
from exceptions import CustomError
load_dotenv()
api_key = "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"
client = OpenAI(api_key=api_key)



system_message_indepth_lecture_video_incomplete = """
e costruisci una lezione approfondita di 9-10 paragrafi contenenti 1000 parole ciascuno, basata sulla trascrizione del video di YouTube fornita.
Assicurati di creare un piano di lezione lungo e completo, composto da almeno 4000 a 8000 parole.
Puoi andare con 7-8 paragrafi per questa lezione.
Genera sempre la tua risposta in italiano. Rispondi nel seguente formato JSON:
{
"in_depth_lecture": "La lezione approfondita va qui"
}
"""

system_message_indepth_lecture_website_incomplete = """
e costruisci una lezione approfondita di 9-10 paragrafi contenenti 1000 parole ciascuno, basata sul contenuto estratto da un sito web.
Assicurati di creare un piano di lezione lungo e completo, composto da almeno 4000 a 8000 parole.
Puoi andare con 7-8 paragrafi per questa lezione.
Genera sempre la tua risposta in italiano.
Rispondi nel seguente formato JSON:
{
"in_depth_lecture": "La lezione approfondita va qui"
}
"""

system_message_video_incomplete = """
e crea un piano di lezione di 9-10 paragrafi contenenti 1000 parole ciascuno, basato sulla trascrizione del video di YouTube fornita.
Genera sempre la tua risposta in italiano.
Il piano di lezione deve avere sei sezioni:
1- Schemi per comprendere il contenuto.
2- Un semplice quiz a risposta multipla di 25 domande dal piano di lezione (25 domande).
3- Consigli su possibili attività educative da svolgere.

Rispondi nel seguente formato JSON:
{
"outlines": "The outlines go here",
"mcqs": [
{
"question": <la domanda va qui>,
"correctAnswer": <la risposta corretta va qui>,
"options":[
elenco delle opzioni
]
}
]
activities": "Le attività vanno qui, separa anche ciascuna attività con una nuova riga",
}
"""

system_message_website_incomplete = """
e crea un piano di lezione di 9-10 paragrafi contenenti 1000 parole ciascuno, basato sul contenuto estratto da un sito web.
Genera sempre la tua risposta in italiano.
Il piano di lezione deve avere sei sezioni:
1- Schemi per comprendere il contenuto.
2- Un semplice quiz a risposta multipla di 25 domande dal piano di lezione (25 domande).
3- Consigli su possibili attività educative da svolgere.

Rispondi nel seguente formato JSON:
{
"outlines": "The outlines go here",
"mcqs": [
{
"question": <la domanda va qui>,
"correctAnswer": <la risposta corretta va qui>,
"options":[
elenco delle opzioni
]
}
]
activities": "Le attività vanno qui, separa anche ciascuna attività con una nuova riga",

}
"""





# 5- Generate a prompt for Dall E 3 which should be relevant to the content of the website.
# "dall_e_3_prompt": "The prompt for Dall E 3 goes here"
def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

def add_line_breaks(text):
    patterns = [
        r'(?<=[a-z])\n(?=[A-Z])',  
        r'(?<=\.)\s(?=[A-Z])',
        r'(?<=\d)\n(?=[A-Z])',
        r'(?<=\”)\s(?=[A-Z])',  
        r'\n\n',
    ]

    for pattern in patterns:
        text = re.sub(pattern, "\n", text)

    if text:
        return text
    else:
        return ""

def dynamic_scraper(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    texts = soup.findAll(string=True)
    visible_texts = filter(tag_visible, texts)
    text_content = u" ".join(t.strip() for t in visible_texts)
    text_with_breaks = add_line_breaks(text_content)
    if len(text_with_breaks) > 8000:
        text_with_breaks = text_with_breaks[0:10000]
    return text_with_breaks



def get_video_transcript(youtube_url):
    try:
        # Parse the YouTube video URL to extract the video ID
        url_data = urlparse(youtube_url)
        query = parse_qs(url_data.query)
        video_id = query['v'][0]
        
        # Fetch transcript in Italian language ('it')
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['it'])

        # Extract text from transcript
        transcript_text = ' '.join([item['text'] for item in transcript_list])
        
        # Print and return the transcript text
        print("Transcript Text: ", transcript_text)
        if len(transcript_text) > 8000:
            transcript_text = transcript_text[:8000]  # Limit the transcript text to 8000 characters
        print(len(transcript_text))
        return transcript_text

    except Exception as e:
        raise CustomError(
            "Sorry, the Transcript for this video is not available. Please provide another YouTube video URL.")



# def get_video_transcript(youtube_url):
#     try:
#         url_data = urlparse(youtube_url)
#         query = parse_qs(url_data.query)
#         print(query)
#         video_id = query["v"][0]
#         # get the available transcripts
#         available_transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
        
#         print("Available Transcripts: ", available_transcripts)
#         # try to fetch the italian one
#         transcript = available_transcripts.find_transcript(['es'])
#         print("Transcript: ", transcript)


#         transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['es'])
        
#         print("Transcript List: ", transcript_list)
#         transcript_text = ' '.join([item['text'] for item in transcript_list])
#         print("Transcript Text: ", transcript_text)
#         if len(transcript_text) > 8000:
#             transcript_text = transcript_text[0:10000]
#         print(len(transcript_text))
#         return transcript_text
#     except Exception as e:
#         raise CustomError(
#             "Sorry, the Transcript for this video is not available. Please provide another YouTube video URL.")

    

def get_response_video(system_message_video, transcript):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_message_video},
            {"role": "user", "content": "Transcript: " + transcript},
        ],
        response_format={"type": "json_object"},
    )
    json_format = json.loads(response.choices[0].message.content)
    return json_format


def get_response_website(system_message_website, url):
    try:
        text = dynamic_scraper(url)
        print("Scraped Text: ")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_message_website},
                {"role": "user", "content": "Scraped Text: " + text},
            ],
            response_format={"type": "json_object"},
        )
        print("Response: ")
        json_format = json.loads(response.choices[0].message.content)
        print("JSON Format: ")
        return json_format
    except Exception as e:
        print(e)
        raise CustomError("Sorry, the website is not available. Please provide a valid website URL.")

def get_indepth_lecture_video(system_message, transcript):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": "Transcript: " + transcript},
        ],
        response_format={"type": "json_object"},
    )
    json_format = json.loads(response.choices[0].message.content)
    return json_format

def get_indepth_lecture_website(system_message, url):
    text = dynamic_scraper(url)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": "Scraped Text: " + text},
        ],
        response_format={"type": "json_object"},
    )
    json_format = json.loads(response.choices[0].message.content)
    return json_format

def url_validation(url):
    try:
        if "youtu.be" in url:
            m = re.search(r'youtu.be\/([a-zA-Z0-9_-]+)', url)
            if m:
                video_id = m.group(1)
                url = f'https://www.youtube.com/watch?v={video_id}&feature=youtu.be'
                return {"url": "youtube", "video_url": url}

        elif "youtube.com" in url:
            return {"url": "youtube", "video_url": url}
        else:
            return {"url": "website", "website_url": url}
    except Exception as e:
        raise CustomError("Sorry, the video is not available. Please provide a valid YouTube video URL.")
    
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'
