import pickle,socket,os,sys
from translate.storage.tmx import tmxfile
from Levenshtein import distance as lev
log=False
if len(sys.argv)>1:
    if sys.argv[1]=="--log":
        log=True
        
HEADER = 4096
hostn=socket.gethostname()
IP = socket.gethostbyname(hostn)#'127.0.0.1'
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
                    instr = client_socket.recv(HEADER)
                    if not instr:
                        break
                    #print("richiesto:",instr)
                    message = pickle.loads(instr)
                    #print("Decodificato:",message)
                    #print("message[0]:",message[0])
                    #print(message)
                    #print(type(message))
                    suggerimenti=[]
                    if message==[None]:
                        suggerimenti.append(None)
                        packsug=pickle.dumps(suggerimenti,protocol=2)
                        client_socket.sendall(packsug)
                        keeperoftheloop=False
                        break
                    else:
                            
                        #try:
                        if message[0][0]==None:
                                print("adding source: "+message[0][1]+"\nand translation: "+message[0][2])
                                with open("outtmx2", 'rb') as fin:
                                    with open("outtmx3", 'a') as des:
                                        whole=fin.read()
                                        liniis=whole.decode("utf-8").split('\n')
                                        for linie in liniis:
                                            #print(str(linie))
                                            if "</body>" not in str(linie):
                                            #if str(linie).find("</body>")==-1:
                                                des.write(str(linie)+"\n")
                                            else:
                                                des.write("    <tu>\n      <tuv xml:lang=\"en\">\n        <seg>"+message[0][1]+"</seg>\n      </tuv>\n")
                                                des.write("      <tuv xml:lang=\"fur\">\n        <seg>"+message[0][2]+"</seg>\n      </tuv>\n    </tu>\n")
                                                des.write("  </body>\n</tmx>\n")
                                                #addnewstrings(message[0][1],message[0][2])
                                                des.close()
                                                if os.path.exists("old_outtmx2"):
                                                    os.remove("old_outtmx2")
                                                os.rename("outtmx2","old_outtmx2")
                                                os.rename("outtmx3","outtmx2")
                                                break
                                break
                        elif message[0][0]==('d','e','l'):
                            with open("outtmx2", 'r', encoding='utf-8') as fin, open("outtmx3", 'a', encoding='utf-8') as des:
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
                                                    if "<seg>"+message[0][1]+"</seg>" in txt and "<seg>"+message[0][2]+"</seg>" in txt:
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
                            os.rename("outtmx2","old_outtmx2")
                            os.rename("outtmx3","outtmx2")
                            break
                        #except:
                        #    pass
                    #elif message==[alc]:
                    #    aggiungi a tmx il termine e la traduzione
                    lung1=len(message[0])
                    #print(lung1)
                    lung2=round(lung1*0.75,0)
                    #print(lung2)
                    delta=lung1-lung2+1
                    #print("delta:",delta)
                    #elif message == [ 2079460347 ]:
                    #    keeperoftheloop=False
                    #    break
                    #controllare grandezza messaggio (4096)
                    with open("outtmx2", 'rb') as fin:
                        tmx_file = tmxfile(fin, "en", "fur")
                        for node in tmx_file.unit_iter():
                            dist=lev(message[0],node.source)
                            if dist<delta:#2
                                suggerimenti.append((node.target,dist))
                                #print(node.source,node.target)
                    suggerimenti.sort(key=lambda element:element[1])
                    packsug=pickle.dumps(suggerimenti,protocol=2)
                    client_socket.sendall(packsug)
    except KeyboardInterrupt:
        server_socket.close()
        print("interrotto dall'utente")
