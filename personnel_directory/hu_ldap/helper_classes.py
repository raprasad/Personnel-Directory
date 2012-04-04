""" Attributes retrieved for a user.  Quick copy/paste from Excel - this may need some help """

MEMBER_ATTRIBUTE_LIST = [ 'memberOf', 'employeeNumber', 'harvardEduIDNumber', 'harvardEduIDCardNumber', 'harvardEduGender', 'harvardEduBirthDate', 'distinguishedName', 'dn', 'userID', 'uid', 'personalTitle', 'givenName', 'harvardEduMiddleName', 'surname', 'sn', 'generationQualifier', 'harvardEduSuffixQualifier', 'commonName', 'cn', 'harvardEduRegisteredName', 'harvardEduRegisteredSortName', 'displayName', 'harvardEduDisplaySortName', 'eduPersonAffiliation', 'harvardEduPersonaNonGrata', 'harvardEduImagePrivacy', 'harvardEduCardDisabled', 'harvardEduCurrentIDCard', 'harvardEduSpecialRoleStatus', 'harvardEduOtherSpecialStatus', 'organizationName', 'o', 'objectClass', 'harvardEduSpecialPrivacy', 'harvardEduBorrowerCode', 'harvardEduEmployeePrivacy', 'departmentNumber', 'title', 'harvardEduPrimeJobDN', 'harvardEduJobDN', 'harvardEduLongerServiceEmployee', 'harvardEduRetireeSpecialStatus', 'harvardEduHRPersonStatus', 'harvardEduLastJobTerminatedOn', 'harvardEduHRDepartmentShortDescription', 'harvardEduStudentPrivacy', 'harvardEduSchool', 'harvardEduStudentStatus', 'harvardEduStudentSpecialStatus', 'harvardEduGraduationDate', 'harvardEduStudentYear', 'harvardEduResidenceHouse', 'harvardEduHouseOfRecord', 'harvardEduBoardHouse', 'harvardEduOnBoardPlan', 'harvardEduSISStatus', 'harvardEduFerpaStatus', 'harvardEduFerpaPastStudentIndicator', 'harvardEduLastDateOfAttendance', 'mail', 'harvardEduMailPrivacy', 'harvardEduDisplayAddress', 'telephoneNumber', 'harvardEduPhonePrivacy', 'facsimileTelephoneNumber', 'fax', 'harvardEduFaxPrivacy', 'harvardEduDirectoryListing', 'homeTelephoneNumber', 'homePhone', 'harvardEduHomePhonePrivacy', 'mobileTelephoneNumber', 'mobile', 'harvardEduMobilePrivacy', 'harvardEduPostalAddressInternal', 'postalAddress', 'localityName', 'l', 'stateOrProvinceName', 'st', 'harvardEduOfficeInternalPostalCode', 'postalCode', 'c', 'countryName', 'co', 'friendlyCountryName', 'harvardEduOfficeAddressPrivacy', 'harvardEduOfficeAddressType', 'harvardEduOfficeAddrSource', 'harvardEduOfficeAddrUpdatedBy', 'harvardEduOfficeAddrUpdatedOn', 'harvardEduHomePostalAddressInternal', 'homePostalAddress', 'harvardEduHomeLocality', 'harvardEduHomeState', 'harvardEduHomeInternalPostalCode', 'harvardEduHomePostalCode', 'harvardEduHomeFriendlyCountryName', 'harvardEduHomeAddressPrivacy', 'harvardEduHomeAddressType', 'harvardEduHomeAddrSource', 'harvardEduHomeAddrUpdatedBy', 'harvardEduHomeAddrUpdatedOn', 'harvardEduStudentOriginalPhone', 'harvardEduStudentDormRoom', 'harvardEduStudentMailingAddress', 'harvardEduDormAddressPrivacy', 'harvardEduMailingAddress', 'harvardEduIDExpirationDate', 'harvardEduIDLogin', 'harvardEduIDOwner', 'roleOccupant',  'harvardEduIsPrimaryJob', 'departmentNumber', 'harvardEduJobStartDate', 'harvardEduJobEndDate', 'harvardEduJobStatus', 'harvardEduJobNumber', 'distinguishedName', 'dn', 'commonName', 'cn', 'objectClass', 'harvardEduJobCode', 'manager', 'harvardEduEmploymentStatus', 'harvardEduPayGroup', 'harvardEduEmployeeClass', 'harvardEduJobLocationCode', 'harvardEduJobIsUnpaid']

NON_LIST_MEMBER_ATTRIBUTES = MEMBER_ATTRIBUTE_LIST[0:]
# needs adjustment
LIST_ATTRS = ['title', 'memberOf', 'eduPersonAffiliation', 'harvardEduSchool']
for attr in LIST_ATTRS:
    NON_LIST_MEMBER_ATTRIBUTES.remove(attr) 


class MemberInfo:
    """ Used to hold AD User information """
    
    def __init__(self, lookup):
        """ Uses an LDAP dictionary for the constructor """
        for attr in MEMBER_ATTRIBUTE_LIST:
            try:
                val = lookup.get(attr, None) 
                if val is None:
                    val = lookup.get(attr.lower(), None)      # some attributes are all lowercase in ldap, but mixed case in docs               
            except AttributeError:
                val = None
                
            #print '%s -> --%s--' % (attr, val)
            if attr in NON_LIST_MEMBER_ATTRIBUTES and not val==None:
                val = val[0]
                
            self.__dict__.update({ attr :val })            
    
    
    def get_or_blank(self, attr_name):
        if attr_name is None:
            return ''

        val = self.__dict__.get(attr_name, None)
        if val == None or val =='':
            return ''
        return val
        
    def get_or_neg1(self, attr_name):
        if attr_name is None:
            return -1
            
        val = self.__dict__.get(attr_name, None)
        if val == None or val =='':
            return -1
        return val
        
    def show(self):
        keys = self.__dict__.keys()
        keys.sort()
        for k in keys:
            val = self.__dict__.get(k)
            if val:
                print '%s: [%s]' % (k, val)
         
    def __unicode__(self):
        """ Return the display name """
        return self.displayName

"""
drop table hu_ldap_harvardpersoninfo;
drop table  hu_ldap_harvardpersoninfo_titles;
drop table  hu_ldap_harvardtitle;

from person.models import *
from hu_ldap.models import *
HarvardPersonInfo.objects.all().delete()
l = Person.objects.all()
for p in l:  
    print ", %s : '%s'" % (p.id, p.hu_ldap_uid)
    if p.hu_ldap_uid:
        hp = HarvardPersonInfo(person=p, uid=p.hu_ldap_uid)
        hp.save()
        print 'person saved', hp
        
cnt=0
for p in HarvardPersonInfo.objects.all(): cnt+=1; print cnt, p        
"""
