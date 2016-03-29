import os
from flask import Flask, request, Response
from twilio.util import TwilioCapability
import twilio.twiml

"""
Set the following contants if you do not intend to set environment variables.

Your AccountSid and AuthToken can be found in your Twilio Dashboard:
https://www.twilio.com/user/account/voice/dashboard

Create a TwiML Application and copy its AppSid:
https://www.twilio.com/user/account/voice/dev-tools/twiml-apps

Caller ID can be any Caller ID verified in your Twilio Account, or any Phone
Number you have purchased on your Twilio Account. It will be used for calls 
initiated from Twilio Client to PSTN phones:
https://www.twilio.com/user/account/phone-numbers/verified
https://www.twilio.com/user/account/voice/phone-numbers

"""

ACCOUNT_SID = 'ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
AUTH_TOKEN = 'YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY'
APP_SID = 'APZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ'
CALLER_ID = '+12345678901'

# This is the Client name that incoming calls from PSTN phones will be routed to
CLIENT = 'jenny'


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def welcome():
  """Returns a simple Welcome message using TwiML"""
  resp = twilio.twiml.Response()
  resp.say("Welcome to Twilio", voice="alice")
  return Response(str(resp), mimetype='application/xml')


@app.route('/token')
def token():
  """Returns a Twilio Capability token in plain text format. 

  There are two optional GET or POST parameters: 'allowOutgoing' and 'client'. 
  'allowOutgoing' is a string value that can be set to 'false' to prevent outgoing
  calls using this Capability Token. 'client' is the Twilio Client name that 
  will be used for incoming calls when registering with this Capability Token.
  """

  # Preference is given to the Twilio account configuration parameters set in
  # the local environment.
  account_sid = os.environ.get("ACCOUNT_SID", ACCOUNT_SID)
  auth_token = os.environ.get("AUTH_TOKEN", AUTH_TOKEN)
  app_sid = os.environ.get("APP_SID", APP_SID)

  capability = TwilioCapability(account_sid, auth_token)

  if request.values.get('allowOutgoing') != 'false':
     capability.allow_client_outgoing(app_sid)

  client = request.values.get('client')
  if client != None:
    capability.allow_client_incoming(client)

  return Response(str(capability.generate()), mimetype='text/plain')


@app.route('/call', methods=['GET', 'POST'])
def call():
  """Routes calls to and from Twilio Client instances and the PSTN.

  Important notes: 

  A [Twilio Client => Twilio Client] call is the easiest to identify because both
  "To" and "From" values will be Client names in the form "client:alice".

  A [Twilio Client => PSTN Phone] call will have a "From" value that is a Client 
  name and a "To" value that is a phone number.

  A [PSTN Phone => Twilio Client] call will have "To" and "From" values that are
  both phone numbers. This is because Twilio is describing the 'parent'(incoming)
  leg of the Call from a regular phone to a Twilio phone number.
  """

  caller_id = os.environ.get("CALLER_ID", CALLER_ID)
  from_param = request.values.get('From')
  to_param = request.values.get('To')

  resp = twilio.twiml.Response()

  if not (from_param and to_param):
    abort(400)

  caller_is_twilio_client = from_param.startswith('client:')
  recipient_is_twilio_client = to_param.startswith('client:')

  with resp.dial() as dial:
    if caller_is_twilio_client and recipient_is_twilio_client:
      # Twilio Client => Twilio Client
      dial.client(to_param[7:])
    elif caller_is_twilio_client:
      # Twilio Client => PSTN Phone (Caller ID must be a Phone Number)
      dial.attrs['callerId'] = CALLER_ID
      dial.number(to_param)
    else:
      # PSTN Phone => Twilio Client
      dial.client(CLIENT)

  return Response(str(resp), mimetype='application/xml')    


if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host='0.0.0.0', port=port, debug=True)
