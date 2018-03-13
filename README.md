<h1 align="center">weather-notify</h1>

<p>An SMS / email notifier sending information about changing weather patterns. Integrates with OpenWeatherMap and Twilio API and requires their keys for proper use.</p>

<h3> Requirements </h3>

- [twilio](https://pypi.python.org/pypi/twilio)
- [pyowm](https://pypi.python.org/pypi/pyowm/2.8.0)
- [schedule](https://pypi.python.org/pypi/schedule/0.5.0)

<h3> Setup </h3>

<p>Before starting up the application, please edit the lines concerning the API keys, usernames, passwords and phone numbers at the beginning of the file. Check the keys on Twilio and OpenWeatherMap websites. The default SMTP value is the one for GMail accounts, but all possible values are: </p>

- Gmail: smtp.gmail.com
- Outlook: smtp-mail.outlook.com
- Yahoo: smtp.mail.yahoo.com
- AT&T: smpt.mail.att.net (port 465)
- Comcast: smtp.comcast.net
- Verizon: smtp.verizon.net (port 465)

<p>Bear in mind that if you are using a GMail account, your username remains the same but your password does NOT! Set up the password by following these intstructions: https://support.google.com/accounts/answer/185833?hl=en </p>
