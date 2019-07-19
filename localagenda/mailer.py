import os
import sys
import logging
from jinja2 import Environment, PackageLoader, select_autoescape
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger(__name__)

env = Environment(
    loader=PackageLoader('localagenda', 'templates'),
    autoescape=select_autoescape(['html', 'xml'])
)

def send_agenda(to, agenda):
    template = env.get_template('agenda.txt')
    content = template.render(agenda=agenda)
    subject = "%s %s Agenda" %(agenda.meeting.city, agenda.meeting.name)

    send(to, subject, content)

def send_verification(agenda):
    template = env.get_template('verification.txt')
    content = template.render(agenda=agenda)
    subject = "Verify new agenda for %s %s" %(agenda.meeting.city, agenda.meeting.name)

    send(os.environ.get('VERIFY_EMAIL'), subject, content)

def send_subscription_notification(to, city):
    template = env.get_template('subscription.txt')
    content = template.render(city=city)
    subject = "Subscribed to agendas for %s" %(city['Name'])

    send(to, subject, content)

def send(to, subject, content):
    if os.environ.get('environment') == 'production':
        send_via_sendgrid(to, subject, content)
    else:
        send_locally(to, subject, content)

def send_locally(to, subject, content):
    log.debug('Local email.... just outputting to terminal')
    log.debug("To: %s" %(to))
    log.debug("From: %s" %(os.environ["EMAIL_FROM"]))
    log.debug("Subject: %s" %(subject))
    log.debug('')
    log.debug('Body:')
    log.debug(content)

def send_via_sendgrid(to, subject, content):
    log.debug('sending to...')
    log.debug(to)
    message = Mail(
        from_email=os.environ['EMAIL_FROM'],
        to_emails=to,
        subject=subject,
        plain_text_content=content,
        is_multiple=(isinstance(to, list)))

    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        log.debug("Sendgrid status %s" %(response.status_code))
    except Exception as e:
        print(str(e))
