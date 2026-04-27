from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'pfe-sothema-secret-2025'

# ── Base de données ──
database_url = os.environ.get('DATABASE_URL', 'sqlite:///mirage.db')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ── Email ──
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'saad.jalaledine03@gmail.com'
app.config['MAIL_PASSWORD'] = 'hmcd mgxo ekcp zxab'

db = SQLAlchemy(app)
mail = Mail(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
s = URLSafeTimedSerializer(app.config['SECRET_KEY'])

# ── Code d'invitation ──
CODE_INVITATION = 'PertesBiocad2026'

# ── Modèle User ──
class User(UserMixin, db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    nom       = db.Column(db.String(50), nullable=False)
    prenom    = db.Column(db.String(50), nullable=False)
    poste     = db.Column(db.String(50), nullable=False)
    email     = db.Column(db.String(100), unique=True, nullable=False)
    password  = db.Column(db.String(200), nullable=False)
    confirmed = db.Column(db.Boolean, default=False)

# ── Modèle Lot ──
class Lot(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    produit   = db.Column(db.String(20), nullable=False)
    num_lot   = db.Column(db.Integer, nullable=False)
    qu_recue  = db.Column(db.Float, nullable=False)
    fib       = db.Column(db.Float, default=0)
    par       = db.Column(db.Float, default=0)
    res_v     = db.Column(db.Float, default=0)
    casse     = db.Column(db.Float, default=0)
    febr      = db.Column(db.Float, default=0)
    total     = db.Column(db.Float, default=0)
    q_bon_mir = db.Column(db.Float, default=0)
    date_rep  = db.Column(db.String(20), default='')
    pertes    = db.Column(db.Float, default=0)
    rend_mir  = db.Column(db.Float, default=0)
    rend_glob = db.Column(db.Float, default=0)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ── Routes Auth ──
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        nom    = request.form['nom']
        prenom = request.form['prenom']
        poste  = request.form['poste']
        email  = request.form['email']
        mdp    = request.form['password']
        code   = request.form['code']

        # Vérification code d'invitation
        if code != CODE_INVITATION:
            flash('Code d\'invitation invalide.', 'error')
            return redirect(url_for('signup'))

        # Vérification email existant
        if User.query.filter_by(email=email).first():
            flash('Email déjà utilisé.', 'error')
            return redirect(url_for('signup'))

        # Création utilisateur
        user = User(
            nom=nom, prenom=prenom, poste=poste,
            email=email,
            password=generate_password_hash(mdp)
        )
        db.session.add(user)
        db.session.commit()

        # Envoi email de confirmation
        token = s.dumps(email, salt='email-confirm')
        lien  = url_for('confirm_email', token=token, _external=True)
        msg   = Message('Confirmation de votre compte — PFE SOTHEMA',
                        sender='saad.jalaledine03@gmail.com',
                        recipients=[email])
        msg.body = f'Bonjour {prenom},\n\nCliquez sur ce lien pour confirmer votre compte :\n{lien}\n\nCe lien expire dans 1 heure.\n\nCordialement,\nPFE SOTHEMA'
        mail.send(msg)

        flash('Inscription réussie ! Un email de confirmation a été envoyé.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=3600)
    except:
        flash('Lien invalide ou expiré.', 'error')
        return redirect(url_for('login'))

    user = User.query.filter_by(email=email).first()
    if user:
        user.confirmed = True
        db.session.commit()
        flash('Compte confirmé — vous pouvez vous connecter.', 'success')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        mdp   = request.form['password']
        user  = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, mdp):
            flash('Email ou mot de passe incorrect.', 'error')
            return redirect(url_for('login'))

        if not user.confirmed:
            flash('Veuillez confirmer votre email avant de vous connecter.', 'error')
            return redirect(url_for('login'))

        login_user(user)
        return redirect(url_for('accueil'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# ── Routes pages ──
@app.route('/')
@login_required
def accueil():
    return render_template('accueil.html')

@app.route('/introduction')
@login_required
def introduction():
    return render_template('introduction.html')

@app.route('/problematique')
@login_required
def problematique():
    return render_template('problematique.html')

@app.route('/procede')
@login_required
def procede():
    return render_template('procede.html')

@app.route('/methodologie')
@login_required
def methodologie():
    return render_template('methodologie.html')

@app.route('/calculs')
@login_required
def calculs():
    return render_template('calculs.html')

# ── API lots ──
@app.route('/api/lots', methods=['GET'])
@login_required
def get_lots():
    lots = Lot.query.all()
    return jsonify([{
        'id': l.id, 'produit': l.produit, 'num_lot': l.num_lot,
        'qu': l.qu_recue, 'fib': l.fib, 'par': l.par, 'res': l.res_v,
        'cas': l.casse, 'feb': l.febr, 'total': l.total,
        'q_bon': l.q_bon_mir, 'date': l.date_rep,
        'pertes': l.pertes, 'rend_mir': l.rend_mir, 'rend_glob': l.rend_glob
    } for l in lots])

@app.route('/api/lots', methods=['POST'])
@login_required
def add_lot():
    data = request.json
    lot  = Lot(
        produit=data['produit'], num_lot=data['num_lot'], qu_recue=data['qu'],
        fib=data['fib'], par=data['par'], res_v=data['res'], casse=data['cas'],
        febr=data['feb'], total=data['total'], q_bon_mir=data['q_bon'],
        date_rep=data['date'], pertes=data['pertes'],
        rend_mir=data['rend_mir'], rend_glob=data['rend_glob']
    )
    db.session.add(lot)
    db.session.commit()
    return jsonify({'success': True, 'id': lot.id})

@app.route('/api/lots/<int:lot_id>', methods=['DELETE'])
@login_required
def delete_lot(lot_id):
    lot = Lot.query.get_or_404(lot_id)
    db.session.delete(lot)
    db.session.commit()
    return jsonify({'success': True})

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)