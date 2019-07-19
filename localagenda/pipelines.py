from localagenda.models.meeting import Meeting
from localagenda.models.subscription import Subscription
from localagenda.models.agenda import Agenda
from localagenda.mailer import send_agenda, send_verification
import hashlib
from datetime import date

class AgendaPipeline(object):
    def process_item(self, item, spider):
        content_hash = hashlib.md5(item['content'].encode('utf-8')).hexdigest()
        meeting = Meeting.get(Meeting.name == item['meeting'], Meeting.city == item['city'])

        send_to = []
        for sub in meeting.subscriptions:
            send_to.append(sub.email)

        if len(send_to) == 0:
            print("No subscriptions for %s %s" %(meeting.city, meeting.name))
            return


        if content_hash != meeting.latest_agenda_hash:
            meeting.latest_agenda_hash = content_hash
            meeting.save()

            agenda = Agenda.create(content_hash=content_hash,
                                   content=item['content'],
                                   target=item['target'],
                                   captured_date=date.today(),
                                   meeting=meeting)
            agenda.save

            if len(meeting.agendas) == 1:
                send_verification(agenda)
            else:
                send_agenda(send_to, agenda)

        return item
