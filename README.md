# fritzbox-thermostat-triggers

This app allows to define and toggle triggers that
- a) set a thermostat to a specified temperature at a specific date and time **once**, or:
- b) set a thermostat to a specified temperature at a specific time, **on each week day specified**

---

<div>
  <img src="https://i.imgur.com/pltsrhx.png" width="400" title="Light theme" style="margin-right: 24px">
  <img src="https://i.imgur.com/jhln2Rq.png" width="400" title="Light theme">
</div>

## Rationale

A utility web app to allow **more options to control** any Fritz! compatible thermostats
like [FRITZ!DECT 301](https://avm.de/produkte/smart-home/fritzdect-301/) or [COMECT DECT](https://eurotronic.org/produkte/dect-ule-heizkoerperthermostat/comet-dect/).

The ecosystem comes with a decent mobile app to control the thermostats in general, you can also use the http://fritz.box Smart Home Web UI to define times in which you want to use one between two possible temperatures. This is all fine, but the Web UI for setting the timing isn't quite mobile friendly and doesn't exactly match all use cases I had, which included:

- Turning off thermostats at night **in case I forgot** to do that myself (I was using cronjobs fo this, which lack an interface and can't quickly be changed from my smartphone)
- Turning on thermostats at predefined times as a **one-off exception**, e.g. heat up the office tomorrow morning, as I'll be working remotely
- I also wanted an interface allowing to change these things as quickly as possible, aka switching on a disabled non-weekly trigger will change its date to either today or tomorrow, whatever makes more sense
- The triggers can give optional feedback via the [Pushover](https://pushover.net/) mobile client.

## Technology used

- [pyfritzhome](https://github.com/hthiery/python-fritzhome)
- [Django](https://www.djangoproject.com/), [htmx](https://htmx.org/)
- [pico.css](https://picocss.com/) :heart:

## Setup

### Development

- Make sure your thermostats are connected to/known by your Fritzbox
- Prepare a Fritz user as described [here](https://github.com/hthiery/python-fritzhome#fritzbox-user)
- Make sure you have Python 3.8+ installed
- Prepare a virtualenv like: `python -m venv venv`
- Install dependencies like: `(venv) pip install -r requirements.txt`
- Initialize the database: `(venv) python manage.py migrate`
- Configure variables for `python-decouple` in a `settings.ini` (or `.env`), see `settings.ini.example`
- Sync the list of thermostats to the app: `(venv) python manage.py sync_and_trigger_thermostats --sync-only`
- Run the app: `(venv) python manage.py runserver`
- Login, logout and most of the CRUD stuff is just done via the Django admin, so make sure to create an admin user: `(venv) python manage.py createsuperuser`
- Visit the interface at http://localhost:8000 then use the Django admin to create your triggers, click "View Site" within the admin pages to go back to the main UI screen.

### Production

- You want to setup the management command (`sync_and_trigger_thermostats`)  as a cronjob to run e.g. every minute
- You probably want `gunicorn` or something similar to run the Django app
- Staticfiles are hosted using whitenoise, so no webserver required for that

