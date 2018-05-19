# lustenauBot - webhook setup on heroku
 
 lustenauBot is a chatbot for the small austrian town "Lustenau". This is the associated webhook for some specific user requests.
 
 More info about Api.ai webhooks could be found here:
 [Api.ai Webhook](https://docs.api.ai/docs/webhook)
 
 # Deploy on Heroku:
 [![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)
 
 # What does it do?
 - weather information fulfillment service, using [Yahoo! Weather API](https://developer.yahoo.com/weather/).
 - building the url to give back a websearch as fallback return
 - providing information on the next departure times at the local bus stations
 
  # What is not yet done?
  - information on upcoming events in lustenau
  - smart and nice answers in webhook
  - first request does not get an answer

 The service packs the result in the Api.ai webhook-compatible response JSON and returns it to Api.ai.
