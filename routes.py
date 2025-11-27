from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash
import db_manager

main = Blueprint('main', __name__)

# --- UTILS / HELPER FUNCTIONS ---

def manage_cumulative_sort(field):
    """
    Gestisce la logica di ordinamento cumulativo salvata in sessione.
    Esempio: Click su 'Squadra', poi su 'Media_Voto'.
    Risultato: ORDER BY Media_Voto [DESC], Squadra [ASC]
    """
    current_sort = session.get('sort_history', [])
    
    # Default direction per tipo di campo
    # Numeri -> DESC (migliori in alto), Stringhe -> ASC (A-Z)
    is_numeric = field in ['Media_Voto', 'FantaMedia', 'Prezzo', 'Titolarita']
    default_dir = 'DESC' if is_numeric else 'ASC'
    
    # Cerca se il campo è già presente nell'ordinamento
    existing_index = next((i for i, (f, d) in enumerate(current_sort) if f == field), -1)
    
    new_dir = default_dir
    
    if existing_index != -1:
        # Se esiste, inverti la direzione e rimuovilo dalla posizione attuale
        _, current_dir = current_sort.pop(existing_index)
        new_dir = 'ASC' if current_dir == 'DESC' else 'DESC'
    
    # Inserisci in testa alla lista (è il criterio prioritario)
    current_sort.insert(0, (field, new_dir))
    
    # Limita la memoria agli ultimi 3 ordinamenti per non impazzire
    session['sort_history'] = current_sort[:3]
    session.modified = True

# --- ROUTES ---

@main.route('/')
def index():
    # 1. Gestione Reset Ordinamento
    if request.args.get('reset_sort'):
        session.pop('sort_history', None)
        return redirect(url_for('main.index'))

    # 2. Gestione Nuovo Ordinamento (Click su intestazione)
    sort_field = request.args.get('sort')
    if sort_field:
        manage_cumulative_sort(sort_field)
    
    # Recupera ordinamento dalla sessione o usa default
    order_by = session.get('sort_history', [])
    
    # 3. Filtri Rapidi (Query String)
    filters = {}
    
    # Filtro Ruolo
    if request.args.get('ruolo'):
        filters['Ruolo'] = request.args.get('ruolo')
        
    # Filtri Booleani "Solo Sì"
    if request.args.get('solo_tiratori'):
        filters['Tiratore_CP'] = 1
    if request.args.get('solo_obiettivi'):
        filters['Obiettivo'] = 1
    if request.args.get('solo_fuori_lista'):
        filters['Fuori_lista'] = 1
        
    # Recupera Giocatori
    players = db_manager.get_filtered_players(order_by=order_by, filters=filters)
    
    # Calcolo statistiche rapide per la dashboard
    stats = {
        'total': len(players),
        'obiettivi': sum(1 for p in players if p['Obiettivo'] == 1),
        'budget_speso': sum(p['Prezzo'] for p in players if p['Prezzo'])
    }
    
    return render_template('index.html', players=players, stats=stats, current_sort=order_by)

@main.route('/insert', methods=['GET', 'POST'])
def insert():
    if request.method == 'POST':
        # Raccolta dati dal form
        # NOTA: I checkbox HTML non inviano nulla se non selezionati.
        # Usiamo '1' se presente, '0' altrimenti.
        player_data = {
            'Nome': request.form['Nome'],
            'Squadra': request.form['Squadra'],
            'Ruolo': request.form['Ruolo'],
            'Ruolo_Dettaglio': request.form['Ruolo_Dettaglio'],
            'Fuori_lista': 1 if request.form.get('Fuori_lista') else 0,
            'Tiratore_CP': 1 if request.form.get('Tiratore_CP') else 0,
            'Obiettivo': 1 if request.form.get('Obiettivo') else 0,
            'Media_Voto': request.form['Media_Voto'] or None,
            'FantaMedia': request.form['FantaMedia'] or None,
            'FantaMedia_Prevista': request.form['FantaMedia_Prevista'] or None,
            'Titolarita': request.form['Titolarita'] or None,
            'Prezzo': request.form['Prezzo'] or None,
            'Nota': request.form['Nota']
        }
        
        db_manager.insert_player(player_data)
        flash('Giocatore inserito con successo!', 'success')
        return redirect(url_for('main.index'))
        
    return render_template('insert.html')

