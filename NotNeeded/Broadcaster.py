from LocalDB import LocalDB

# Todo: hook up to SMS, email, Twitter, etc
class Broadcaster:
    
    def __init__(self):
        self.db = LocalDB()
        
     #TODO: Send via SMS, email, or whatever
    def alert_access_members(self, message):
        access_notify_members = self.db.get_access_notify_members()    
        for anm in access_notify_members:
            print "Hey %s, " % anm[1] + message

    #TODO: send via SMS, email or whatever
    def alert_alarm_members(self, message):
        alarm_notify_members = self.db.get_alarm_notify_members()    
        for anm in alarm_notify_members:
            print "Hey %s, " % anm[1] + message