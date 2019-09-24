import os
import json
import logging
import requests
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
                                                                                             
@app.route('/m2x-send-data', methods=['POST'])
def send_data():
    req_json = request.get_json()
    value = req_json["value"]
    device_id = req_json["device_id"]
    m2x_key = req_json["m2x_key"]
    try:
        value_in_kg = round(float(value)/1000, 2)
        url = f"http://api-m2x.att.com/v2/devices/{device_id}/streams/keg-weight/value"
        headers = {"X-M2X-KEY": m2x_key}
        json_data = {"value": value_in_kg}
        print(f"Keg weight is: {value_in_kg} kg")
        response = requests.put(url, headers=headers, json=json_data)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        return jsonify(response.json()), response.status_code
    return jsonify(result="Success"), 200

@app.route('/health')
def health_check():
    health = 'healthy'
    status = 'up'
    return jsonify(health=health, status=status), 200
                                                                                         
if __name__ == '__main__':
    logging.info(f'>>>>> Starting flask server at http://{host}:{port}')
    app.run(host=host, port=port, debug=True)
