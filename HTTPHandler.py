from analyzer import analyzeRequest
from saveRecord import saveRecord
import BaseHTTPServer
import logging
import os
import attackHandler
import urllib
import urlparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HTTPHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_HEAD(self):
        saveRecord(self)
        self.send_response(200)
        self.set_header()

    def do_GET(self):
        self.path=urllib.unquote(self.path).decode('utf8')
        if self.path == "/":
            self.path = "/index.php"
        reqType = analyzeRequest(self,"GET")
        if reqType == "rfi":
            ret = attackHandler.rfi(self)
            saveRecord(self,'rfi',ret)
        elif reqType == "lfi":
            ret = attackHandler.lfi(self)
            saveRecord(self,'lfi',ret)
        elif reqType == "xss":
            ret = attackHandler.xss(self)
            saveRecord(self,'xss',ret)
        else:
            #It is either normal, or one of the non emulated ones
            saveRecord(self,reqType)
            saveRecord(self,'normal')
            p = self.path.split('?')[0]
            path = p[1:]
            path = 'www/'+path
            f = open('dir.txt')
            c = f.read()
            f.close()
            l = c.split('\n')
            logger.info(path)
            for pa in l:
                if path == pa:
                    validPath=True
                    break
            else:
                validPath=False
            if validPath and p[1:]=='index.php':
                if "template=beige.php" in self.path:
                    self.send_response(200)
                    self.set_header()
                    reqFile = os.getcwd()+"/www"+p
                    fo = open(reqFile,'rb')
                    f = fo.read()
                    pos = f.find('<link href="css/custom.css" rel="stylesheet">')
                    self.wfile.write(f[:pos+45]+'\n'+'<style>body{background-color:#f1e2b9;}</style>'+f[pos+45:])
                    fo.close()
                else:
                    self.send_response(200)
                    self.set_header()
                    reqFile = os.getcwd()+"/www"+p
                    fo = open(reqFile,'rb')
                    f = fo.read()
                    pos = f.find('<link href="css/custom.css" rel="stylesheet">')
                    self.wfile.write(f[:pos+45]+'\n'+'<style>body{background-color:white;}</style>'+f[pos+45:])
                    fo.close()
            elif validPath and p[1:]=='about.php':
                if "city=" in self.path:
                    parsed = urlparse.urlparse(self.path)
                    val = urlparse.parse_qs(parsed.query)['city'][0]
                else:
                    val = "Bangalore"
                #Get ready to start rendering the page
                self.send_response(200)
                self.set_header()
                fo = open('www/about.php','rb')
                f = fo.read()
                fo.close()
                pos = f.find("<div id='head'>")
                self.wfile.write(f[:pos+15]+'\n'+val+'\n</div></p><p>')#XSS vulnerability
                if val == "Mumbai" or val == "Bangalore" or val=="Chennai" or val=="Delhi":
                    fname = val
                else:
                    fname = -1
                if fname!=-1:
                    detailFile = open('www/'+fname+'.txt','rb')
                    additive = detailFile.read()
                    detailFile.close()
                else:
                    additive= "FILE ERROR"
                pos = f.find("<div id='data'>")
                self.wfile.write('\n'+"<div id='data'>"+additive+f[pos+15:])
            
            elif validPath:
                self.send_response(200)
                self.set_header()
                reqFile = os.getcwd()+"/www"+p
                f = open(reqFile,'rb').read()
                self.wfile.write(f)
            else:
                self.send_response(404)

    def do_POST(self):
        if self.path == "/":
            self.path = "/index.php"
        #extract POST variables
        length = int(self.headers.getheader('content-length'))
        field_data = self.rfile.read(length)
        fields = urlparse.parse_qs(field_data)

        #append handler with corresponding post variables
        self.fields = fields
        self.path=urllib.unquote(self.path).decode('utf8') 
        reqType = analyzeRequest(self,"POST")
        if reqType == "normal":
            saveRecord(self,'normal')
            p = self.path.split('?')[0]
            path = p[1:]
            path = 'www/'+path
            f = open('dir.txt')
            c = f.read()
            f.close()
            l = c.split('\n')
            logger.info(path)
            for pa in l:
                if path == pa:
                    validPath=True
                    break
            else:
                validPath=False
            if validPath and p[1:]=='login.php':
                self.send_response(200)
                self.set_header()
                reqFile = os.getcwd()+"/www"+'/login.php'
                fo = open(reqFile,'rb')
                f = fo.read()
                pos = f.find('<head>')
                self.wfile.write(f[:pos+6]+'\n'+"<script>alert('Invalid login details')</script>"+f[pos+6:])
                fo.close()
            elif validPath:
                self.send_response(200)
                self.set_header()
                reqFile = os.getcwd()+"/www"+p
                f = open(reqFile,'rb').read()
                self.wfile.write(f)
            else:
                self.send_response(404)
        elif reqType == "sql":
            ret = attackHandler.sql(self)
            saveRecord(self,'sql',ret)
        
    def set_header(self): #Setting headers to mimic Apache 2
        self.server_version = "Apache/2.4.10 OpenSSL/1.0.1i PHP/5.6.3"
        self.sys_version = ""
        self.send_header("Content-Type","text/html; charset=UTF-8")
        self.send_header("Keep-Alive","timeout=5, max=99")
        self.send_header("Server","Apache/2.4.10 (Win32) OpenSSL/1.0.1i PHP/5.6.3")
        self.send_header("X-Powered-By","PHP/5.6.3")
        self.end_headers()

    def validate(self,path):
        #return True
        path = 'www/'+path
        f = open('dir.txt')
        c = f.read()
        f.close()
        l = c.split('\n')
        logger.info(path)
        for p in l:
            if path == p:
                return True
        else:
            return False
