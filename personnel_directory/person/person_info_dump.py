from person.models import Person, DeletedPerson
from django.template.loader import render_to_string

def get_person_text_info(person):
    """Used in pre-delete"""
    if person is None:
        return
    lu = { 'p' : person}    
    
    info_str =  render_to_string('person/info_dump.txt', lu)
    info_str = info_str.replace('\n\n', '\n').replace('\n\n', '\n').strip()
    return info_str
    
def save_deleted_person_info(sender, **kwargs):
    
    person = kwargs.get('instance', None)
    if person is None:
        return
        
    pinfo = get_person_text_info(person)
    
    dp = DeletedPerson(lname=person.lname
            , fname=person.fname
            , minitial=person.minitial
            , info=pinfo)
    dp.save()
    