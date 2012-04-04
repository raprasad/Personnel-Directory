from xlwt import easyxf

style_header = easyxf('pattern: pattern solid, fore_colour light_yellow;align: wrap on;align:vert top; borders: top thin, bottom thin, right thin, left thin;')
style_header_gray = easyxf('pattern: pattern solid, fore_colour gray25;align: wrap on;align:vert top; borders: top thin, bottom thin, right thin, left thin;font: bold on;')
style_info_cell = easyxf('pattern: pattern solid, fore_colour white;align: wrap off;align:vert top; borders: top thin, bottom thin, right thin, left thin;')

style_info_cell_light_blue = easyxf('pattern: pattern solid, fore_colour pale_blue;align: wrap off;align:vert top; borders: top thin, bottom thin, right thin, left thin;')
style_info_cell_light_blue_wrap_on = easyxf('pattern: pattern solid, fore_colour pale_blue;align: wrap on;align:vert top; borders: top thin, bottom thin, right thin, left thin;')


style_info_cell_light_yellow = easyxf('pattern: pattern solid, fore_colour light_yellow;align: wrap off;align:vert top; borders: top thin, bottom thin, right thin, left thin;')
style_info_cell_light_yellow_wrap_on = easyxf('pattern: pattern solid, fore_colour light_yellow;align: wrap on;align:vert top; borders: top thin, bottom thin, right thin, left thin;')


style_info_cell_bold = easyxf('pattern: pattern solid, fore_colour white;align: wrap off;align:vert top; borders: top thin, bottom thin, right thin, left thin;font: bold on;font: height 240;')
style_info_cell_wrap_on = easyxf('pattern: pattern solid, fore_colour white;align: wrap on;align:vert top; borders: top thin, bottom thin, right thin, left thin;')


def fmt_domain(d):
    if d is None or not d.lower().endswith('.harvard.edu'):
        return d
    d = d.lower()
    username, domain_sec = d.split('@')
    domain_sec = domain_sec.replace('.harvard.edu', '')

    return '%s\%s' % (domain_sec, username)

def fmt_phone(phone):
    if phone is None or not len(phone)==12:
        return ''

    phone_parts = phone.split('-')
    if not len(phone_parts) == 3:
        return phone    

    return '(%s) %s-%s' % (phone_parts[0], phone_parts[1], phone_parts[2] )
      
def attr_len(attr):
    if attr is None:
        return 5
    try:
        return len(str(attr))
    except:
        return 5