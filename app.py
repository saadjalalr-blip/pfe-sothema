from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
import os

database_url = os.environ.get('DATABASE_URL', 'sqlite:///mirage.db')

# Render utilise postgres:// mais SQLAlchemy veut postgresql://
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ── Modèle base de données ──
class Lot(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    produit     = db.Column(db.String(20), nullable=False)
    num_lot     = db.Column(db.Integer, nullable=False)
    qu_recue    = db.Column(db.Float, nullable=False)
    fib         = db.Column(db.Float, default=0)
    par         = db.Column(db.Float, default=0)
    res_v       = db.Column(db.Float, default=0)
    casse       = db.Column(db.Float, default=0)
    febr        = db.Column(db.Float, default=0)
    total       = db.Column(db.Float, default=0)
    q_bon_mir   = db.Column(db.Float, default=0)
    date_rep    = db.Column(db.String(20), default='')
    pertes      = db.Column(db.Float, default=0)
    rend_mir    = db.Column(db.Float, default=0)
    rend_glob   = db.Column(db.Float, default=0)

# ── Routes pages ──
@app.route('/')
def accueil():
    return render_template('accueil.html')

@app.route('/introduction')
def introduction():
    return render_template('introduction.html')

@app.route('/problematique')
def problematique():
    return render_template('problematique.html')

@app.route('/procede')
def procede():
    return render_template('procede.html')

@app.route('/methodologie')
def methodologie():
    return render_template('methodologie.html')

@app.route('/calculs')
def calculs():
    return render_template('calculs.html')

# ── API lots ──
@app.route('/api/lots', methods=['GET'])
def get_lots():
    lots = Lot.query.all()
    return jsonify([{
        'id': l.id,
        'produit': l.produit,
        'num_lot': l.num_lot,
        'qu': l.qu_recue,
        'fib': l.fib,
        'par': l.par,
        'res': l.res_v,
        'cas': l.casse,
        'feb': l.febr,
        'total': l.total,
        'q_bon': l.q_bon_mir,
        'date': l.date_rep,
        'pertes': l.pertes,
        'rend_mir': l.rend_mir,
        'rend_glob': l.rend_glob
    } for l in lots])

@app.route('/api/lots', methods=['POST'])
def add_lot():
    data = request.json
    lot = Lot(
        produit=data['produit'],
        num_lot=data['num_lot'],
        qu_recue=data['qu'],
        fib=data['fib'],
        par=data['par'],
        res_v=data['res'],
        casse=data['cas'],
        febr=data['feb'],
        total=data['total'],
        q_bon_mir=data['q_bon'],
        date_rep=data['date'],
        pertes=data['pertes'],
        rend_mir=data['rend_mir'],
        rend_glob=data['rend_glob']
    )
    db.session.add(lot)
    db.session.commit()
    return jsonify({'success': True, 'id': lot.id})

@app.route('/api/lots/<int:lot_id>', methods=['DELETE'])
def delete_lot(lot_id):
    lot = Lot.query.get_or_404(lot_id)
    db.session.delete(lot)
    db.session.commit()
    return jsonify({'success': True})

# ── Créer la base de données ──
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)