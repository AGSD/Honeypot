from time import gmtime, strftime
import os

def saveRecord(handler,requestType,special=''):
    now = strftime("%Y-%m-%d %H:%M:%S",gmtime())
    recString = ['"timestamp": """'+str(now)+'""", ']
    recString.append('"type": """'+requestType+'""", ')
    if special:
        recString.append('"special": """'+special+'""", ')
    recString.append('"clientIP": """'+str(handler.client_address[0])+'""", ')
    recString.append('"clientPort": """'+str(handler.client_address[1])+'""", ')
    recString.append('"command": """'+str(handler.command)+'""", ')
    recString.append('"path": """'+str(handler.path)+'""", ')
    recString.append('"version": """'+str(handler.request_version)+'""", ')
    h = str(handler.headers)
    l = h.split('\n')
    for s in l:
        rec = s.strip()
        pos = rec.find(':')
        st = '"'+rec[:pos]+'": """'+rec[pos+1:]+'""", '
        recString.append(st)
    f = open(os.getcwd()+"/data/db.txt","a+")
    f.write('{')
    for s in recString:
        f.write(str(s))
    f.write('}')
    f.write('\n')
    f.close()
