import pickle,socket,os,sys,html
from translate.storage.tmx import tmxfile
from Levenshtein import distance as lev
ftmx="outtmx2"
log=False
if len(sys.argv)>1:
    if sys.argv[1]=="--log":
        log=True
        
HEADER = 4096
hostn=socket.gethostname()
IP = socket.gethostbyname(hostn)
PORT = 2022
keeperoftheloop=True
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
#server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP,PORT))
    server_socket.listen()
    try:
        while keeperoftheloop:
            client_socket, client_address = server_socket.accept()
            with client_socket:
                if log:
                    print(f"Connected by {client_address}")
                while True:
                    try:
                        instr = client_socket.recv(HEADER)
                        if not instr:
                            break
                        if log:
	                        print("richiesto:",instr)
                        message = pickle.loads(instr)
                        if log:
                        	print(message)
                        	print(type(message))
                        suggerimenti=[]
                        if message==[None]:
                            suggerimenti.append(None)
                            packsug=pickle.dumps(suggerimenti,protocol=2)
                            client_socket.sendall(packsug)
                            keeperoftheloop=False
                            break
                        elif message[0][0]==None:
                                print("adding source: "+message[0][1]+"\nand translation: "+message[0][2])
                                with open(ftmx, 'rb') as fin:
                                    with open("outtmx3", 'a') as des:
                                        whole=fin.read()
                                        liniis=whole.decode("utf-8").split('\n')
                                        for linie in liniis:
                                            if "</body>" not in str(linie):
                                            #if str(linie).find("</body>")==-1:
                                                des.write(str(linie)+"\n")
                                            else:
                                                msgid=html.escape(message[0][1])
                                                msgstr=html.escape(message[0][2])
                                                des.write("    <tu>\n      <tuv xml:lang=\"en\">\n        <seg>"+msgid+"</seg>\n      </tuv>\n")
                                                des.write("      <tuv xml:lang=\"fur\">\n        <seg>"+msgstr+"</seg>\n      </tuv>\n    </tu>\n")
                                                des.write("  </body>\n</tmx>\n")
                                                des.close()
                                                if os.path.exists("old_outtmx2"):
                                                    os.remove("old_outtmx2")
                                                os.rename(ftmx,"old_outtmx2")
                                                os.rename("outtmx3",ftmx)
                                                break
                                break
                        elif message[0][0]==('d','e','l'):
                                with open(ftmx, 'r', encoding='utf-8') as fin, open("outtmx3", 'a', encoding='utf-8') as des:
                                        whole=fin.read()
                                        liniis=whole.split('\n')
                                        nl=len(liniis)
                                        i=0
                                        while i<nl:
                                            if '<tu>' not in str(liniis[i]):
                                                des.write(str(liniis[i])+"\n")
                                            else:
                                                k=1
                                                nextclose=False
                                                txt=str(liniis[i])+"\n"
                                                if 'tuv xml:lang="en"' in  str(liniis[i + k]):
                                                #if str(liniis[i+k]).find("tuv xml:lang=\"en\"")>-1:
                                                    txt+=str(liniis[i+k])+"\n"
                                                    while True:
                                                        k+=1
                                                        txt+=str(liniis[i+k])+"\n"
                                                        if '<tuv xml:lang="fur">' in str(liniis[i+k]):
                                                        #if str(liniis[i+k]).find("<tuv xml:lang=\"fur\">")>-1:
                                                            nextclose=True
                                                        if nextclose:
                                                            if '</seg>' in str(liniis[i+k]):
                                                            #if str(liniis[i+k]).find("</seg>")>-1:
                                                                k+=1
                                                                txt+=str(liniis[i+k])+"\n" #this adds /tuv
                                                                txt+=str(liniis[i+k+1])+"\n" #this add /tu
                                                                break
                                                    #if (txt.find("<seg>"+message[0][1]+"</seg>")>-1) and (txt.find("<seg>"+message[0][2]+"</seg>")>-1):
                                                    msgid=html.escape(message[0][1])
                                                    msgstr=html.escape(message[0][2])
                                                    if "<seg>"+msgid+"</seg>" in txt and "<seg>"+msgstr+"</seg>" in txt:
                                                        i+=k+1
                                                    else:
                                                        des.write(txt)
                                                        #for rie in txt:
                                                        #    des.write(rie)
                                                        i+=k+1
                                            i+=1
                                    #des.close()
                                if os.path.exists("old_outtmx2"):
                                     os.remove("old_outtmx2")
                                os.rename(ftmx,"old_outtmx2")
                                os.rename("outtmx3",ftmx)
                                break
                        else:
                            lung1=len(message[0])
                            lung2=round(lung1*0.75,0)
                            delta=lung1-lung2+1
                            with open(ftmx, 'rb') as fin:
                                tmx_file = tmxfile(fin, "en", "fur")
                                for node in tmx_file.unit_iter():
                                    dist=lev(message[0],node.source)
                                    if dist<delta:#2
                                        suggerimenti.append((node.target,dist))
                            suggerimenti.sort(key=lambda element:element[1])
                            client_socket.send(pickle.dumps(suggerimenti,protocol=2))
                    except FileNotFoundError as e:
                        with open(ftmx, 'a') as des:
                            des.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<!DOCTYPE tmx SYSTEM \"tmx14.dtd\">\n<tmx version=\"1.4\">\n  <header creationtool=\"Translate Toolkit\" creationtoolversion=\"3.8.0\" segtype=\"sentence\" o-tmf=\"UTF-8\" adminlang=\"en\" srclang=\"en\" datatype=\"PlainText\"/>\n  <body>\n")
                            des.write("  </body>\n</tmx>\n")
    except KeyboardInterrupt:
        server_socket.close()
        print("interrotto dall'utente")