@main.route('/detail/<int:player_id>', methods=['GET', 'POST'])
def detail(player_id):
    player = db_manager.get_player_by_id(player_id)
    
    if not player:
        flash('Giocatore non trovato!', 'danger')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        # Gestione Eliminazione
        if 'delete' in request.form:
            db_manager.delete_player(player_id)
            flash(f"Giocatore {player['Nome']} eliminato.", 'warning')
            return redirect(url_for('main.index'))
            
        # Gestione Aggiornamento
        updated_data = {
            'Nome': request.form['Nome'],
            'Squadra': request.form['Squadra'],
            'Ruolo': request.form['Ruolo'],
            'Ruolo_Dettaglio': request.form['Ruolo_Dettaglio'],
            'Fuori_lista': 1 if request.form.get('Fuori_lista') else 0,
            'Tiratore_CP': 1 if request.form.get('Tiratore_CP') else 0,
            'Obiettivo': 1 if request.form.get('Obiettivo') else 0,
            'Media_Voto': request.form['Media_Voto'] or None,
            'FantaMedia': request.form['FantaMedia'] or None,
            'FantaMedia_Prevista': request.form['FantaMedia_Prevista'] or None,
            'Titolarita': request.form['Titolarita'] or None,
            'Prezzo': request.form['Prezzo'] or None,
            'Nota': request.form['Nota']
        }
        
        db_manager.update_player(player_id, updated_data)
        flash('Dati aggiornati correttamente.', 'success')
        return redirect(url_for('main.detail', player_id=player_id))
        
    return render_template('detail.html', player=player)

@main.route('/search', methods=['GET', 'POST'])
def search_page():
    results = []
    if request.method == 'POST':
        # Costruzione dizionario filtri complessi per db_manager.get_advanced_search
        # Nota: Questo si aspetta che tu abbia implementato get_advanced_search
        # come definito nel file db_manager.py che hai fornito
        
        filters = {}
        
        # Mapping campi semplici
        if request.form.get('Nome'):
            filters['Nome'] = {'operator': 'LIKE', 'value': request.form['Nome']}
        
        if request.form.get('Squadra'):
            filters['Squadra'] = {'operator': 'LIKE', 'value': request.form['Squadra']}
            
        if request.form.get('Ruolo'):
            filters['Ruolo'] = {'operator': '=', 'value': request.form['Ruolo']}
            
        # Mapping campi numerici con operatore selezionabile
        # Prezzo
        if request.form.get('Prezzo_val'):
            filters['Prezzo'] = {
                'operator': request.form.get('Prezzo_op', '='),
                'value': request.form.get('Prezzo_val')
            }
            
        # Titolarità
        if request.form.get('Titolarita_val'):
            filters['Titolarita'] = {
                'operator': request.form.get('Titolarita_op', '='),
                'value': request.form.get('Titolarita_val')
            }
            
        # FantaMedia
        if request.form.get('FantaMedia_val'):
            filters['FantaMedia'] = {
                'operator': request.form.get('FantaMedia_op', '='),
                'value': request.form.get('FantaMedia_val')
            }
            
        # Checkbox "Solo Selezionati"
        if request.form.get('Tiratore_CP'):
            filters['Tiratore_CP'] = {'operator': '=', 'value': 1}
            
        if request.form.get('Fuori_lista'):
            filters['Fuori_lista'] = {'operator': '=', 'value': 1}
            
        if request.form.get('Obiettivo'):
            filters['Obiettivo'] = {'operator': '=', 'value': 1}
            
        results = db_manager.get_advanced_search(filters)
        
    return render_template('search.html', results=results)

@main.route('/api/toggle_objective', methods=['POST'])
def toggle_objective():
    """API per aggiornare il flag Obiettivo via AJAX"""
    data = request.get_json()
    player_id = data.get('id')
    new_status = data.get('status') # 1 o 0
    
    if player_id is not None and new_status is not None:
        db_manager.update_obiettivo(player_id, int(new_status))
        return jsonify({'success': True})
    
    return jsonify({'success': False}), 400