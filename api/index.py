import os, io
import pandas as pd
import plotly.express as px
from flask import (Flask, render_template, redirect,
                   url_for, Response, flash, abort)
from flask_migrate import Migrate

# Importation corrigée pour éviter les erreurs relatives selon votre structure
from api.models import db, Etudiant
from api.forms import EtudiantForm

app = Flask(__name__, template_folder='../templates', static_folder='../static')

# Configuration de la clé secrète
app.config['SECRET_KEY'] = os.environ.get(
    'SECRET_KEY', 
    '216f422e7dc13f83311339cfc7e730e1a4467f9a64b2a492f3f9a8240ef45c97'
)

# Configuration de la base de données PostgreSQL (Neon)
database_url = os.environ.get('DATABASE_URL')

if not database_url:
    raise ValueError("La variable d'environnement 'DATABASE_URL' est manquante ou non configurée !")

if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

with app.app_context():
    # Crée les tables dans la base de données distante
    db.create_all()

# ── ACCUEIL ───────────────────────────────────────────────────
@app.route('/')
def index():
    try:
        total = Etudiant.query.count()
        tres_satisfaits = Etudiant.query.filter_by(satisfaction='Très').count()
        taux_satisfaction = round((tres_satisfaits / total * 100), 1) if total > 0 else 0
    except Exception:
        total = 0
        tres_satisfaits = 0
        taux_satisfaction = 0.0

    return render_template('index.html',
                           total=total,
                           tres_satisfaits=tres_satisfaits,
                           taux_satisfaction=taux_satisfaction)

# ── FORMULAIRE ───────────────────────────────────────────────
@app.route('/formulaire', methods=['GET', 'POST'])
def formulaire():
    form = EtudiantForm()
    
    try:
        total = Etudiant.query.count()
    except Exception:
        total = 0

    if total >= 100:
        flash('Les 100 étudiants ont déjà été enregistrés.', 'warning')
        return redirect(url_for('donnees'))
    
    if form.validate_on_submit():
        try:
            etudiant = Etudiant(
                age=form.age.data,
                sexe=form.sexe.data,
                niveau_etudes=form.niveau_etudes.data,
                filiere=form.filiere.data,
                heures_etude=form.heures_etude.data,
                moment_etude=form.moment_etude.data,
                matiere_principale=form.matiere_principale.data,
                lieu_etude=form.lieu_etude.data,
                methode_etude=form.methode_etude.data,
                satisfaction=form.satisfaction.data,
            )
            db.session.add(etudiant)
            db.session.commit()
            
            total_apres = Etudiant.query.count()
            reste = 100 - total_apres
            flash(f'Étudiant enregistré ! Il reste {reste} étudiant(s) à saisir.', 'success')
        except Exception as e:
            db.session.rollback()
            flash("Une erreur est survenue lors de l'enregistrement de l'étudiant : " + str(e), 'danger')
            
        return redirect(url_for('formulaire'))
        
    return render_template('formulaire.html', form=form, total=total)

# ── DONNÉES ──────────────────────────────────────────────────
@app.route('/donnees')
def donnees():
    try:
        etudiants = Etudiant.query.order_by(Etudiant.created_at.desc()).all()
    except Exception:
        etudiants = []
        flash("Impossible de charger les données depuis la base de données.", "danger")
        
    return render_template('donnees.html', etudiants=etudiants)

# ── SUPPRESSION ──────────────────────────────────────────────
@app.route('/supprimer/<int:id>')
def supprimer(id):
    etudiant = Etudiant.query.get_or_404(id)
    try:
        db.session.delete(etudiant)
        db.session.commit()
        flash('Entrée supprimée.', 'warning')
    except Exception as e:
        db.session.rollback()
        flash("Erreur lors de la suppression : " + str(e), 'danger')
        
    return redirect(url_for('donnees'))

