from gspread import Client as GSpreadClient
import requests
import json
import openai
from oauth2client.service_account import ServiceAccountCredentials
# from dotenv import load_dotenv 
# load_dotenv()
def write_expense_to_spreadsheet(Product_Codes, Price, Client, Client_Code, Orders, Total):
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('filename', scope)
    gspread_client = GSpreadClient(creds)
    spreadsheet_id = ""
    sheet = gspread_client.open_by_key(spreadsheet_id).sheet1
    sheet.append_row([Product_Codes, Price, Client, Client_Code, Orders, Total])

WEBHOOK_URL = ""
def post_message_to_slack_via_webhook(message):
    payload = {'text': message}

    response = requests.post(
        WEBHOOK_URL, data=json.dumps(payload),
        headers={'Content-Type': 'application/json'}
    )

    if response.ok:
        print('Message sent successfully')
    else:
        print('Failed to send message. Error:', response.text)

openai.api_key = "OPENAI_API"
def run_conversation():

    user_input=input("user_input:")
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=[
                {"role": "system", "content": "You are the best assistant ever!"},
                {"role": "user", "content": user_input}],
            functions=[
                {
                    "name": "write_expense_to_spreadsheet",
                    "description": "Cosmetics Inc.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "Product Codes": {"type": "number"},
                            "Price": {"type": "number"},
                            "Client": {"type": "number"},
                            "Client Code": {"type": "string"},
                            "Orders" : {"type": "number"},
                            "Total" : {"type": "number"},
                        },
                        "required": ["Product Codes", "Price", "Client", "Client Code", "Orders", "Total"],
                    },
                },
                {
                    "name": "post_message_to_slack_via_webhook",
                    "description": "Post a message to Slack",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "message": {"type": "string"},
                        },
                        "required": ["message"],
                    },
                }
            ],

            function_call="auto",
        )
        message = response["choices"][0]["message"]
    except Exception as Error:
        print('here text :',Error)

    if message.get("function_call"):
        function_name = message["function_call"]["name"]
        arguments = json.loads(message["function_call"]["arguments"])
        # print(arguments)
        print(message["function_call"]["arguments"])
        if function_name == "write_expense_to_spreadsheet":
            function_response = write_expense_to_spreadsheet(
                Product_Codes=arguments.get("Product Codes"),
                Price=arguments.get("Price"),
                Client=arguments.get("Client"),
                Client_Code=arguments.get("Client Code"),
                Orders=arguments.get("Orders"),
                Total=arguments.get("Total")
            )
        elif function_name == "post_message_to_slack_via_webhook":
            function_response = post_message_to_slack_via_webhook(
                message=arguments.get("message"),
            )
        else:
            raise NotImplementedError()
        
        second_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
             # get user input
             
            messages=[
                {"role": "user", "content": user_input},
                message,
                {
                    "role": "function",
                    "name": function_name,
                    "content": str(function_response),
                },
            ],
        )
        return second_response
    else:
        return response

print("response:", run_conversation()["choices"][0]["message"]["content"], "\n\n")
