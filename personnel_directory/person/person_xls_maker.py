import xlwt
from xlwt import easyxf
from personnel_directory.common.xls_styles import *
from personnel_directory.person.models import Person, SecondaryTitle

def get_max_len_attr(attr_name, lst_people, char_multiplier=256):
    # iterate through each attribute, turn it into a string, and then a len() integer
    '''for ln in lst_people:
        print ln.lname
        print unicode(ln.lname)
    '''
    attr_lengths = map(lambda x: len( unicode(x.__dict__.get(attr_name, ''))  ), lst_people)
    max_len = max( attr_lengths)
    
    if max_len < 10:
        return 10 * char_multiplier
    return max_len * char_multiplier
    
def get_secondary_office_person_ids():
    return Person.objects.exclude(secondary_offices=None).filter(visible=True).values_list('id', flat=True)

def get_secondary_lab_person_ids():
    return Person.objects.exclude(secondary_labs=None).filter(visible=True).values_list('id', flat=True)

def get_secondary_title_person_ids():
    return SecondaryTitle.objects.all().values_list('person__id', flat=True)
    

def make_person_roster(sheet1, info_line, people, **kwargs):
    """Spreadsheet for MCB Core admin use"""
    if sheet1 is None:
        return None
    if people is None:
        return sheet
                  
    if info_line:
        sheet1.write(0, 0, info_line, style_info_cell)

    #   (header label, attribute, width)
    column_attributes = [ ('Last Name', 'lname', 20)
    ,('First Name', 'fname', 20)
    ,('Middle Initial', 'minitial', 20)
    ,('Email', 'email', 30)
    ,('HU directory Email', 'hu_email', 30)
    ,('2nd Email', 'second_email', 30)
    ,('Phone', 'phone', 15)
    ,('2nd Phone', 'second_phone', 15)
    ,('Room', 'room', 15)
    ,('Address', 'address', 20)
    ,('City', 'city', 20)
    ,('State', 'state', 20)
    ,('Zip', 'zip', 20)
    ,('Appointment', 'appointment', 20)
    ,('Affiliation', 'affiliation', 20)
    ,('Title', 'title', 20)
    ,('Secondary Titles', 'secondary_titles', 20)
    ,('Grad Program', 'grad_program', 20)
    ,('Grad Year', 'grad_year', 20)
    ,('Office', 'office', 20)
    ,('Secondary Offices', 'secondary_offices', 20)
    ,('Primary Lab', 'primary_lab', 20)
    ,('Primary Lab Affiliation', 'primary_lab_affiliation', 15)
    ,('Secondary Labs', 'secondary_labs', 20)
    ]
    
    #----------------------------
    # Add the header row and set column widths
    #----------------------------
    char_multiplier = 256
    excel_row_num = 1
    for col_idx, (col_name, attr_name, col_width) in enumerate(column_attributes):
        sheet1.write(excel_row_num, col_idx, col_name, style_header)
        sheet1.col(col_idx).width = col_width * char_multiplier  

        
    # Set the column widths for the spreadsheet, based on the widest value for each column
    #    
    
    
    foreign_key_attrs = """appointment affiliation title grad_program grad_year office primary_lab primary_lab_affiliation""".split()

    ids_of_people_with_secondary_labs = get_secondary_lab_person_ids()
    ids_of_people_with_seconary_titles = get_secondary_title_person_ids()
    ids_of_people_with_secondary_offices = get_secondary_office_person_ids()

    #   Add data to the spreadsheet
    #
    for p in people:
        excel_row_num +=1

        for col_idx, (col_name, attr, col_width) in enumerate(column_attributes):
            
            if attr in ['city', 'state', 'zip']:
                continue
            elif attr== 'hu_email':
                try:
                    hu_email = p.harvardpersoninfo_set.all()[0].email
                except:
                    hu_email = 'n/a'
                sheet1.write(excel_row_num, col_idx, hu_email, style_info_cell_wrap_on) 
                 
            elif attr == 'address':
                if p.building:
                    addr_str = p.building.addr1
                    if p.building.addr2:
                        addr_str += '\n%s' % p.building.addr2
                    sheet1.write(excel_row_num, col_idx, addr_str, style_info_cell_wrap_on);     col_idx+=1
                    sheet1.write(excel_row_num, col_idx, p.building.city, style_info_cell); col_idx+=1                  
                    sheet1.write(excel_row_num, col_idx, p.building.state, style_info_cell); col_idx+=1
                    sheet1.write(excel_row_num, col_idx, p.building.zipcode, style_info_cell)
                else:   
                    # blank out address info
                    sheet1.write(excel_row_num, col_idx, '', style_info_cell_wrap_on);     col_idx+=1
                    sheet1.write(excel_row_num, col_idx, '', style_info_cell); col_idx+=1                  
                    sheet1.write(excel_row_num, col_idx, '', style_info_cell); col_idx+=1
                    sheet1.write(excel_row_num, col_idx, '', style_info_cell)
            
            elif attr in foreign_key_attrs:
                cell_val = ''
                if attr == 'primary_lab' and p.primary_lab:     # exception b/c str() val is two fields
                    cell_val = p.primary_lab.name
                elif attr == 'primary_lab_affiliation' and p.primary_lab and p.primary_lab.affiliation:
                    cell_val = p.primary_lab.affiliation.name
                elif attr == 'primary_lab_affiliation':
                    cell_val = ''
                else:    
                    cell_val = str(eval('p.' + attr))
                    if cell_val == 'None': 
                        cell_val = ''
                sheet1.write(excel_row_num, col_idx, cell_val, style_info_cell_wrap_on)  

            elif attr == 'secondary_titles':
                title_str = ''
                if p.id in ids_of_people_with_seconary_titles:
                    titles = []
                    for st in SecondaryTitle.objects.filter(person=p):
                        titles.append(st.title.title)
                    if len(titles) > 0: title_str = '\n'.join(titles)
                sheet1.write(excel_row_num, col_idx, title_str, style_info_cell_wrap_on)  

            elif attr == 'secondary_offices':
                office_str = '' 
                if p.id in ids_of_people_with_secondary_offices:
                    offices = []
                    for office in p.secondary_offices.all():
                        offices.append(office.name)
                    if len(offices) > 0: 
                        office_str = '\n'.join(offices)
                sheet1.write(excel_row_num, col_idx, office_str, style_info_cell_wrap_on)  
            
            elif attr == 'secondary_labs':
                lab_str = '' 
                if p.id in ids_of_people_with_secondary_labs:
                    labs = []
                    for lab in p.secondary_labs.all():
                        labs.append(lab.name)
                    if len(labs) > 0: 
                        lab_str = '\n'.join(labs)
                sheet1.write(excel_row_num, col_idx, lab_str, style_info_cell_wrap_on)  
            else:
                # default for most attributes
                sheet1.write(excel_row_num, col_idx, unicode(p.__dict__.get(attr,  '')), style_info_cell_wrap_on)  
            col_idx+=1
        
    
    return sheet1
