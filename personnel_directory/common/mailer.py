#from personnel_directory.common.time_util import *
from personnel_directory.common.msg_util import *
from django.core.mail import EmailMultiAlternatives, SMTPConnection
from django.conf.settings import ADMINS


def get_admin_email_addresses():
    """Return the 1st admin email address from the settings file
    Example of format:
     ADMINS = (\
         ('Raman Prasad', 'rprasad@cgr.harvard.edu'),\
    )
    """
    if ADMINS is None: return None
    
    try:        
        return map(lambda x: x[1], ADMINS)
    except: 
        return None
    
def send_message(from_email, to_addresses=[], subject='subject', text_content='', html_content=''):

    msgt('preparing to send message')
    #smtp_conn = SMTPConnection('smtp.lsdiv.harvard.edu') 
    #smtp_conn = SMTPConnection('shaggy.nucleus.harvard.edu') 
    msg('server conn created')    
    multipart_msg = EmailMultiAlternatives(subject, text_content, from_email, to_addresses)#, connection=smtp_conn)
    multipart_msg.attach_alternative(html_content, "text/html")
    multipart_msg.send()
    msg('email sent')

'''
from mcb_event_forms.models import *
from mcb_event_forms.views_bakesale import *
l = BakeSaleDonorRegistration.objects.all()[0]
send_bakesale_confirmation(l)

'''