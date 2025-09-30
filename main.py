# === IMPORT ===
# Funzioni .json
import json
# Variabile per le Date
from datetime import datetime

# === GESTIONE ===
class LibroNonTrovatoError(Exception):
    # Errore quando un libro non viene trovato
    pass

class LibroGiaEsistenteError(Exception):
    # Errore quando si tenta di aggiungere un libro già esistente
    pass

# === COSTANTI ===
SEPARATORE = "=" * 20

# === FUNZIONI === 
# Aggiungi libro al database
def aggiungi_libro(data):
    try:
        # Input e aggiunta genere se nuovo
        genere = validazione_input("inserire il genere del libro: ")
        if genere.lower() not in data["generi"]:
            data["generi"].append(genere)

        # Input e controllo ID
        id_libro = genera_id(data)
        if id_libro in data["libri"]:
            raise LibroGiaEsistenteError("Esiste già un libro con quell'id")

        # Input e controllo titolo
        titolo = validazione_input("inserire il titolo del libro: ")
        for libro in data["libri"].values():
            if libro["titolo"].lower() == titolo.lower() and libro["genere"].lower() == genere.lower():
                raise LibroGiaEsistenteError("Esiste già un libro con quel titolo in questo genere")

        autore = validazione_input("inserire l'autore del libro: ")
        while True:
            anno = input("inserire l'anno di pubblicazione del libro: ")
            if valida_anno(anno): break
            print("Anno non valido, deve essere tra 1000 e 2025")
        
        # Aggiunge libro
        data["libri"][id_libro] = {
            "titolo": titolo, "autore": autore, "anno": anno,  "genere": genere, "disponibile": True,  "prestiti": []
        }
        
        # Aggiorna statistiche
        data["statistiche"]["totale_libri"] = len(data["libri"])
        data["statistiche"]["libri_disponibili"] += 1
        print(f"Libro aggiunto: '{titolo}' di {autore}")

    except LibroGiaEsistenteError as e: print(f"Errore: {e}")
    except Exception as e: print(f"Errore imprevisto: {e}")

# Elimina un libro dal database
def elimina_libro(data):
    try:
        # Input e controllo ID
        id_libro = validazione_input("Inserire l'id del libro: ")
        if id_libro not in data["libri"]:
            raise LibroNonTrovatoError("Non esiste un libro con quell'id")

        # Conferma e Cancellazione
        print(f"Eliminare '{data['libri'][id_libro]['titolo']}'?")
        if validazione_input("si/no") == "si":
            # Aggiorna statistiche
            if data["libri"][id_libro]["disponibile"]:
                data["statistiche"]["libri_disponibili"] -= 1
            data["statistiche"]["totale_libri"] -= 1
            
            print("Libro eliminato dal database")
            del data["libri"][id_libro]
        else: pass

    except LibroNonTrovatoError as e: print(f"Errore: {e}")
    except Exception as e: print(f"Errore imprevisto: {e}")

# Cerca i libri scritti da un'autore
def cerca_libro_per_autore(data):
    try:
        autore = validazione_input("Inserire l'autore del libro: ")
        # List Comprehension per trovare id e info libro di ogni libro scritto da quell autore
        libri_trovati = [{"id": id_libro, **info_libro}
                        for id_libro, info_libro in data["libri"].items()
                        if autore.lower() in info_libro["autore"].lower()]

        # Output
        if libri_trovati:
            print(f"Libri di {autore}:")
            for libro in libri_trovati:
                stato = "Disponibile" if libro["disponibile"] else "In prestito"
                print(f"  ID {libro['id']}: {libro['titolo']} ({libro['anno']}) - {stato}")
        else:
            print(f"Nessun libro trovato per: {autore}")

    except Exception as e: print(f"Errore: {e}")

# Cerca tutti i libri disponibili attualmente
def libri_disponibili(data):
    try:
        # List Comprehension per trovare id e info libro di ogni libro disponibile
        libri_trovati = [{"id": id_libro, **info_libro}
                for id_libro, info_libro in data["libri"].items()
                    if info_libro["disponibile"] == True]

        # Output
        if libri_trovati:
            print("I libri disponibili sono:")
            for libro in libri_trovati:
                stato = "Disponibile" if libro["disponibile"] else "In prestito"
                print(f"  ID {libro['id']}: {libro['titolo']} ({libro['anno']}) - {stato}")
        else:
            print("Non ci sono libri disponibili.")

    except Exception as e: print(f"Errore: {e}")

