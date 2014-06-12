from django.http import HttpResponse
from django.template.defaultfilters import slugify, escapejs
from django.template.loader import render_to_string

MCB_SERVERS = { 
        #, '140.247.111.70' : 'www.mcb.university.edu' \
        #, '127.0.0.1' : 'local machine (for testing)' \
}        

SERVERS_ALLOWED_TO_MAKE_JSON_CALL = MCB_SERVERS.keys()

def get_http_err(msg):
    return HttpResponse('Error: %s' % msg)


def get_json_str_add_user_via_email(email, success, msg_for_user):
    """ Return a JSON object with 'email', 'success', and 'msg' attributes """

    if success:
        success_str = 'true'
    else:
        success_str = 'false'
    
    json_str = """{ "email" : "%s", "success": %s, "msg" : "%s" }""" % (escapejs(email), success_str, msg_for_user.replace('"',''))

    return json_str


def get_json_str(success, msg_for_user, lu_vals={}):
    """ Return a JSON object with 'success', and 'msg' attributes """

    if success:
        success_str = 'true'
    else:
        success_str = 'false'
    
    lu_str = ''
    if len(lu_vals) > 0:
        for (k,v) in lu_vals.items():
            k = k.replace('"', '\"').replace('\'', '\'')
            v = v.replace('"', '\"').replace('\'', '\'')
            lu_str += ' , "%s": "%s" ' % (k, v)
    
    json_str = """{ "success": %s,
              "msg" : "%s"  %s }""" % (success_str, msg_for_user.replace('"',''), lu_str)

    return json_str
    
def get_json_str_as_http_response2(request, success, msg, json_str='', callback=None):
    """ Return a JSON object with the HTTP Response """

    if success:
         success_str = 'true'
    else:
         success_str = 'false'

    json_str = """{ "success": %s,
               "msg" : "%s"  %s }""" % (success_str, msg.replace('"',''), json_str)

    if callback is not None:
        json_str = '%s(%s)' % (callback, json_str)

    return HttpResponse(json_str)
    
def get_json_str_as_http_response(request, success, msg, lu_vals={}):
    """ Return a JSON object with the HTTP Response """

    return HttpResponse(get_json_str(success, msg, lu_vals))    


def render_to_string_remove_spaces(template_name, lookup={}):
    if template_name is None or lookup is None:
        return None

    rendered_str = render_to_string(template_name, lookup)
    return rendered_str.replace('\n', ' ').replace('\t', ' ')