# ── DASHBOARD ────────────────────────────────────────────────
@app.route('/dashboard')
def dashboard():
    try:
        rows = [e.to_dict() for e in Etudiant.query.all()]
    except Exception:
        rows = []
        
    if not rows:
        return render_template('dashboard.html',
                               graphiques=[], stats={})

    df = pd.DataFrame(rows)

    stats = {
        'total': len(df),
        'heures_moy': round(df['heures_etude'].mean(), 1),
        'heures_max': df['heures_etude'].max(),
        'heures_min': df['heures_etude'].min(),
        'moment_top': df['moment_etude'].value_counts().idxmax(),
        'lieu_top': df['lieu_etude'].value_counts().idxmax(),
        'methode_top': df['methode_etude'].value_counts().idxmax(),
        'filiere_top': df.groupby('filiere')['heures_etude'].mean().idxmax(),
        'pct_tres_satisfait': round((df['satisfaction'] == 'Très').mean() * 100, 1),
    }

    graphiques = []

    fig1 = px.box(df, x='filiere', y='heures_etude',
                  title="Heures d'étude par filière",
                  color='filiere',
                  labels={'filiere': 'Filière',
                          'heures_etude': 'Heures / jour'})
    fig1.update_layout(showlegend=False)
    graphiques.append(fig1.to_html(full_html=False))

    fig2 = px.pie(df, names='moment_etude',
                  title="Moment d'étude préféré",
                  hole=0.4,
                  color_discrete_sequence=px.colors.sequential.RdBu)
    graphiques.append(fig2.to_html(full_html=False))

    ordre_niveaux = ['Licence 1', 'Licence 2', 'Licence 3',
                     'Master 1', 'Master 2', 'Doctorat']
    fig3 = px.histogram(df, x='niveau_etudes', y='heures_etude',
                        histfunc='avg',
                        title="Heures moyennes d'étude par niveau",
                        labels={'niveau_etudes': 'Niveau',
                                'heures_etude': 'Heures moy. / jour'},
                        color='niveau_etudes',
                        category_orders={'niveau_etudes': ordre_niveaux})
    fig3.update_layout(showlegend=False)
    graphiques.append(fig3.to_html(full_html=False))

    fig4 = px.pie(df, names='lieu_etude',
                  title="Lieux d'étude préférés",
                  hole=0.4,
                  color_discrete_sequence=px.colors.sequential.Teal)
    graphiques.append(fig4.to_html(full_html=False))

    methodes = df['methode_etude'].value_counts().reset_index()
    fig5 = px.bar(methodes, x='methode_etude', y='count',
                  title="Méthodes d'étude utilisées",
                  labels={'methode_etude': 'Méthode',
                          'count': 'Nombre d\'étudiants'},
                  color='methode_etude')
    fig5.update_layout(showlegend=False)
    graphiques.append(fig5.to_html(full_html=False))

    satisfaction_ordre = ['Pas du tout', 'Peu', 'Assez', 'Très']
    fig6 = px.histogram(df, x='filiere',
                        color='satisfaction',
                        barmode='group',
                        title="Satisfaction de l'emploi du temps par filière",
                        labels={'filiere': 'Filière',
                                'count': 'Nombre',
                                'satisfaction': 'Satisfaction'},
                        category_orders={'satisfaction': satisfaction_ordre})
    graphiques.append(fig6.to_html(full_html=False))

    return render_template('dashboard.html',
                           graphiques=graphiques,
                           stats=stats)

# ── EXPORT CSV ───────────────────────────────────────────────
@app.route('/export')
def export():
    rows = [e.to_dict() for e in Etudiant.query.all()]
    df = pd.DataFrame(rows)
    buf = io.StringIO()
    df.to_csv(buf, index=False, sep=';', encoding='utf-8-sig')
    return Response(buf.getvalue(),
                    mimetype='text/csv',
                    headers={'Content-Disposition':
                             'attachment; filename=emploi_du_temps.csv'})

app = app

if __name__ == '__main__':
    app.run(debug=True)