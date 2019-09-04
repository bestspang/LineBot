from google.oauth2 import service_account
import os

os.environ["DIALOGFLOW_PROJECT_ID"]="bplinebot"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="/System/Volumes/Data/Users/bestspang/Developer/Projects/linebot/LineBot/BPLINEBOT-0106b42afbf3.json"

def detect_intent_texts(project_id, session_id, texts, language_code):
    """Returns the result of detect intent with texts as inputs.

    Using the same `session_id` between requests allows continuation
    of the conversation."""

    import dialogflow_v2 as dialogflow
    session_client = dialogflow.SessionsClient()

    session = session_client.session_path(project_id, session_id)
    print('Session path: {}\n'.format(session))

    for text in texts:
        text_input = dialogflow.types.TextInput(
            text=text, language_code=language_code)

        query_input = dialogflow.types.QueryInput(text=text_input)

        response = session_client.detect_intent(
            session=session, query_input=query_input)

        print('=' * 20)
        print('Query text: {}'.format(response.query_result.query_text))
        print('Detected intent: {} (confidence: {})\n'.format(
            response.query_result.intent.display_name,
            response.query_result.intent_detection_confidence))
        print('Fulfillment text: {}\n'.format(
            response.query_result.fulfillment_text))

project_id = 'bplinebot'
message = 'สวัสดี'
fulfillment_text = detect_intent_texts(project_id, "unique", message, 'th')

print(fulfillment_text)
