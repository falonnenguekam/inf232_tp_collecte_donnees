from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Etudiant(db.Model):
    __tablename__ = 'etudiants'

    id                  = db.Column(db.Integer, primary_key=True)
    age                 = db.Column(db.Integer, nullable=False)
    sexe                = db.Column(db.String(1), nullable=False)
    niveau_etudes       = db.Column(db.String(20), nullable=False)
    filiere             = db.Column(db.String(50), nullable=False)
    heures_etude        = db.Column(db.Float, nullable=False)
    moment_etude        = db.Column(db.String(20), nullable=False)
    matiere_principale  = db.Column(db.String(50), nullable=False)
    lieu_etude          = db.Column(db.String(30), nullable=False)
    methode_etude       = db.Column(db.String(30), nullable=False)
    satisfaction        = db.Column(db.String(30), nullable=False)
    created_at          = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id':                 self.id,
            'age':                self.age,
            'sexe':               self.sexe,
            'niveau_etudes':      self.niveau_etudes,
            'filiere':            self.filiere,
            'heures_etude':       self.heures_etude,
            'moment_etude':       self.moment_etude,
            'matiere_principale': self.matiere_principale,
            'lieu_etude':         self.lieu_etude,
            'methode_etude':      self.methode_etude,
            'satisfaction':       self.satisfaction,
            'created_at':         self.created_at.isoformat() if self.created_at else None
        }