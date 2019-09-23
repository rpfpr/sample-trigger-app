import os
import json
import logging
import smtplib

from email.message import EmailMessage
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
host = '0.0.0.0'
port = '8080'

CORS(app, origins=json.loads('["*"]'))
print(f'CORS allowed origins set to ["*"]')

@app.route('/m2x-trigger', methods=['POST'])
def m2x_trigger():
    req_json = request.get_json()
    print(f'{req_json}')
    logging.info(f'~~ {req_json} ~~')
    custom_data = json.loads(req_json["custom_data"])
    if req_json["event"] == "fired":
        message = f'M2X Trigger {req_json["trigger"]}: keg is running low on coffee. Uh oh! VALUES: [ '
    else:
        message = f'M2X Trigger {req_json["trigger"]}: keg has been filled up. Yay! VALUES: [ '
    count = 1
    num_values = len(req_json["values"])
    for stream in req_json["values"]:
        message += stream + ": " + str(req_json["values"][stream]["value"])
        message += " ]" if num_values == count else ", "
        count += 1
    msg = EmailMessage()
    msg.set_content(message)
    status = "running low" if req_json["event"] == "fired" else "re-filled"
    msg['Subject'] = f'M2X Trigger named {req_json["trigger"]}: {status}'
    msg['From'] = "coldbrew.keg.lifesaver@gmail.com"
    msg['To'] = custom_data["recipient"]
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.ehlo()
    s.login('coldbrew.keg.lifesaver@gmail.com', custom_data["password"])
    s.send_message(msg)
    s.close()
    return jsonify(result="Success"), 200
if __name__ == '__main__':
    logging.info(f'>>>>> Starting flask server at http://{host}:{port}')
    app.run(host=host, port=port, debug=True)
