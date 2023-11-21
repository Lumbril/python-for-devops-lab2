import atexit
import os
import signal
import sys
import time


class Daemon:
    def __init__(self, pidfile):
        self.pidfile = pidfile

    def daemonize(self):
        try:
            pid = os.fork()

            if pid > 0:
                sys.exit(0)
        except OSError as err:
            sys.stderr.write('fork #1 failed: {0}\n'.format(err))
            sys.exit(1)

        os.chdir('/')
        os.setsid()
        os.umask(0)

        try:
            pid = os.fork()

            if pid > 0:
                sys.exit(0)
        except OSError as err:
            sys.stderr.write('fork #2 failed: {0}\n'.format(err))
            sys.exit(1)

        sys.stdout.flush()
        sys.stderr.flush()
        si = open(os.devnull, 'r')
        so = open(os.devnull, 'a+')
        se = open(os.devnull, 'a+')

        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        atexit.register(self.delpid)

        pid = str(os.getpid())

        with open(self.pidfile, 'w+') as f:
            f.write(pid + '\n')

    def delpid(self):
        os.remove(self.pidfile)

    def start(self):
        if os.path.exists(self.pidfile):
            print("Daemon is running")
            sys.exit(0)

        self.daemonize()
        self.run()

    def stop(self):
        if not os.path.exists(self.pidfile):
            print("Daemon is not running")
            sys.exit(0)

        with open(self.pidfile, 'r') as pid_file:
            pid = pid_file.readline()

        if not pid:
            print("Daemon is not running")
            sys.exit(0)

        self.delpid()
        os.kill(int(pid), signal.SIGTERM)

    def restart(self):
        self.stop()
        self.start()

    def run(self):
        while True:
            time.sleep(1)

