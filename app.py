import os, io
import pandas as pd
import plotly.express as px
from flask import (Flask, render_template, redirect,
                   url_for, Response, flash)
from models import db, Etudiant
from forms import EtudiantForm

app = Flask(__name__)
app.config['SECRET_KEY']                     = os.environ.get('SECRET_KEY', 'dev-key-inf232')
app.config['SQLALCHEMY_DATABASE_URI']        = os.environ.get('DATABASE_URL', 'sqlite:///emploi_du_temps.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

# ── ACCUEIL ───────────────────────────────────────────────────
@app.route('/')
def index():
    total       = Etudiant.query.count()
    tres_satisfaits = Etudiant.query.filter_by(satisfaction='Très').count()
    taux_satisfaction = round((tres_satisfaits / total * 100), 1) if total > 0 else 0
    return render_template('index.html',
                           total=total,
                           tres_satisfaits=tres_satisfaits,
                           taux_satisfaction=taux_satisfaction)

# ── FORMULAIRE ───────────────────────────────────────────────
@app.route('/formulaire', methods=['GET', 'POST'])
def formulaire():
    form  = EtudiantForm()
    total = Etudiant.query.count()
    if total >= 100:
        flash('Les 100 étudiants ont déjà été enregistrés.', 'warning')
        return redirect(url_for('donnees'))
    if form.validate_on_submit():
        etudiant = Etudiant(
            age                = form.age.data,
            sexe               = form.sexe.data,
            niveau_etudes      = form.niveau_etudes.data,
            filiere            = form.filiere.data,
            heures_etude       = form.heures_etude.data,
            moment_etude       = form.moment_etude.data,
            matiere_principale = form.matiere_principale.data,
            lieu_etude         = form.lieu_etude.data,
            methode_etude      = form.methode_etude.data,
            satisfaction       = form.satisfaction.data,
        )
        db.session.add(etudiant)
        db.session.commit()
        reste = 100 - Etudiant.query.count()
        flash(f'Étudiant enregistré ! Il reste {reste} étudiant(s) à saisir.',
              'success')
        return redirect(url_for('formulaire'))
    return render_template('formulaire.html', form=form,
                           total=Etudiant.query.count())

# ── DONNÉES ──────────────────────────────────────────────────
@app.route('/donnees')
def donnees():
    etudiants = Etudiant.query.order_by(Etudiant.created_at.desc()).all()
    return render_template('donnees.html', etudiants=etudiants)

# ── SUPPRESSION ──────────────────────────────────────────────
@app.route('/supprimer/<int:id>')
def supprimer(id):
    etudiant = Etudiant.query.get_or_404(id)
    db.session.delete(etudiant)
    db.session.commit()
    flash('Entrée supprimée.', 'warning')
    return redirect(url_for('donnees'))

# ── DASHBOARD ────────────────────────────────────────────────
@app.route('/dashboard')
def dashboard():
    rows = [e.to_dict() for e in Etudiant.query.all()]
    if not rows:
        return render_template('dashboard.html',
                               graphiques=[], stats={})

    df = pd.DataFrame(rows)

    # Statistiques descriptives
    stats = {
        'total':             len(df),
        'heures_moy':        round(df['heures_etude'].mean(), 1),
        'heures_max':        df['heures_etude'].max(),
        'heures_min':        df['heures_etude'].min(),
        'moment_top':        df['moment_etude'].value_counts().idxmax(),
        'lieu_top':          df['lieu_etude'].value_counts().idxmax(),
        'methode_top':       df['methode_etude'].value_counts().idxmax(),
        'filiere_top':       df.groupby('filiere')['heures_etude']
                               .mean().idxmax(),
        'pct_tres_satisfait': round(
            (df['satisfaction'] == 'Très').mean() * 100, 1),
    }

    graphiques = []

    # 1. Heures d'étude par filière
    fig1 = px.box(df, x='filiere', y='heures_etude',
                  title="Heures d'étude par filière",
                  color='filiere',
                  labels={'filiere': 'Filière',
                          'heures_etude': 'Heures / jour'})
    fig1.update_layout(showlegend=False)
    graphiques.append(fig1.to_html(full_html=False))

    # 2. Moment d'étude préféré
    fig2 = px.pie(df, names='moment_etude',
                  title="Moment d'étude préféré",
                  hole=0.4,
                  color_discrete_sequence=px.colors.sequential.RdBu)
    graphiques.append(fig2.to_html(full_html=False))

    # 3. Heures d'étude par niveau
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

    # 4. Lieux d'étude préférés
    fig4 = px.pie(df, names='lieu_etude',
                  title="Lieux d'étude préférés",
                  hole=0.4,
                  color_discrete_sequence=px.colors.sequential.Teal)
    graphiques.append(fig4.to_html(full_html=False))

    # 5. Méthodes d'étude utilisées
    methodes = df['methode_etude'].value_counts().reset_index()
    fig5 = px.bar(methodes, x='methode_etude', y='count',
                  title="Méthodes d'étude utilisées",
                  labels={'methode_etude': 'Méthode',
                          'count': 'Nombre d\'étudiants'},
                  color='methode_etude')
    fig5.update_layout(showlegend=False)
    graphiques.append(fig5.to_html(full_html=False))

    # 6. Satisfaction par filière
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
    df   = pd.DataFrame(rows)
    buf  = io.StringIO()
    df.to_csv(buf, index=False, sep=';', encoding='utf-8-sig')
    return Response(buf.getvalue(),
                    mimetype='text/csv',
                    headers={'Content-Disposition':
                             'attachment; filename=emploi_du_temps.csv'})

if __name__ == '__main__':
    app.run(debug=True)