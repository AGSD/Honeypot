import time
import BaseHTTPServer
import logging
import os
from HTTPHandler import HTTPHandler
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Honeypot:
    def __init__(self,h='192.168.56.1',p=8080):
        self.host=h
        self.port=p
        self.httpd = BaseHTTPServer.HTTPServer((self.host,self.port), HTTPHandler)
        f = open("dir.txt","w+")
        logger.info('populating dir')
        self.populateDir(f,'www')
        f.close()

    def run(self):
        logger.info( str(time.asctime())+ " Server Starts - %s:%s" % (self.host, self.port))
        try:
            self.httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        self.terminate();

    def terminate(self):
        self.httpd.server_close();
        logger.info(str(time.asctime()) + " Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER))

    def populateDir(s,fi,p):
        l = os.listdir(p)
        for f in l:
            if os.path.isdir(p+'/'+f) == True:
                s.populateDir(fi,p+"/"+f)
            else:
                fi.write(p+'/'+f+'\n')

if __name__ == '__main__':
    Honeypot().run()
