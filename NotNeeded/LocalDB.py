import sqlite3

class LocalDB:
    
    def is_allowed(self, rfid):
        db = sqlite3.connect('ControlPanel.db')

        cur = db.cursor()
        #NOTE: took out check for expiry date because my tag has expired.. 
        #NOTE: Also we should include a grace period, as before -Leo 
        #cur.execute("SELECT name FROM access_list WHERE rfid = '%s' and end_date > date('now')" % rfid)
        cur.execute("SELECT name FROM access_list WHERE rfid = '%s'" % rfid)
        results = cur.fetchall()
        
        db.close()

        if len(results) == 0:
            return (None, False)
        else:
            return (results[0], True)
        
    def get_current_occupants(self):
        db = sqlite3.connect('ControlPanel.db')
        
        cur = db.cursor()
        cur.execute("SELECT rfid from current_occupants")
        
        results = cur.fetchall()
        
        db.close()
        
        return results

    def add_occupant(self, rfid):
        db = sqlite3.connect('ControlPanel.db')
        
        cur = db.cursor()
        cur.execute("INSERT INTO current_occupants VALUES(" + str(rfid) + ")")
        db.commit()    
        db.close()
        
    def get_access_notify_members(self):
        db = sqlite3.connect('ControlPanel.db')
        
        cur = db.cursor()
        cur.execute("SELECT * FROM access_list WHERE access = 1")
        
        results = cur.fetchall()
        
        db.close()
        
        return results

    def get_alarm_notify_members(self):
        db = sqlite3.connect('ControlPanel.db')
        
        cur = db.cursor()
        cur.execute("SELECT * FROM access_list WHERE alarm = 1")
        
        results = cur.fetchall()
        
        db.close()
        
        return results
    
    def get_member_by_rfid(self, rfid):
        db = sqlite3.connect('ControlPanel.db')
        
        cur = db.cursor()
        cur.execute("SELECT * FROM access_list WHERE rfid = '%s'" % rfid)
        
        result = cur.fetchone()
        
        return result

    def get_id_by_rfid(self, rfid):
        db = sqlite3.connect('ControlPanel.db')
        cur = db.cursor()
        cur.execute("SELECT id FROM access_list WHERE rfid = '%s'" % rfid)
        result = cur.fetchone()
        return result
    
    def log_access_granted(self, rfid):
        db = sqlite3.connect('ControlPanel.db')
        
        cur = db.cursor()
        id = self.get_id_by_rfid(self, rfid)
        cur.execute("INSERT INTO access_log (id, action, synced, date) VALUES (%d, 'Access Granted', 0, DATETIME('now'))" % id)
        db.commit()   
        db.close()

    def log_access_denied(self, rfid):
        db = sqlite3.connect('ControlPanel.db')
        cur = db.cursor()

        id_row = self.get_id_by_rfid(rfid)
        if id_row is None:
            id = 0
        else:
            id = id_row[0]

        print id
        print rfid
        cur.execute("INSERT INTO access_log (id, action, synced, date) VALUES (%d, 'Access Denied to RFID: %d', 0, DATETIME('now'))" % (id, rfid))
        db.commit()   
        db.close()
    
    def get_member_by_rfid(self, rfid):
        db = sqlite3.connect('ControlPanel.db')
        
        cur = db.cursor()
        cur.execute("SELECT * FROM access_list WHERE rfid = '%s'" % rfid)
        
        result = cur.fetchone()
        
        if result is not None:
            return result
        return False
    
    def get_member_details(self, rfid):
        db = sqlite3.connect('ControlPanel.db')
        
        cur = db.cursor()
        cur.execute("SELECT name,phone,end_date FROM access_list WHERE rfid = '%s' and phone is not null" % rfid)
        results = cur.fetchall()
        db.close()
        
        return results
    
    # clears current occupants
    def clear_current_occupants(self):
        db = sqlite3.connect('ControlPanel.db')
        cur = db.cursor()
        cur.execute("DELETE from current_occupants")
        db.commit()
        db.close()
