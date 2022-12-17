import pickle,socket
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
                    print("richiesto:",instr)
                    message = pickle.loads(instr)
                    suggerimenti=[]
                    if message==[None]:
                        suggerimenti.append(None)
                        packsug=pickle.dumps(suggerimenti,protocol=2)
                        client_socket.sendall(packsug)
                        keeperoftheloop=False
                        break
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
