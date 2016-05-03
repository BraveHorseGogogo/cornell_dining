from icalendar import Calendar, Event
import re
import datetime
from pytz import timezone
import pytz

def weekday_num_converter(weekday_str):
    if weekday_str == "SU":
        return 0
    elif weekday_str == 'MO':
    	return 1
    elif weekday_str == 'TU':
    	return 2
    elif weekday_str == 'WE':
    	return 3
    elif weekday_str == 'TH':
    	return 4
    elif weekday_str == 'FR':
    	return 5
    elif weekday_str == 'SA':
    	return 6
    else:
    	return -1

class Hours(object):
    """docstring for Hours"""

    def __init__(self):
        super(Hours, self).__init__()
        self.are_data_updated = [-1]*10
        self.today_hour = dict()
        self.meal_dict = dict(breakfast=0,brunch=1,lunch=2,dinner=3,closed=4,open=5)
        self.next_six_days_hour = dict()

    def is_today_in_weekly_rrule(self, now, rrule):
        today_weekday = int(now.strftime("%w"))
        is_today_hit = 0
        for byday_itm in rrule['BYDAY']:
            # print byday_itm
            day_number = weekday_num_converter(byday_itm)
            if today_weekday == day_number:
                is_today_hit = 1
                break
        # print is_today_hit
        return is_today_hit

    """this method is for testing"""
    def hours(self,ics_file_name):
        # dining_hall_id = int(ics_file_name.split(".")[0])
        
        #print now.strftime("%w")
        g = open(ics_file_name,'rb')
        gcal = Calendar.from_ical(g.read())
        
        #self.today_hour[str(ics_file_name.split(".")[0])]=today_open_hour
        #print "hours called"
        key = str(re.split('[./]',ics_file_name)[4])
        """
        This function return a dict return the opening hours and closed hours for each dining hall in the coming 7 days, including today
        """
        for day in xrange(0,7):
            today_close_hour = []
            today_open_hour = []
            #now = datetime.datetime.now(pytz.utc)+datetime.timedelta(days=day)
            now = datetime.datetime.now(pytz.timezone('US/Eastern'))+datetime.timedelta(days=day)
            if day == 0:
                self.today_hour[key]=today_open_hour
            else:
                day_dict = self.next_six_days_hour.get(str(day))
                if day_dict == None:
                    day_dict = dict()
                    self.next_six_days_hour[str(day)]=day_dict
                day_dict[key]=today_open_hour
        # print len(self.today_hour.keys())
            for component in gcal.walk():
                if component.name == 'VEVENT':
                    if component.get('SUMMARY') == None:
                        continue
                    summary_list = str(component.get('SUMMARY')).split(" ")
                
                    event_type = "NO"
                    is_limited = 0
                    for sum_itm in summary_list:
                        lower_itm = sum_itm.lower()
                        if lower_itm == 'limited' or lower_itm == 'house':
                            is_limited = 1
                        if self.meal_dict.get(lower_itm) != None and event_type == "NO":
                            event_type = lower_itm
                
                    if event_type == 'limited':
                        event_type = (summary_list[1]).lower()
                        is_limited = 1
                
                    event_start = component.get('DTSTART').dt
                    # print type(event_start)
                    if type(event_start) != datetime.datetime:
                        event_start = datetime.datetime(event_start.year, event_start.month,event_start.day)
                    event_end = component.get('DTEND').dt
                    if type(event_end) != datetime.datetime:
                        event_end = datetime.datetime(event_end.year, event_end.month, event_end.day)
                    # print event_type
                    if event_type == 'closed':
                        rrule = component.get('RRULE')

                        if rrule != None and (rrule.get('UNTIL') == None or (type(rrule['UNTIL'][0]) == type(now) and now < rrule['UNTIL'][0]) or (type(rrule['UNTIL'][0]) != type(now) and now.date() < rrule['UNTIL'][0])) and now.date() >= event_start.date():

                            if rrule['FREQ'][0] == 'WEEKLY' and self.is_today_in_weekly_rrule(now,rrule) == 1:
                                today_close_hour.append(dict(dtstart=event_start,
                                                     dtend=event_end))
                            elif rrule['FREQ'][0] == 'DAILY':
                                count_array = rrule.get('COUNT')
                                if count_array == None:
                                    continue
                                count = count_array[0]
                                if count != None and (now.date()-event_start.date()).days+1 > count :
                                    continue
                                else :
                                    today_close_hour.append(dict(dtstart=event_start,
                                                     dtend=event_end))
                        if rrule == None and (now.date()>=event_start.date() and now.date()<=event_end.date()):
                            today_close_hour.append(dict(dtstart=event_start,
                                            dtend=event_end))

                    elif event_type != 'NO':
                        rrule = component.get('RRULE')
                        if rrule != None and (rrule.get('UNTIL') == None or now < rrule['UNTIL'][0]) and now.date() >= event_start.date():

                            if (rrule['FREQ'][0] == 'WEEKLY' and self.is_today_in_weekly_rrule(now,rrule) == 1) or rrule['FREQ'][0] == 'DAILY':
                                event_already_exist = 0
                                for today_hour_itm in today_open_hour:
                                    if today_hour_itm['event_type'] == event_type and today_hour_itm['is_limited'] == is_limited:
                                        event_already_exist = 1
                                        break
                                if event_already_exist == 0:
                                    today_open_hour.append(dict(event_type=event_type,
                                                     is_limited=is_limited,
                                                     dtstart=event_start,
                                                     dtend=event_end))

            for close_hour_itm in today_close_hour:
                for open_hour_itm in today_open_hour:
                    if type(close_hour_itm['dtstart']) == datetime.date:
                        for open_hour_itm2 in today_open_hour:
                            today_open_hour.remove(open_hour_itm2)
                        return
                    else:
                        open_itm_start = open_hour_itm['dtstart'] + datetime.timedelta(days=(now.date() - open_hour_itm['dtstart'].date()).days)
                        open_itm_start = open_itm_start.replace(tzinfo=None)
                        open_itm_end = open_hour_itm['dtend'] + datetime.timedelta(days=(now.date() - open_hour_itm['dtend'].date()).days)
                        if open_itm_start.time() > open_itm_end.time():
                            open_itm_end = open_itm_end + datetime.timedelta(days=1)
                        open_itm_end = open_itm_end.replace(tzinfo=None)
                        close_itm_start = close_hour_itm['dtstart'] + datetime.timedelta(days=(now.date() - close_hour_itm['dtstart'].date()).days)
                        close_itm_start = close_itm_start.replace(tzinfo=None)
                        close_itm_end = close_hour_itm['dtend'] + datetime.timedelta(days=(now.date() - close_hour_itm['dtend'].date()).days)
                        
                        if close_itm_start.time() > close_itm_end.time():

                            close_itm_end = close_itm_end + datetime.timedelta(days=1)
                        close_itm_end = close_itm_end.replace(tzinfo=None)
                        if (open_itm_start >= close_itm_start and open_itm_end <=close_itm_end) \
                        or (close_itm_start >= open_itm_start and close_itm_end <= open_itm_end):

                            today_open_hour.remove(open_hour_itm)
                        elif (open_itm_start >= close_itm_start and open_itm_start <= close_itm_end) and open_itm_end >= close_itm_end:

                            open_hour_itm['dtstart'] = close_hour_itm['dtend']
                        elif (open_itm_end >= close_itm_start and open_itm_end <= close_itm_end) and open_itm_start <= close_itm_start:

                            open_hour_itm['dtend'] = close_hour_itm['dtend']
            today_open_hour = sorted(today_open_hour, key = lambda x: self.meal_dict[x['event_type']])
            # print today_open_hour
            # print today_close_hour
            # print today_open_hour
            # print "Hello"
            # print self.today_hour
# test = Hours()
# test.hours("./static/ics/2.ics")

