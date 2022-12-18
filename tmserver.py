import pickle,socket,os
from translate.storage.tmx import tmxfile
from Levenshtein import distance as lev

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
                print(f"Connected by {client_address}")
                while True:
                    instr = client_socket.recv(HEADER)
                    if not instr:
                        break
                    #print("richiesto:",instr)
                    message = pickle.loads(instr)
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
                                            if str(linie).find("</body>")==-1:
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
                        #except:
                        #    pass
                    #elif message==[alc]:
                    #    aggiungi a tmx il termine e la traduzione
                    lung1=len(message[0])
                    print(lung1)
                    lung2=round(lung1*0.75,0)
                    print(lung2)
                    delta=lung1-lung2+1
                    print("delta:",delta)
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
