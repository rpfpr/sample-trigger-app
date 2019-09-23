import os
import json
import logging
import smtplib
​
from email.message import EmailMessage
from flask import Flask, jsonify, request
from flask_cors import CORS
​
# Init flask app
app = Flask(__name__)
host = '0.0.0.0'
port = '8080'
​
# Setup API endpoints
CORS(app, origins=json.loads('["*"]'))
print(f'CORS allowed origins set to ["*"]')
​
# Init health endpoint
@app.route('/m2x-trigger', methods=['POST'])
def m2x_trigger():
    req_json = request.get_json()
    print(f'{req_json}')
    logging.info(f'~~ {req_json} ~~')
    body = req_json["body"]
    custom_data = req_json["body"]["custom_data"]
    if body["event"] == "fired":
        message = f'Conditions met for M2X Trigger named {body["trigger"]}. " VALUES: [ '
    else:
        message = f'M2X Trigger named {body["trigger"]} has been reset. " VALUES: [ '
​
    count = 1
    num_values = len(body["values"])
    for stream in body["values"]:
        message += stream + ": " + str(body["values"][stream]["value"])
        message += " ]" if num_values == count else ", "
        count += 1
​
    msg = EmailMessage()
    msg.set_content(message)
    msg['Subject'] = f'M2X Trigger named {body["trigger"]}'
    msg['From'] = "coldbrew.keg.lifesaver@gmail.com"
    msg['To'] = custom_data["recipient"]
​
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.ehlo()
    s.login('coldbrew.keg.lifesaver@gmail.com', custom_data["password"])
    s.send_message(msg)
    s.close()
​
    return jsonify(result="Success"), 200
​
if __name__ == '__main__':
    logging.info(f'>>>>> Starting flask server at http://{host}:{port}')
    app.run(host=host, port=port, debug=True)
