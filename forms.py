from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, FloatField, StringField
from wtforms.validators import DataRequired, NumberRange

class EtudiantForm(FlaskForm):

    age = IntegerField('Âge',
                       validators=[DataRequired(),
                                   NumberRange(min=15, max=60)])

    sexe = SelectField('Sexe',
                       choices=[('M', 'Masculin'), ('F', 'Féminin')],
                       validators=[DataRequired()])

    niveau_etudes = SelectField('Niveau d\'études',
                                choices=[
                                    ('Licence 1',  'Licence 1'),
                                    ('Licence 2',  'Licence 2'),
                                    ('Licence 3',  'Licence 3'),
                                    ('Master 1',   'Master 1'),
                                    ('Master 2',   'Master 2'),
                                    ('Doctorat',   'Doctorat'),
                                ],
                                validators=[DataRequired()])

    filiere = SelectField('Filière',
                          choices=[
                              ('Informatique',       'Informatique'),
                              ('Mathématiques',      'Mathématiques'),
                              ('Droit',              'Droit'),
                              ('Médecine',           'Médecine'),
                              ('Économie',           'Économie'),
                              ('Lettres',            'Lettres'),
                              ('Sciences',           'Sciences'),
                              ('Gestion',            'Gestion'),
                              ('Autre',              'Autre'),
                          ],
                          validators=[DataRequired()])

    heures_etude = FloatField('Nombre d\'heures d\'étude par jour',
                              validators=[DataRequired(),
                                          NumberRange(min=0, max=24)])

    moment_etude = SelectField('Moment d\'étude préféré',
                               choices=[
                                   ('Matin',       'Matin (6h-12h)'),
                                   ('Après-midi',  'Après-midi (12h-18h)'),
                                   ('Soir',        'Soir (18h-22h)'),
                                   ('Nuit',        'Nuit (22h et plus)'),
                               ],
                               validators=[DataRequired()])

    matiere_principale = SelectField('Matière la plus étudiée',
                                     choices=[
                                         ('Mathématiques',   'Mathématiques'),
                                         ('Informatique',    'Informatique'),
                                         ('Physique',        'Physique'),
                                         ('Chimie',          'Chimie'),
                                         ('Droit',           'Droit'),
                                         ('Économie',        'Économie'),
                                         ('Langues',         'Langues'),
                                         ('Autre',           'Autre'),
                                     ],
                                     validators=[DataRequired()])

    lieu_etude = SelectField('Lieu d\'étude préféré',
                             choices=[
                                 ('Domicile',      'Domicile'),
                                 ('Bibliothèque',  'Bibliothèque'),
                                 ('Campus',        'Campus'),
                                 ('Café',          'Café / Restaurant'),
                                 ('Autre',         'Autre'),
                             ],
                             validators=[DataRequired()])

    methode_etude = SelectField('Méthode d\'étude principale',
                                choices=[
                                    ('Fiches',       'Fiches de révision'),
                                    ('Relecture',    'Relecture des cours'),
                                    ('Exercices',    'Exercices pratiques'),
                                    ('Groupe',       'Travail en groupe'),
                                    ('Vidéos',       'Vidéos / Tutoriels'),
                                    ('Autre',        'Autre'),
                                ],
                                validators=[DataRequired()])

    satisfaction = SelectField('Satisfaction de votre emploi du temps',
                               choices=[
                                   ('Pas du tout',  'Pas du tout satisfait'),
                                   ('Peu',          'Peu satisfait'),
                                   ('Assez',        'Assez satisfait'),
                                   ('Très',         'Très satisfait'),
                               ],
                               validators=[DataRequired()])