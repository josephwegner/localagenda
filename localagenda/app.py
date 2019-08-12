import logging
import re
from flask import Flask, redirect, render_template, request, url_for, abort
from localagenda.cities import cities
from localagenda.models.subscription import Subscription
from localagenda.models.meeting import Meeting
from localagenda.models.city_request import CityRequest
from localagenda.mailer import send_subscription_notification
application = Flask(__name__)
log = application.logger

@application.route('/')
def home():
    return render_template('home.html', cities=cities)

@application.route('/about')
def about():
    return render_template('about.html')

@application.route('/cities')
def list_cities():
    active_cities = filter(lambda c: c.Subscribe, cities)
    return render_template('cities.html', cities=active_cities)

@application.route('/privacy')
def privacy():
    return render_template('privacy.html')

@application.route('/c', methods=['POST'])
def lookup_city():
    input = re.sub(r"[^A-Za-z,]", "", request.form['city'].lower())
    split = input.split(",")

    requested_state = ''
    if len(split) > 1:
        requested_state = split.pop()

    requested_city = ''.join(split)

    slug = "%s-%s" %(requested_city, requested_state)
    for city in cities:
        if city['slug'] == slug:
            return redirect(url_for('show_city', slug=slug))

    return redirect(url_for('request_city', slug=slug, full_name=request.form['city']))

@application.route('/c/<slug>', methods=['GET'])
def show_city(slug):
    chosen_city = None
    for city in cities:
        if city['slug'] == slug:
            chosen_city = city
            break

    if chosen_city == None:
        abort(404)

    return render_template('show.html', city=chosen_city, len=len)

@application.route('/r/<slug>', methods=['GET'])
def request_city(slug):
    name = request.args.get('full_name')
    if name == None:
        name = ', '.join(slug.split('-'))

    split = name.split(',')
    state = ''
    if len(split) > 1:
        state = split.pop()

    city = ','.join(split)

    return render_template('request.html', city=city, state=state)

@application.route('/request', methods=['POST'])
def submit_request():
    cr = CityRequest(city=request.form['city'], state=request.form['state'], email=request.form['email'])
    cr.save()

    return render_template('request_created.html', request=cr)

@application.route('/signup', methods=['POST'])
def signup():
    chosen_city = None
    for city in cities:
        if city['slug'] == request.form['slug']:
            chosen_city = city
            break

    if chosen_city == None:
        abort(404)

    user_subscriptions = (Subscription.select()
                          .join(Meeting)
                          .where(Subscription.email == request.form['email'],
                                 Meeting.city == chosen_city['Name']))

    user_meetings = list(map(sub_to_meeting, user_subscriptions))
    added_meetings = 0

    # Yes, this is O(n). Get off my back.
    for requested_meeting in request.form.getlist('meetings'):
        meeting_found = False
        for meeting in user_meetings:
            if meeting.name == requested_meeting:
                meeting_found = True
        if not meeting_found:
            db_meeting = Meeting.select().where(Meeting.name == requested_meeting,
                                                Meeting.city == chosen_city['Name']).get()
            sub = Subscription.create(email=request.form['email'], meeting=db_meeting)
            sub.save()

            user_meetings.append(db_meeting)
            added_meetings += 1

    if added_meetings > 0:
        send_subscription_notification(request.form['email'], chosen_city)

    return render_template('signed_up.html', meetings=user_meetings, city=chosen_city, len=len)

@application.template_filter('pluralize')
def pluralize(singular, multiple, int):
    if int != 1:
        return multiple
    else:
        return singular

def sub_to_meeting(subscription):
    return subscription.meeting
