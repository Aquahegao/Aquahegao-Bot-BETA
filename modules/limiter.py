from threading import Timer, Semaphore


class Limiter(object):
    def __init__(self, limit, time):
        self.sema = Semaphore(limit)
        self.time = time

    def acquire(self):
        self.sema.acquire()
        thread = Timer(self.time, self.release)
        thread.daemon = True
        thread.start()
        return thread

    def cancel(self, thread):
        thread.cancel()
        self.sema.release()

    def release(self):
        self.sema.release()


class ShortLimiter(Limiter):
    def __init__(self, limit):
        super(ShortLimiter, self).__init__(limit, 30)


class LongLimiter(Limiter):
    def __init__(self, limit):
        day = 60 * 60 * 24
        super(LongLimiter, self).__init__(limit, day)
