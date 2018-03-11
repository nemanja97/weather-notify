#! py3
# notify.py - An SMS/email weather notifier, runs every hour

from twilio.rest import Client
from sys import argv
from pyowm.exceptions import api_call_error, api_response_error, not_found_error, unauthorized_error
from pyowm import OWM
import schedule
import time
import smtplib


# OPTIONS YOU NEED TO CHANGE:
# ------------------------------------------------
# TWILIO
accountSID  = None
authToken   = None
senderNum   = None
receiverNum = None
# OPENWEATHER
weather_api = None
# EMAIL
username    = None
password    = None
# ------------------------------------------------


def print_usage():
    print("-" * 50)
    print("USAGE:")
    print("notify -es -n place_name")
    print("notify -e -id place_id")
    print("notify -s -id place_id")
    print("-" * 50)
    print("EXAMPLES:")
    print('notify -es -n "Novi Sad, RS"')
    print('notify -e -n "Belgrade, RS"')
    print('notify -s -id 3194360')
    print('notify -es -id 3189595')


def parse_parameters():
    # Command line argument checker
    if len(argv) == 4:
        if argv[2] == "-n" or argv[2] == "-N":
            return argv[1], argv[2], argv[3]
        if argv[2] == "-id" or argv[2] == "-ID":
            try:
                return argv[1], argv[2], int(argv[3])
            except ValueError:
                print_usage()
                quit(1)
        else:
            print_usage()
            quit(1)
    else:
        print_usage()
        quit(1)


def setup_incomplete():
    # Displays a notifier upon incomplete setup
    print("Setup incomplete:")
    print("Make sure to set the values for API keys before starting.")
    quit(1)


def setup_check(sender_option):
    # Checks if you performed the setup correctly
    if sender_option == "-ES" or sender_option == "-es":
        try:
            assert accountSID  is not None
            assert authToken   is not None
            assert senderNum   is not None
            assert receiverNum is not None
            assert weather_api is not None
            assert username    is not None
            assert password    is not None
        except AssertionError:
            setup_incomplete()
    elif sender_option == "-S" or sender_option == "-s":
        try:
            assert accountSID  is not None
            assert authToken   is not None
            assert senderNum   is not None
            assert receiverNum is not None
            assert weather_api is not None
        except AssertionError:
            setup_incomplete()
    elif sender_option == "-E" or sender_option == "-e":
        try:
            assert weather_api is not None
            assert username    is not None
            assert password    is not None
        except AssertionError:
            setup_incomplete()
    else:
        print_usage()
        quit(1)


def get_observation_report(weather_client, search_option, search_term):
    # Tries to retrieve an observation report based on your search
    try:
        if search_option == "-n" or search_option == "-N":
            weather = weather_client.weather_at_place(search_term)
            return weather
        else:
            weather = weather_client.weather_at_id(search_term)
            return weather
    except unauthorized_error.UnauthorizedError:
        print("Invalid API key")
        quit(1)
    except not_found_error.NotFoundError:
        print("Unknown location")
        quit(1)
    except api_call_error.APICallError:
        print("Could not establish communication")
        quit(1)
    except api_response_error.APIResponseError:
        print("Could not get a response")
        quit(1)


def make_report(weather):
    # Makes a report of current weather
    report = {
        'time'     : weather.get_reference_time(timeformat='iso'),
        'status'   : weather.get_detailed_status(),
        'temp'     : weather.get_temperature(unit='celsius'),
        'clouds'   : weather.get_clouds(),
        'rain'     : weather.get_rain(),
        'snow'     : weather.get_snow(),
        'humidity' : weather.get_humidity(),
        'pressure' : weather.get_pressure(),
    }
    return report


def make_message(report):
    # Makes a string based message given the report
    time        = "\nTime: " + str(report['time']) + "\n"
    status      = "Status: " + str(report['status']) + "\n"
    temperature = "Temperature: " + str(report['temp']['temp']) + " C\n"
    clouds      = "Clouds: " + str(report['clouds']) + " %\n"
    humidity    = "Humidity: " + str(report['humidity']) + " %\n"
    pressure    = "Pressure: " + str(report['pressure']['press']) + " mbar\n"
    return time + status + temperature + clouds + humidity + pressure


def ready_smtp_server():
    # Readies up a SMTP server for connection
    try:
        smtp_obj = smtplib.SMTP('smtp.gmail.com', 587)
        smtp_obj.starttls()
        return smtp_obj
    except smtplib.SMTPConnectError:
        print("Not connected to the Internet")
        quit(1)


def login_account(smtp_obj):
    # Logins into the server with username / password combo
    try:
        smtp_obj.login(username, password)
    except smtplib.SMTPAuthenticationError:
        print("Could not log in")
        quit(1)


def send_mail(smtp_obj, content):
    # Sends a mail with a content representing a weather report
    try:
        smtp_obj.sendmail(username, username, content)
    except smtplib.SMTPRecipientsRefused:
        print("Error when sending")
        quit(1)


def run(sender_option, search_option, search_term):
    weather_client = OWM(weather_api)
    observation = get_observation_report(weather_client, search_option, search_term)
    report = make_report(observation.get_weather())
    message_body = make_message(report)

    if sender_option == "-ES" or sender_option == "-es" or sender_option == "-S" or sender_option == "-s":
        twilio_client = Client(accountSID, authToken)
        message = twilio_client.messages.create(to=receiverNum, from_=senderNum, body=message_body)
        print("Message sent >> SID : " + str(message.sid))

    if sender_option == "-ES" or sender_option == "-es" or sender_option == "-E" or sender_option == "-e":
        smtp_obj = ready_smtp_server()
        login_account(smtp_obj)
        send_mail(smtp_obj, message_body)
        print("Email sent\n")


if __name__ == "__main__":
    # Checks start parameters and setup
    sender_option, search_option, search_term = parse_parameters()
    setup_check(sender_option)

    # Schedule a task to run every hour
    schedule.every().minute.do(run, sender_option, search_option, search_term)
    while True:
        schedule.run_pending()
        time.sleep(1)
