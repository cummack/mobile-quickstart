# Twilio Client Mobile (iOS + Android) - Quickstart Tutorial Server

Find me at [https://github.com/twilio/mobile-quickstart](https://github.com/twilio/mobile-quickstart).

This repository includes a server-side web application that is required by Twilio Client mobile sample apps such as the Quickstart tutorial for [Android](https://www.twilio.com/docs/quickstart/php/android-client) and [iOS](https://www.twilio.com/docs/quickstart/php/ios-client). 

This small Python/[Flask](http://flask.pocoo.org) app is responsible for generating [Twilio Capability Tokens](https://www.twilio.com/docs/api/client/capability-tokens) in JWT format and for serving [TwiML](https://www.twilio.com/docs/api/twiml).

## Prerequisites

If you don't have one already, you'll need a [Twilio Account](https://www.twilio.com/try-twilio).

To deploy the app, you'll need your Twilio Account Sid and Auth Token, both available from your [Twilio Account Dashboard](https://www.twilio.com/user/account/). You will also need to create a [TwiML App](https://www.twilio.com/user/account/apps). 

You will also need a [verified phone number](https://www.twilio.com/user/account/phone-numbers/verified) to use as Caller ID.  Or you can use any [Twilio Phone Number](https://www.twilio.com/user/account/phone-numbers/incoming) that you've already purchased. 


## Deployment

So that Twilio can communicate with your web application, it needs to be accessible via the public Internet. Two of the simplest options for deployment are hosting the app on [Heroku](https://heroku.com/), or using [ngrok](https://ngrok.com/) to enable Twilio's servers to reach the web server on your development machine.

#### Option 1: Heroku
Use the Heroku Button below to automatically install the app into your Heroku account. You will need to enter your Twilio Account Sid, Auth Token, TwiML App Sid and verified phone number when prompted.

[![Deploy](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy)

#### Option 2: Local + Ngrok
If you prefer to run the application locally, make sure that you have `python` and `pip` installed, then install the required packages:

    pip install -r requirements.txt

Open `server.py` and replace the constants `ACCOUNT_SID`, `AUTH_TOKEN`, `APP_SID` and `CALLER_ID` with the relevant values from your Twilio account. 

Run the application using:

	python server.py  

Then, use `ngrok` to open up Internet access to your server: 

    ngrok http 5000

#### Option 3: Anywhere Else!
This repository constitutes a standard python application utilizing the Flask micro-framework. Feel free to deploy it to any host where it can be reached by Twilio's servers via the Internet. 

#### Final Steps
Lastly, configure your TwiML App's Voice Request URL to point at your newly deployed web application's `/call` URL. e.g.: `http://babbling-bobby-1432.herokuapp.com/call`.

## Testing

run `python server_tests.py` at your terminal, or experiment manually at `http://localhost:5000/token` and `http://localhost:5000/call?To=client:bob&From=client:alice`, etc. 


## Client App Configuration

You will need to modify the Twilio Client sample applications to point at the `/token` URL of your web server in order to fetch a Capability Token. Details are included in the application tutorials on Twilio's website.
