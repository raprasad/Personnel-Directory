"""
Working on the hu ldap / personnel db connection
"""
if __name__=='__main__':
    #-------------------------
    # import django settings
    #-------------------------
    import os, sys
    #pths = 
    sys.path.append('/var/webapps/django/MCB-Website/')
    sys.path.append('/var/webapps/django/MCB-Website/mcb_website')
    from django.core.management import setup_environ
    import settings
    setup_environ(settings)
else:
    import settings
    
from personnel_directory.common.msg_util import *
import ldap, sys, md5

from helper_classes import MemberInfo

# Please fill these in
#
CUSTOMER_NAME =  settings.LDAP_CUSTOMER_NAME #''   # username/id for binding to ldap server   
CUSTOMER_PW = settings.LDAP_CUSTOMER_PASSWORD  #'' # password for binding to ldap server   
LDAP_SERVER = settings.LDAP_SERVER

# Set LDAP options
ldap.set_option(ldap.OPT_REFERRALS, 0)  # turn off referrals
ldap.set_option (ldap.OPT_PROTOCOL_VERSION, ldap.VERSION3)  # version 3
ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)  # allow self-signed cert

class HUDirectorySearcher:
    """
    Grab an instance then use the 'find person' method.
    Searches by lname, fname, fname + lname, email, huid, etc, etc
    
    example:
        >searcher = HUDirectorySearcher()    # starts ldap connection
        >searcher.find_people(**kwargs)

        returns: None or [MemberInfo1, MemberInfo2, etc]
    """
    def __init__(self):
        
        self.AD_SEARCH_DN = "ou=people, o=Harvard University Core, dc=huid, dc=harvard, dc=edu";


        if settings.__dict__.get('LDAP_SERVER', False):
            self.ldap_url = settings.LDAP_SERVER  
        elif settings.DEBUG:
            self.ldap_url = 'ldaps://hu-ldap-test.harvard.edu'
        else:
            self.ldap_url = 'ldaps://hu-ldap.harvard.edu'
        self.ad_bind_usr = 'uid=%s, ou=applications,o=Harvard University Core,dc=huid,dc=harvard,dc=edu' % CUSTOMER_NAME
        self.ad_bind_pw = CUSTOMER_PW
    
        self.ldap_conn = self.get_ldap_connection()
        
    def close_connection(self):
        if self.ldap_conn is None:
            return None
            
        self.ldap_conn.unbind_s()
        
    def get_ldap_connection(self):
        
        msgt('(1) attempt to initialize url')        
        conn = ldap.initialize(self.ldap_url) 
        msg('url initialized')
        
        msgt('(2) attempt to bind to server with CUSTOMER_NAME = "%s"' % CUSTOMER_NAME )
        conn.simple_bind_s(self.ad_bind_usr, self.ad_bind_pw)
        msg('bind successful')
        
        return conn
        
        
    def find_people(self, **kwargs):

        # process **kwargs
        kw_ad_attrs_dict = { 'lname' : 'sn'
                            , 'fname' : 'givenName'
                            , 'email' : 'mail'
                            , 'huid' : 'harvardEduIDNumber'
                            , 'uid' : 'uid'
                            , 'role': 'eduPersonAffiliation'
                            }
        
        filter_pairs = []
        for kw, ad_kw in kw_ad_attrs_dict.iteritems():
            kwarg_val = kwargs.get(kw, None)
            if kwarg_val is not None:
                filter_pairs.append('(%s=%s)' % (ad_kw, kwarg_val))
        
        if len(filter_pairs) == 0:
            msgx('None of these keywords found in search filter: %s'  %  '\n - '.join(kw_ad_attrs_dict.keys()) )
        elif len(filter_pairs) == 1:
            search_filter = filter_pairs[0]
        else:
            search_filter = '(&%s)' % ''.join(filter_pairs)
        

        """Search the directory based on keyword info"""
        FIELDS_TO_RETURN = ['*']    # fields to return, '*': return everything
        #FIELDS_TO_RETURN = ['sn', 'givenName', 'title', 'mail']   # return last name, first name, title, and email

        # search the people section of HU Core
        AD_SEARCH_DN = "ou=people, o=Harvard University Core, dc=huid, dc=harvard, dc=edu";
        #search_filter = '(&(givenName=r*)(sn=smith))'
        msg('using filter: %s' % search_filter)
        try:
            results = self.ldap_conn.search_ext_s(self.AD_SEARCH_DN,ldap.SCOPE_SUBTREE, search_filter, FIELDS_TO_RETURN)  
        except UnicodeEncodeError:
            msg('ERROR: filter had UnicodeEncodeError')
            return None
        
        msg('search complete - raw results:')
        dashes()
        print results
        dashes()
        msg('formatted results')
        dashes()
        
        members = []
        for idx, r in enumerate(results):
            cn, lu = r      
            #msgt('(%s) %s' % (idx+1, cn))
            #print lu
            mi = MemberInfo(lu)     # convenience class from 'helper_classes.py'
            members.append(mi)
            #mi.show()
       
        if members == []:
            msg('>> no results from search')
            return None
        
        return members
        
        

if __name__=='__main__':
    if len(sys.argv) > 1:
        lu = {}
        for arg in sys.argv[1:]:
            if arg.find('=') > -1:
                kw, val = arg.split('=')
                lu.update({ kw:val})
    else:
        lu = { 'lname' : 'prasad'
                , 'fname': 'raman' }
    
    searcher = HUDirectorySearcher() 
    #kwarg = eval('lname="prasad"')
    members = searcher.find_people(**lu)
    if members is not None:
        for idx, mi in enumerate(members): print idx+1, mi.show(); dashes()
    searcher.close_connection()
    
#search_filter = '(&(givenName=r*)(sn=smith))'   
# examples of other filters
#search_filter = '(&(givenName=r*)(sn=smith)(c=USA))'    # Last name 'smith', first name starts with 'r', country is 'USA'
#search_filter = '(&(givenName=r*)(sn=smith)(c=USA)(mail=*harvard.edu))'   # Same as above, email ends with 'harvard.edu'
#search_filter = '(givenName=%s)' % 'Joe'   # Look for a specific first name
#search_filter = '(harvardEduIDNumber=%s)' % '11111111'    # Look for a specific harvard ID
#search_filter = '(uid=LNAMEa--THE-HASH--22a83f548376912fbd3d2)'  # Look for a specific UID

