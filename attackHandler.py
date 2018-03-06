import urllib2
import os
import subprocess
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def rfi(requestHandler):
        phpLocation = r'D:\installs\xampp\php\php.exe'
        
        logger.info( "entered rfi handler")
	rh = requestHandler
	url = rh.path
	filename = url.split('?')[0]
	#find starting of the required link
	s = url.find('http')
	if s == -1:
		s = url.find('ftp')
        link = url[s:]
        e = link.find('&')
        #set the link
        if e != -1:
                link = link[:e]
	logger.info( "trying link " + link)
	#fetch the file from the link
	try:
                r = urllib2.Request(link)
                f = urllib2.urlopen(r,timeout=4).read()
                logger.info( "got file")
                #store the file
                storeName = link.split('/')[-1]
                for ch in ['\\','/','?',':','*','\"','<','>']:
                        if ch in storeName:
                                storeName = storeName.replace(ch,'')
                if os.path.isfile('data/rfi/'+storeName):
                                of = open('data/rfi/'+storeName,"r+")
                                if of.read() == f:
                                        logger.info( 'file already present')
                                else:
                                        i=1
                                        newName = storeName.split('.')[0]+str(i)+'.'+storeName.split('.')[1]
                                        while os.path.isfile('data/rfi/'+newName):
                                                        of.close()
                                                        of = open('data/rfi/'+newName,"r+")
                                                        if of.read() == f:
                                                                logger.info( 'file already present')
                                                                storeName = newName
                                                                of.close()
                                                                break
                                                        i = i+1
                                                        newName = storeName.split('.')[0]+str(i)+'.'+storeName.split('.')[1]
                                        else:
                                                storeName = newName
                                                sf = open('data/rfi/'+storeName,"w+")
                                                sf.write(f)
                                                sf.close()
                                                logger.info( "stored file")
                else:        
                        sf = open('data/rfi/'+storeName,"w+")
                        sf.write(f)
                        sf.close()
                        logger.info( "stored file")
        except:
                f=-1
                storeName = ''
                logger.info( "error is getting/storing file")
        #if wrong filename is used, rfi shouldn't occur
        filename = url.split('?')[0]
        if filename[1:] != 'index.php':
                path = filename[1:]
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
                if validPath:
                        rh.send_response(200)
                        rh.set_header()
                        reqFile = os.getcwd()+"/www"+filename
                        fo = open(reqFile,'rb')
                        f = fo.read()
                        rh.wfile.write(f)
                        fo.close()
                else:
                        logger.warning("failed validation for "+filename)
                        rh.send_response(404)
                return storeName
	#run the file obtained on the php executable
        additive = ''
        if f!=-1:
                try:
                        for st in ['stream_socket_client']:
                                if st in f:
                                        break
                        else:
                                logger.info( "executing php script")
                                process = subprocess.Popen([phpLocation,'data/rfi/'+storeName],shell=True, stdout=subprocess.PIPE)#,stderr=subprocess.PIPE)
                                out, err = process.communicate()
                                logger.info( "parsed output is " + out)
                                additive = out
                                
                except:
                        pass
                        
	#provide suitable reply to attacker
        logger.info("sending reply")
	filename = url.split('?')[0]
	path = filename[1:]
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
	if validPath:
		rh.send_response(200)
		rh.set_header()
		reqFile = os.getcwd()+"/www"+filename
		fo = open(reqFile,'rb')
		f = fo.read()
		pos = f.find('<head>')
		rh.wfile.write(f[:pos+6]+'\n'+additive+f[pos+6:])
		fo.close()
	else:
                logger.warning("failed validation for "+filename)
                rh.send_response(404)
        return storeName

