
import sqlite3
import csv
from typing import List, Dict, Optional, Tuple

DATABASE_NAME = 'fantacale.db'

def get_connection():
    """Crea connessione al database"""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Inizializza il database con lo schema corretto"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS calciatori (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Nome TEXT NOT NULL,
            Squadra TEXT,
            Ruolo TEXT,
            Ruolo_Dettaglio TEXT,
            Fuori_lista INTEGER DEFAULT 0,
            Tiratore_CP INTEGER DEFAULT 0,
            Media_Voto REAL,
            FantaMedia REAL,
            FantaMedia_Prevista REAL,
            Titolarita INTEGER,
            Prezzo INTEGER,
            Obiettivo INTEGER DEFAULT 0,
            Nota TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database inizializzato con successo!")

def import_from_csv(csv_path: str):
    """Importa dati da CSV con gestione corretta dei booleani"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Svuota la tabella esistente
    cursor.execute('DELETE FROM calciatori')
    
    with open(csv_path, 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        
        for row in csv_reader:
            # Gestione booleani: vuoto/None/0 -> 0, altrimenti -> 1
            fuori_lista = 1 if row.get('Fuori_lista', '').strip() in ['1', 'True', 'true'] else 0
            tiratore_cp = 1 if row.get('Tiratore_CP', '').strip() in ['1', 'True', 'true'] else 0
            obiettivo = 1 if row.get('Obiettivo', '').strip() in ['1', 'True', 'true'] else 0
            
            # Gestione valori numerici vuoti
            def parse_float(val):
                return float(val) if val and val.strip() else None
            
            def parse_int(val):
                return int(val) if val and val.strip() else None
            
            cursor.execute('''
                INSERT INTO calciatori (
                    Nome, Squadra, Ruolo, Ruolo_Dettaglio, Fuori_lista, 
                    Tiratore_CP, Media_Voto, FantaMedia, FantaMedia_Prevista, 
                    Titolarita, Prezzo, Obiettivo, Nota
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                row['Nome'],
                row['Squadra'],
                row['Ruolo'],
                row['Ruolo_Dettaglio'],
                fuori_lista,
                tiratore_cp,
                parse_float(row.get('Media_Voto')),
                parse_float(row.get('FantaMedia')),
                parse_float(row.get('FantaMedia_Prevista')),
                parse_int(row.get('Titolarita')),
                parse_int(row.get('Prezzo')),
                obiettivo,
                row.get('Nota', '')
            ))
    
    conn.commit()
    conn.close()
    print(f"Importati {cursor.rowcount} giocatori dal CSV")

def insert_player(data: Dict) -> int:
    """Inserisce un nuovo giocatore (senza ID - autoincrement)"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO calciatori (
            Nome, Squadra, Ruolo, Ruolo_Dettaglio, Fuori_lista, 
            Tiratore_CP, Media_Voto, FantaMedia, FantaMedia_Prevista, 
            Titolarita, Prezzo, Obiettivo, Nota
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['Nome'],
        data.get('Squadra'),
        data.get('Ruolo'),
        data.get('Ruolo_Dettaglio'),
        data.get('Fuori_lista', 0),
        data.get('Tiratore_CP', 0),
        data.get('Media_Voto'),
        data.get('FantaMedia'),
        data.get('FantaMedia_Prevista'),
        data.get('Titolarita'),
        data.get('Prezzo'),
        data.get('Obiettivo', 0),
        data.get('Nota', '')
    ))
    
    player_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return player_id

def get_filtered_players(order_by: List[Tuple[str, str]] = None, filters: Dict = None) -> List[Dict]:
    """
    Recupera giocatori con ordinamento cumulativo e filtri
    order_by: Lista di tuple (campo, direzione) es. [('Squadra', 'ASC'), ('FantaMedia', 'DESC')]
    filters: Dizionario con filtri es. {'Tiratore_CP': 1, 'Prezzo': {'op': '<', 'val': 15}}
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM calciatori"
    params = []
    
    # Applica filtri
    if filters:
        where_clauses = []
        for field, value in filters.items():
            if isinstance(value, dict):  # Filtro con operatore
                where_clauses.append(f"{field} {value['op']} ?")
                params.append(value['val'])
            else:  # Filtro semplice
                where_clauses.append(f"{field} = ?")
                params.append(value)
        
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
    
    # Applica ordinamento cumulativo
    if order_by and len(order_by) > 0:
        order_clauses = [f"{field} {direction}" for field, direction in order_by]
        query += " ORDER BY " + ", ".join(order_clauses)
    else:
        # Ordinamento default: Ruolo inverso (P-D-C-A) + FantaMedia DESC
        query += " ORDER BY Ruolo DESC, FantaMedia DESC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def get_player_by_id(player_id: int) -> Optional[Dict]:
    """Recupera un singolo giocatore per ID"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM calciatori WHERE ID = ?", (player_id,))
    row = cursor.fetchone()
    conn.close()
    
    return dict(row) if row else None

def update_player(player_id: int, data: Dict):
    """Aggiorna un giocatore esistente"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE calciatori SET
            Nome = ?, Squadra = ?, Ruolo = ?, Ruolo_Dettaglio = ?,
            Fuori_lista = ?, Tiratore_CP = ?, Media_Voto = ?,
            FantaMedia = ?, FantaMedia_Prevista = ?, Titolarita = ?,
            Prezzo = ?, Obiettivo = ?, Nota = ?
        WHERE ID = ?
    ''', (
        data['Nome'], data.get('Squadra'), data.get('Ruolo'),
        data.get('Ruolo_Dettaglio'), data.get('Fuori_lista', 0),
        data.get('Tiratore_CP', 0), data.get('Media_Voto'),
        data.get('FantaMedia'), data.get('FantaMedia_Prevista'),
        data.get('Titolarita'), data.get('Prezzo'),
        data.get('Obiettivo', 0), data.get('Nota', ''),
        player_id
    ))
    
    conn.commit()
    conn.close()

def delete_player(player_id: int):
    """Elimina un giocatore"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM calciatori WHERE ID = ?", (player_id,))
    conn.commit()
    conn.close()

def update_obiettivo(player_id: int, value: int):
    """Aggiorna solo il campo Obiettivo (per AJAX)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE calciatori SET Obiettivo = ? WHERE ID = ?", (value, player_id))
    conn.commit()
    conn.close()

def get_advanced_search(filters: Dict) -> List[Dict]:
    """Ricerca avanzata con filtri complessi"""
    conn = get_connection()
    cursor = conn.cursor()
    
    where_clauses = []
    params = []
    
    for field, filter_data in filters.items():
        if filter_data['value'] is not None and filter_data['value'] != '':
            operator = filter_data['operator']
            value = filter_data['value']
            
            if operator == 'LIKE':
                where_clauses.append(f"{field} LIKE ?")
                params.append(f"%{value}%")
            else:
                where_clauses.append(f"{field} {operator} ?")
                params.append(value)
    
    query = "SELECT * FROM calciatori"
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)
    query += " ORDER BY Ruolo DESC, FantaMedia DESC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]