# Modifica dati dopo un prestito
def prestito_libro(data):
    try:
        # Input e controllo ID
        id_libro = validazione_input("inserire l'id del libro: ")
        if id_libro not in data["libri"]:
            raise LibroNonTrovatoError("Non esiste un libro con quell'id")

        # Controllo se il libro è disponibile
        if not data["libri"][id_libro]["disponibile"]:
            print("Il libro non è disponibile")
            return

        # Registra prestito
        nome_persona = validazione_input("inserire il nome della persona: ")
        data["libri"][id_libro]["disponibile"] = False
        data_prestito = datetime.now().strftime("%Y-%m-%d")
        data["libri"][id_libro]["prestiti"].append({
            "nome": nome_persona,
            "data_prestito": data_prestito
        })
        
        # Aggiorna statistiche
        data["statistiche"]["libri_disponibili"] -= 1
        print("Prestito registrato!")
        
    except LibroNonTrovatoError as e: print(f"Errore: {e}")
    except Exception as e: print(f"Errore imprevisto: {e}")

# Modifica dati dopo un ritorno
def ritorno_libro(data):
    try:
        # Input e controllo ID
        id_libro = validazione_input("inserire l'id del libro: ")
        if id_libro not in data["libri"]:
            raise LibroNonTrovatoError("Non esiste un libro con quell'id")

        # Controllo se il libro è disponibile
        if data["libri"][id_libro]["disponibile"]:
            print("Il libro è già disponibile")
            return

        # Registra ritorno
        data["libri"][id_libro]["disponibile"] = True
        
        # Aggiorna statistiche
        data["statistiche"]["libri_disponibili"] += 1
        print("Ritorno registrato!")

    except LibroNonTrovatoError as e: print(f"Errore: {e}")
    except Exception as e: print(f"Errore imprevisto: {e}")

# Salva i dati nel file .json
def salva_dati(data, **kwargs):
    try:
        # Parametri opzionali
        filename = kwargs.get('filename', 'biblioteca.json')
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Dati salvati in {filename}")
    
    except Exception as e: print(f"Errore: {e}")

# Genera ID unico
def genera_id(data):
    if not data["libri"]: return "1"
    # Trova il numero di ID e aggiungi 1
    n_id = max([int(id_) for id_ in data["libri"].keys()])
    return str(n_id + 1)

# Validazione Input
def validazione_input(messaggio):
    while True:
        valore = input(messaggio).strip()
        if valore:
            return valore
        print("Il campo non può essere vuoto!")

# Validazione Anno
def valida_anno(anno):
    # True se si trova tra i 2 anni messi
    try: return 1000 <= int(anno) <= 2025
    except ValueError: return False

# === MAIN ===
def main():
    # Carica il file biblioteca.json
    try:
        with open('biblioteca.json', 'r', encoding='utf-8') as file:
            data = json.load(file)

    except FileNotFoundError:
        print("Errore: File biblioteca.json non trovato!")
        exit()
    except json.JSONDecodeError:
        print("Errore: File JSON corrotto!")
        exit()

    print("=" * 20)
    print("Gestione di una Biblioteca .json")

    while True:
        try:
            print("=" * 20)
            print("MENU'")
            print("1. Visualizza tutti i libri, 2. Aggiungi libro, 3. Elimina libro, 4. Cerca libro per Autore")
            print("5. Visualizza libri attualmente disponibili, 6. Registra prestito, 7. Registra ritorno, 8. Salva dati, 9. Esci")
            scelta = input("cosa vuoi fare?: ")

            match scelta:
                case "1": 
                    print(SEPARATORE)
                    print(data)
                case "2": 
                    print(SEPARATORE)
                    aggiungi_libro(data)
                case "3": 
                    print(SEPARATORE)
                    elimina_libro(data)
                case "4": 
                    print(SEPARATORE)
                    cerca_libro_per_autore(data)
                case "5": 
                    print(SEPARATORE)
                    libri_disponibili(data)
                case "6": 
                    print(SEPARATORE)
                    prestito_libro(data)
                case "7": 
                    print(SEPARATORE)
                    ritorno_libro(data)
                case "8": 
                    print(SEPARATORE)
                    salva_dati(data)
                case "9": 
                    print(SEPARATORE)
                    print("Grazie per aver usato il mio programma -Michele")
                    break
                case _:
                    print("Scelta non valida! Inserire un numero da 1 a 9")

        except Exception as e: print(f"Errore imprevisto: {e}")

if __name__ == '__main__':
    main()