def lfi(requestHandler):
        logger.info( "entered lfi handler")
	rh = requestHandler
	url = rh.path
	
	#find starting of the required link
	s = url.find('../')
        link = url[s:]
        e = link.find('&')
        
        #set the link
        if e != -1:
                link = link[:e]
        x = link.rfind('../')
	localFileName = link[x+2:]

	#check if localFileName is the correct file and correct number of '../' are used
        filename = url.split('?')[0]
	if filename[1:] != "about.php" or link.count('../')!=2:
                logger.info( "incorrect file for lfi output")
                #print filename,link.count('../')
                path = filename[1:]
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
                if validPath:
                        rh.send_response(200)
                        rh.set_header()
                        reqFile = os.getcwd()+"/www"+filename
                        fo = open(reqFile,'rb')
                        f = fo.read()
                        rh.wfile.write(f)
                        fo.close()
                else:
                        logger.warning("failed validation for "+filename)
                        rh.send_response(404)
                return localFileName

        #for exact matches, try to find file and perform neccessary things
	if os.path.isfile('vfs/'+localFileName):
                f = open('vfs/'+localFileName)
                additive = f.read()
                f.close()
                logger.info( "local file found, emulating output")
        else:
                additive = ''
                logger.info( "local file not found, ignoring output")

        filename = url.split('?')[0]
        path = filename[1:]
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
	if validPath:
		rh.send_response(200)
		rh.set_header()
		reqFile = os.getcwd()+"/www"+filename
		fo = open(reqFile,'rb')
		f = fo.read()
		pos = f.find("<div id='data'>")
		rh.wfile.write(f[:pos+15]+'\n'+additive+f[pos+15:])
		fo.close()
	else:
                logger.warning("failed validation for "+filename)
                rh.send_response(404)
        return localFileName

def xss(requestHandler):
        logger.info( "entered xss")
	rh = requestHandler
	url = rh.path

	#find starting of xss code
	s = url.find('<script>')
	link = url[s:]
	e = link.rfind('</script>')
	code = link[:e+9]

	#Filter code for dangerous inputs
	filename = url.split('?')[0]
	if code.find('cookie') != -1 or code.find('http') != -1 or filename[1:]!='about.php':
                path = filename[1:]
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
                if validPath:
                        rh.send_response(200)
                        rh.set_header()
                        reqFile = os.getcwd()+"/www"+filename
                        fo = open(reqFile,'rb')
                        f = fo.read()
                        rh.wfile.write(f)
                        fo.close()
                else:
                        logger.warning("failed validation for "+filename)
                        rh.send_response(404)
                return code

        #if code is reasonably simple, inject it provided that its the correct file
        rh.send_response(200)
        rh.set_header()
        reqFile = os.getcwd()+"/www"+filename
        fo = open(reqFile,'rb')
        f = fo.read()
        pos = f.find("<div id='head'>")
        rh.wfile.write(f[:pos+15]+code+f[pos+15:])
        fo.close()

def sql(requestHandler):
        rh = requestHandler
        url = rh.path

        #extrac file name 
        filename = url.split('?')
        filename = filename[0]

        #check if correct file is being exploited
        if filename[1:] != 'login.php':
                path = filename[1:]
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
                if validPath:
                        rh.send_response(200)
                        rh.set_header()
                        reqFile = os.getcwd()+"/www"+filename
                        fo = open(reqFile,'rb')
                        f = fo.read()
                        rh.wfile.write(f)
                        fo.close()
                else:
                        logger.warning("failed validation for "+filename)
                        rh.send_response(404)
                login = rh.fields['login']
                login = login[0]
                password = rh.fields['password']
                password = password[0]
                retString = "login:'"+login+"' password:'"+password+"'"
                return retString
        
        #if correct file is exploited, we will now respond
        login = rh.fields['login']
        login = login[0]
        responseMessage = "Invalid query: You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near '"+login+"' at line 1"
        #For MongoDB "Error: couldn't connect to server 127.0.0.1:27017, connection attempt failed :\nconnect@src/mongo/shell/mongo.js:229:14"
        rh.send_response(200)
        rh.set_header()
        reqFile = os.getcwd()+"/www"+filename
        fo = open(reqFile,'rb')
        f = fo.read()
        pos = f.find('<head>')
        rh.wfile.write(f[:pos+6]+'\n'+responseMessage+f[pos+6:])
        fo.close()
        logger.info("Post variables: "+str(rh.fields))
        password = rh.fields['password']
        password = password[0]
        retString = "login:'"+login+"' password:'"+password+"'"
        return retString
