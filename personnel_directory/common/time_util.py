from personnel_directory.common.msg_util import *
from platform import python_version
import datetime, calendar


#
#   Given a date time object, return a new object with:
#   - hour=0
#   - minute=0
#   - second=0
#   - microsecond=0
#
def get_zero_hour_datetime(dt):
    if dt==None:
        return None
        
    return datetime.datetime(year=dt.year, month=dt.month, day=dt.day, hour=0, minute=0, second=0, microsecond=0)

def get_midnight_hour_datetime(dt):
    if dt==None:
        return None
        
    return datetime.datetime(year=dt.year, month=dt.month, day=dt.day, hour=0, minute=0, second=0, microsecond=0) + get_time_delta(days=1)


#
#   input: "hh-mm"
#   return datetime.time object
#
def get_time_from_str(time_str):
    
    try: 
        hr, min = time_str.split('-')
        return datetime.time(hour=int(hr), minute=int(min))
    except:
        return None

def get_date_today():
    return datetime.date.today()
        
def get_datetime_now():
    return datetime.datetime.now()

def get_time_delta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0):

    return datetime.timedelta(days=days, seconds=seconds, microseconds=microseconds, milliseconds=milliseconds, minutes=minutes, hours=hours, weeks=weeks)
    


def build_datetime(year, month, day=1, hr=0, min=0, sec=0):
    #    return datetime.datetime(year=int(year), month=int(month), day=int(day), hour=int(hr), minute=int(min), second=int(second))

    try:
        return datetime.datetime(year=int(year), month=int(month), day=int(day), hour=int(hr), minute=int(min), second=int(sec))
    except:
        return None


def build_date(year, month=1, day=1):
    try:
        return datetime.date(year=int(year), month=int(month), day=int(day))
    except:
        return None
        
        
#
#   Input: year, month (from selected_day)
#   
#   Output: A list of the weeks. Each weeks is a list of seven datetime.date objects.
#
def pull_calendar_weeks(year, month, one_list=False):
        
    if python_version()[:3] == '2.4':
        pass
        
    else:           # assume 2.5 or higher
        # start the day of the week on sunday
        cal = calendar.Calendar(calendar.SUNDAY)            # make a calendar, sunday is the first day of the week

        if one_list:
            return cal.itermonthdates(year, month)
        
        # a list of the weeks. Each weeks is a list of seven datetime.date objects.
        cal_weeks = cal.monthdatescalendar(year, month)   
        
        
        return cal_weeks        
        
        
    calendar.setfirstweekday(calendar.SUNDAY)       # set sunday to first day of week
    week_lists = calendar.monthcalendar(year,  month)  #   pull array of arrays
    
    fmt_weeks = []
    for idx, week in enumerate(week_lists):
        fmt_one_week = []
        last_day = None

        # first week
        #
        if idx == 0:        
            week.reverse()          # reverse the order
            for day in week:
                if day ==0:         # day in previous month
                    date_obj = last_day + get_time_delta(days=-1)          
                    fmt_one_week.append(date_obj )
                else:
                    date_obj = build_date(year, month, day)
                    fmt_one_week.append(date_obj )
                last_day = date_obj
            fmt_one_week.reverse()
        #
        #   other weeks
        else:      
            for day in week:
                if day==0:           # day in next month
                    date_obj = last_day + get_time_delta(days=1)          
                    fmt_one_week.append(date_obj )
                else:     
                    date_obj = build_date(year, month, day)
                    fmt_one_week.append(date_obj )                
                last_day = date_obj
        #msgt(fmt_one_week)         
        fmt_weeks.append(fmt_one_week)
    
    if not one_list:
        return fmt_weeks         
    else:
        big_list = []
        for week in fmt_weeks:
            for day in week:
                big_list.append(day)
        return big_list
        
    
