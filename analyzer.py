import re

def analyzeRequest(handler,method):
        getPatterns = {
                'rfi' : '.*(php(3){0,1}\?){0,1}.*(=.*(http(s){0,1}|ftp(s){0,1}):).*',
                'lfi' : '.*php(3){0,1}\?.*=(\.\./)+(home|conf|usr|etc|proc|opt|s?bin|local|dev|tmp|kern|root|sys|system|windows|winnt|program|inetpub/boot\.ini).*',
                'xss' : '.*script.*(alert|eval|msgbox|showmodaldialog|prompt|write|confirm|dialog|open|src).*/script.*',
                'phpcodeinjection' : '.*(define|eval|file_get_contents|include|require|require_once|set|shell_exec|phpinfo|system|passthru|preg_|execute|echo|print|print_r|var_dump|[fp]open)\(.*',
                'html': '.*<(frame|applet|isindex|marquee|keygen|audio|video|input|button|textarea|style|base|body|meta|link|object|embed|param|plaintext|xml|image|div).*',
                'robots':'^/robots\.txt$'
        }
        postPatterns = {
                'sql' : '.*(select|drop|update|union|insert|alter|declare|cast)( |\().*'
        }
        uri = handler.path
        if method=="GET":
                for t,string in getPatterns.iteritems():
                        expression = re.compile(string,re.I)
                        match = expression.search(uri)
                        if match:
                                print t
                                return t
        elif method=="POST":
                for t,string in postPatterns.iteritems():
                        expression = re.compile(string,re.I)
                        for var in handler.fields:
                                match = expression.search(handler.fields[var][0])
                                copy = handler.fields[var][0]
                                for ch in ['@','#','_','$']:
                                        if ch in copy:
                                                copy = copy.replace(ch,'a')
                                if match or not copy.isalnum():
                                        print t
                                        return t
        else:
                pass

        print "normal"
        return "normal"
