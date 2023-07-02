from ics import Calendar
import requests
import configparser
import logging
from time import sleep
import arrow

def qtl_parse_bool(s):
    if s.lower() in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh']:
        return True
    elif s.lower() in ["false", "0", "f", "n", "no", "nope", "nah"]:
        return False
    else:
        return None


config = configparser.ConfigParser()
config.read("./config.ini")

# Get config groups
cCalendar = config["CALENDAR"]
cScheduling = config["SCHEDULING"]
cBookingSystem = config["BOOKING SYSTEM"]

# Get config parameters
pLogFile = cBookingSystem["LogFile"]
pCalendarURL = cCalendar["CalendarURL"]
pCalendarUpdateInterval = int(cBookingSystem["CalendarUpdateInterval"])
pUseDirectStartup = qtl_parse_bool(cScheduling["UseDirectStartup"])
pGracePeriod = int(cScheduling["GracePeriod"])
pCryogenicCooldownPeriod = int(cScheduling["CryogenicCooldownPeriod"])

# Setup logging
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', filename=pLogFile, encoding="utf-8", level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler())

logging.info("=== STARTED QTL SNSPD BOOKING ===")
# State
has_started = False
events = []

#### FUNCTION HANDLE FOR API TRIGGER
def startSNSPD():
    logging.info("Starting SNSPD")
    global has_started
    has_started = True
    sleep(5)

def stopSNSPD():
    logging.info("Stopping SNSPD")
    global has_started
    has_started = False
    sleep(5)
### END FUNCTION HANDLE


while True:
    cal = Calendar(requests.get(pCalendarURL).text)

    events = cal.events
    sorted_events = sorted(events)
    sorted_events = [x for x in sorted_events if x.begin > arrow.now()]
    logging.info("Found events {}".format([x.name for x in sorted_events]))
    next_event = sorted_events[0]
    next_event_start = arrow.get(next_event.begin)
    next_event_stop = arrow.get(next_event.end)


    if len(events) >= 2:
        next_next_event = sorted_events[1]
        next_next_event_start = arrow.get(next_next_event.begin)
        next_next_event_stop = arrow.get(next_next_event.end)
    else:
        logging.warning("Found only 1 booking. If no other bookings are made, system will shutdown after end of booking.")


    cur_time = arrow.now()

    startup_time_before_booking = pCryogenicCooldownPeriod
    if pUseDirectStartup:
        startup_time_before_booking = 0

    if cur_time > next_event_start.shift(minutes=-startup_time_before_booking):
        if not has_started:
            logging.info("Time to start SNSPD")
            logging.info("Booking {}".format(next_event.name))
            startSNSPD()
    else:
        time_to_start = (next_event_start-cur_time)
        logging.info("Starting system for booking \"{}\" in {}".format(next_event.name, time_to_start))
    if has_started:
        if len(events) > 2:
            if next_next_event_start < next_event_stop.shift(minutes=+pGracePeriod):
                #Keep system running
                logging.info("Next event start @{} is within the grace period ({} hrs). System will NOT halt in between.".format(next_next_event_start, pGracePeriod))
            else:
                logging.info("Next event start @{} is outside the grace period ({} hrs). System halting...".format(next_next_event_start, pGracePeriod))
        else:
            if cur_time > next_event_stop:
                stopSNSPD()

    sleep(pCalendarUpdateInterval)

