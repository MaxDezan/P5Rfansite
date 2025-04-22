from flask import Flask, render_template, request, redirect, url_for
import sqlite3, pytz
from datetime import datetime
import pytz

def get_local_time():
    tz = pytz.timezone('America/Sao_Paulo')
    return datetime.now(tz)

app = Flask(__name__, static_folder='static', template_folder='templates')

@app.context_processor
def inject_ano():
    return {'ano_atual': datetime.now().year}

# Configuração do banco de dados
def get_db_connection():
    conn = sqlite3.connect('forum.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS comentarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            texto TEXT NOT NULL,
            data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

@app.template_filter('formatar_data')
def formatar_data(value):
    tz = pytz.timezone('America/Sao_Paulo')
    if isinstance(value, str):
        try:
            value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return value
    # Converte para o fuso horário correto
    value = value.replace(tzinfo=pytz.utc).astimezone(tz)
    return value.strftime('%d/%m/%Y às %H:%M')

# Rotas principais
@app.route('/')
def home():
    return render_template('index.html')
    
@app.route('/guias')
def guias():
    return render_template('guias.html')

@app.route('/updates')
def updates():
    return render_template('updates.html')

@app.route('/forum')
def forum():
    conn = get_db_connection()
    comentarios = conn.execute('SELECT *, datetime(data) as data_formatada FROM comentarios ORDER BY data DESC').fetchall()
    conn.close()
    return render_template('forum.html', comentarios=comentarios)

@app.route('/personagens')
def personagens():
    return render_template('personagens.html')

@app.route('/adicionar_comentario', methods=['POST'])
def adicionar_comentario():
    texto = request.form.get('comentario', '').strip()[:500]
    if texto:
        conn = get_db_connection()
        conn.execute('INSERT INTO comentarios (texto) VALUES (?)', (texto,))
        conn.commit()
        conn.close()
    return redirect(url_for('forum'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.before_request
def check_routes():
    print(f"Acessando: {request.path}")

import webbrowser
from threading import Timer

def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')

if __name__ == '__main__':
    init_db()
    Timer(1, open_browser).start()  # Abre o navegador após 1 segundo
    app.run(debug=True, use_reloader=False)  # use_reloader=False para evitar abrir o navegador duas vezes

# Para resetar os comentários, descomente a linha abaixo e execute o script:
# python -c "
# import sqlite3; 
# conn = sqlite3.connect('forum.db');
# conn.execute('DELETE FROM comentarios');
# conn.commit();
# print('Comentários resetados!');
# conn.close()
# "