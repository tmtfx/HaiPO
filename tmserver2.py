#!/boot/system/bin/python3
import os
import sqlite3
import socket
import pickle
import html
import argparse
from Levenshtein import distance as lev

from Be.FindDirectory import *
from Be.Directory import create_directory
from Be import BDirectory,BEntry,BPath

def initialize_db(db_path):
    """Crea la tabella della memoria di traduzione se non esiste."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS translation_units (
            source TEXT NOT NULL,
            target TEXT NOT NULL,
            UNIQUE(source, target)
        );
    """)
    conn.commit()
    conn.close()
    return db_path
   
perc=BPath()
find_directory(directory_which.B_USER_NONPACKAGED_DATA_DIRECTORY,perc,False,None)
ent=BEntry(perc.Path()+"/HaiPO2")
pth=BPath()
ent.GetPath(pth)
if ent.Exists() and ent.IsDirectory():
	pass
else:
	create_directory(pth.Path(),0o777)
DATA_DIR = pth.Path()
print("Datadir",DATA_DIR)
DB_PATH_TEMPLATE=os.path.join(DATA_DIR, 'outtmx_{}.db')

class TMSearchServer:
    def __init__(self, tmxlang, log=False):
        # Inizializzazione della classe con le impostazioni base
        self.tmxlang = tmxlang
        self.log = log
        self.db_path = DB_PATH_TEMPLATE.format(self.tmxlang)
        
       	print("Template:",self.db_path)
        self.keeperoftheloop = True
        
        # Assicura che la directory esista e inizializza il database
        #os.makedirs(DATA_DIR, exist_ok=True) già fatto prima
        initialize_db(self.db_path)
        
        if self.log:
            self.flog = os.path.join(DATA_DIR, 'log.txt')
            with open(self.flog, 'a') as des:
                des.write("Server initialized and DB ready.\n")

    def log_message(self, message):
        """Scrive un messaggio nel file di log se il logging è attivo."""
        if self.log:
            with open(self.flog, 'a') as des:
                des.write(f"{message}\n")

    def handle_request(self, message, db_conn):
        """
        Elabora la richiesta dal client, rispettando il formato di messaggio originale.
        Il messaggio è sempre una lista.
        """
        self.log_message(f"Processing message with type: {type(message)}")
        
        # --- 1. Richiesta di Chiusura: message == [None] ---
        if message == [None]:
            self.keeperoftheloop = False
            self.log_message("Received shutdown request ([None]).")
            # Nel codice originale restituisci [None] come suggerimento
            return [None]

        # Assumiamo che il messaggio sia una lista contenente almeno un elemento
        if not isinstance(message, list) or not message:
             self.log_message("Invalid message format (not a list or empty).")
             return []

        first_element = message[0]
        
        # --- 2. Richiesta di Aggiunta (ADD): message[0] == (None, source, target) ---
        if isinstance(first_element, tuple) and len(first_element) == 3 and first_element[0] is None:
            # Il tuo codice originale: elif message[0][0]==None:
            source = first_element[1].strip()
            target = first_element[2].strip()
            
            if source and target:
                try:
                    cursor = db_conn.cursor()
                    # Inserisce solo se la coppia non esiste già.
                    # Nota: il codice originale usava html.escape, che qui non è necessario 
                    # grazie a SQLite, ma lo manteniamo per fedeltà concettuale.
                    cursor.execute("INSERT OR IGNORE INTO translation_units (source, target) VALUES (?, ?)", 
                                   (html.escape(source), html.escape(target)))
                    db_conn.commit()
                    self.log_message(f"Added entry: {source} -> {target}")
                    return [] # Non si aspettava un suggerimento, quindi ritorna una lista vuota o None
                except Exception as e:
                    self.log_message(f"Error adding entry: {e}")
                    return []
            self.log_message("Error: Source or target is empty for ADD.")
            return []

        # --- 3. Richiesta di Cambiamento (CHG): message[0] == ('c', 'h', 'g') ---
        elif first_element == ('c', 'h', 'g'):
            # Il tuo codice originale: elif message[0][0]==('c','h','g'):
            self.log_message("Received Change request (c,h,g). Action ignored (paths re-read).")
            # Nel codice originale, questa azione ricarica i percorsi dei file. 
            # Qui non è necessario dato che usiamo un path fisso per SQLite.
            return []

        # --- 4. Richiesta di Eliminazione (DELETE): message[0] == ('d', 'e', 'l') ---
        # Si ipotizza che il formato sia: [('d', 'e', 'l'), source_text, target_text]
        elif first_element == ('d', 'e', 'l'):
            # Il tuo codice originale: elif message[0][0]==('d','e','l'):
            if len(message) < 3:
                self.log_message("Error: DELETE format incomplete.")
                return []
                
            source_to_delete = message[1].strip()
            target_to_delete = message[2].strip()

            try:
                cursor = db_conn.cursor()
                # Usiamo html.escape per trovare le entry memorizzate con l'escape
                cursor.execute("DELETE FROM translation_units WHERE source = ? AND target = ?", 
                               (html.escape(source_to_delete), html.escape(target_to_delete)))
                db_conn.commit()
                self.log_message(f"Deleted entry: {source_to_delete} -> {target_to_delete}. Rows affected: {cursor.rowcount}")
                return []
            except Exception as e:
                self.log_message(f"Error deleting entry: {e}")
                return []

        # --- 5. Richiesta di Ricerca (SEARCH): message == [source_text] (la stringa è il primo elemento) ---
        elif isinstance(first_element, str):
            # Il tuo codice originale: else: (si assume che sia una richiesta di ricerca)
            search_text = first_element
            if not search_text:
                return []
            
            suggestions = []
            
            # Calcola la soglia di tolleranza (delta) come nel tuo codice originale
            lung1 = len(search_text)
            # lung2=round(lung1*0.75,0) -> 0.75 di match significa 0.25 di differenza tollerata
            delta = int(lung1 * 0.25) + 1 
            
            try:
                # Recupera TUTTE le unità di traduzione per la ricerca (veloce con SQLite)
                cursor = db_conn.cursor()
                cursor.execute("SELECT source, target FROM translation_units")
                all_units = cursor.fetchall()

                # Esegue la distanza di Levenshtein (lev) in memoria
                for source, target in all_units:
                    # Rimuoviamo l'escape prima del calcolo se è stato applicato in fase di salvataggio
                    dist = lev(search_text, html.unescape(source)) 
                    if dist < delta:
                        # Restituisce la traduzione (target) e la distanza
                        suggestions.append((html.unescape(target), dist))
                
                # Ordina e restituisce
                suggestions.sort(key=lambda element: element[1])
                self.log_message(f"Search found {len(suggestions)} suggestions.")
                return suggestions
            except Exception as e:
                self.log_message(f"Error during search: {e}")
                return []

        # --- 6. Formato Sconosciuto ---
        else:
             self.log_message(f"Unknown message format: {message}")
             return []

    def server(self, addr, PORT=2022, HEADER=4096):
        """Funzione principale per l'esecuzione del server."""
        IP = socket.gethostbyname(addr)
        
        # Connessione persistente al database durante il ciclo di vita del server
        db_conn = sqlite3.connect(self.db_path)

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
                server_socket.bind((IP, PORT))
                server_socket.listen()
                self.log_message(f"Server listening on {IP}:{PORT}")

                while self.keeperoftheloop:
                    try:
                        client_socket, client_address = server_socket.accept()
                        self.log_message(f"Connected by {client_address}")

                        with client_socket:
                            while True:
                                instr = client_socket.recv(HEADER)
                                if not instr:
                                    break # Client disconnesso

                                message = pickle.loads(instr)
                                
                                # Elabora la richiesta con il db_conn aperto
                                response = self.handle_request(message, db_conn)
                                
                                # Invia la risposta al client
                                packsug = pickle.dumps(response, protocol=2)
                                client_socket.sendall(packsug)
                                
                                # Se l'azione era [None], usciamo dal loop
                                if message == [None]:
                                    break 

                    except socket.timeout:
                        continue 
                    except Exception as e:
                        self.log_message(f"Error in client connection loop: {e}")
                        break 
                self.log_message("Server stopping loop...")

        except OSError as e:
            if e.errno == 98: 
                print("Server instance not started\nprobably another one already running...")
            else:
                self.log_message(f"OS Error: {e}")
        except KeyboardInterrupt:
            print("Aborted by user")
        finally:
            db_conn.close()
            print("Server closed")
            
def main():
    # 1. Configurazione degli argomenti da riga di comando
    parser = argparse.ArgumentParser(description="Translation Memory Server standalone.")
    parser.add_argument('lang', type=str, 
                        help="Il codice della lingua di destinazione (es. 'it', 'fr', 'fur').")
    parser.add_argument('--port', type=int, default=2022, 
                        help="La porta su cui il server ascolterà (default: 2022).")
    parser.add_argument('--addr', type=str, default='127.0.0.1', 
                        help="L'indirizzo IP su cui il server ascolterà (default: 127.0.0.1 per locale).")
    parser.add_argument('--log', action='store_true', 
                        help="Abilita la scrittura di log su file (log.txt).")
    
    args = parser.parse_args()

    # 2. Creazione dell'istanza del server
    print(f"Server TM in avvio per lingua: {args.lang}")
    server_instance = TMSearchServer(tmxlang=args.lang, log=args.log)

    # 3. Avvio del server
    try:
        server_instance.server(addr=args.addr, PORT=args.port)
    except Exception as e:
        print(f"Errore critico durante l'esecuzione del server: {e}")

if __name__ == "__main__":
    main()
