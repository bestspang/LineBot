from google.oauth2 import service_account
import os

os.environ["DIALOGFLOW_PROJECT_ID"]="bplinebot"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="/System/Volumes/Data/Users/bestspang/Developer/Projects/linebot/LineBot/BPLINEBOT-0106b42afbf3.json"

def detect_intent_texts(project_id, session_id, text, language_code):
    import dialogflow_v2 as dialogflow
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)

    if text:
        text_input = dialogflow.types.TextInput(
            text=text, language_code=language_code)
        query_input = dialogflow.types.QueryInput(text=text_input)
        response = session_client.detect_intent(
            session=session, query_input=query_input)

        return response.query_result.fulfillment_text

project_id = 'bplinebot'
message = 'สวัสดี'
fulfillment_text = detect_intent_texts(project_id, "unique", message, 'th')

print(fulfillment_text)
