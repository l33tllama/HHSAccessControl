from LocalDB import LocalDB
from GPIOControl import GPIOControl
from Broadcaster import Broadcaster
class AlarmControl:
    
    ALARM_TOGGLE_PIN = 10
    ALARM_ARMED_STATUS_PIN = 8 
    ARM_ALARM_BUTTON_PIN = 3
    ALARM_SOUNDING_STATUS_PIN = 7
    
    def __init__(self, pi):
        self.pi = pi
        self.gpio = GPIOControl(self.pi)
        self.bcast = Broadcaster()
        self.db = LocalDB()
        self.arming = False
        self.is_alarm_arming = False
    
    def alarmSounding(self):
        #messages everyone on the alarm list (second last column)
        # set a flag so that if the alrarm is turned off by any member, it messages the entire alarm list (not just the access list)
        alert_alarm_members("Alarm at the Hackerspace has been activated (is Sounding)!")
        self.is_alarm_sounding = True

    def toggle_alarm_pin(self):
        gpio = self.gpio
        gpio.on(AlarmControl.ALARM_TOGGLE_PIN)
        gpio.timeout(gpio.off, AlarmControl.ALARM_TOGGLE_PIN,seconds=3)
        
    def alarm_arming(self):
        self.arming = False
    
    def is_alarm_armed(self):
        return self.pi.read(ALARM_ARMED_STATUS_PIN) == 0
    
    # Alarm arm button callback
    def armAlarm(self, gpio, level, tick) :

        if self.arming:
            return
        self.arming = True
        io = self.gpio
        io.timeout(self.alarm_arming,seconds=10)

        # checks alarm status
        if not is_alarm_armed(): 
            toggle_alarm_pin()

        # ourput buzzer for 3 seconds
        io.off(25)
        io.timeout(io.on,25,seconds=8)
        
        self.db.clear_current_occupants()
        print "deleted all occupants"
        
        # message the access list of people
        print "Alarm is Armed"
        self.bcast.alert_access_members("The Alarm has been Armed")


