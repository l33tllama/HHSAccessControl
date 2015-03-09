from apscheduler.scheduler import Scheduler
import pigpio
import datetime as dt
class GPIOControl:
    
    def __init__(self, pi):
        self.sched = Scheduler()
        self.sched.start()
        self.pi = pi

    def timeout(self, job_fn, *fn_args, **delta_args):
        """
        Usage:
            # calls `fn()` after 3 seconds
            timeout(fn, seconds=3)

            # calls `fn(foo, bar)` after 10 seconds
            timeout(fn, foor, bar, seconds=10)
        """
        time = dt.datetime.now() + dt.timedelta(**delta_args)
        return self.sched.add_date_job(job_fn, time, fn_args)

    def on(self, pin):
        pi = self.pi
        pi.set_mode(pin, pigpio.OUTPUT)
        pi.write(pin,1)

    def off(self, pin):
        pi = self.pi
        pi.set_mode(pin, pigpio.OUTPUT)
        pi.write(pin,0) 
