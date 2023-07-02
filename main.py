from ics import Calendar
import requests
import configparser

config = configparser.ConfigParser()
config.read("./config.ini")


# Parse the URL
#ICAL = "https://outlook.office365.com/owa/calendar/b0e8c31afbbd4c53a12a32d94c447d92@liu.se/5cb28d5392c14bf3ba4699b6fc76ea4417369955892265280648/calendar.ics"
ICAL = config["CALENDAR"]["CalendarURL"]


print("=== Read calendar events ===")
cal = Calendar(requests.get(ICAL).text)
print("Found {} events".format(len(cal.events)))
print(cal.events)
events = cal.events
sorted_events = sorted(events)
print("=== === ")
print(sorted_events)
print("=== === ")
print(list(sorted_events))
print(sorted_events[0].begin)
# init the calendar