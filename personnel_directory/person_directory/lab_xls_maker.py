import xlwt
from xlwt import easyxf
from common.xls_styles import *


def make_lab_member_roster(sheet1, info_line, people, lab_obj=None):
    if sheet1 is None:
        return None
    if people is None:
        return sheet
    
    row_num =0
    if info_line:
        sheet1.write(row_num, 0, info_line, style_info_cell)
    
    row_num+=1
    if lab_obj:
        sheet1.write(row_num, 0, '%s Lab Member List' % (lab_obj.name), style_info_cell_bold)        
    else:
        sheet1.write(row_num, 0, 'Lab Member List', style_info_cell_bold)
    
    # header column
    row_num+=1
    col_names = """Name,Position,Phone,Email,mcb username,Room,Location,Address""".split(',')
    for idx, col_name in enumerate(col_names):
        sheet1.write(row_num, idx, col_name, style_header)


    char_multiplier = 256

    # Set the column widths for the spreadsheet, based on the widest value for each column
    #    
    if people.count() > 0:
        # Set the column widths for the spreadsheet, based on the widest value for each column
        #    
        sheet1.col(0).width = max([attr_len(p) for p in people]) * char_multiplier
        sheet1.col(1).width = max([attr_len(p.title) for p in people]) * char_multiplier
        sheet1.col(2).width = 20  * char_multiplier  #max([attr_len(p.phone) for p in people]) * char_multiplier
        sheet1.col(3).width = max([attr_len(p.email) for p in people]) * char_multiplier
        sheet1.col(4).width = max([attr_len(p.ad_username) for p in people]) * char_multiplier
        sheet1.col(5).width = max([attr_len(p.room) for p in people]) * char_multiplier
        sheet1.col(6).width = max([attr_len(p.get_building_name()) for p in people]) * char_multiplier
        sheet1.col(7).width = max([attr_len(p.address_col_xls()) for p in people]) * char_multiplier

     
    #   Add data to the spreadsheet
    #
    for p in people:
        row_num +=1
        sheet1.write(row_num, 0, '%s' % p, style_info_cell)   # column 1
        if p.title:
            sheet1.write(row_num, 1, p.title.title, style_info_cell)  
        else:
            sheet1.write(row_num, 1, '', style_info_cell)  
            
        phone = fmt_phone(p.phone)
        if p.second_phone:
            phone += ' \n%s' % fmt_phone(p.second_phone)
        sheet1.write(row_num, 2, phone, style_info_cell_wrap_on)  

        fmt_email = p.email
        if p.second_email:
            fmt_email += ' \n%s' % p.second_email
        sheet1.write(row_num, 3, fmt_email, style_info_cell_wrap_on)  
        sheet1.write(row_num, 4, fmt_domain(p.ad_username), style_info_cell)  
        sheet1.write(row_num, 5, p.room, style_info_cell)  
        sheet1.write(row_num, 6, p.get_building_name(), style_info_cell)  
        sheet1.write(row_num, 7, p.address_col_xls(), style_info_cell)
        
    return sheet1

    
