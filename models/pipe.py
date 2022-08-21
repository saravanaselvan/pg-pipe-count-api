from db import db
from flask_jwt_extended import get_jwt_identity
from datetime import datetime
import os
from .user import UserModel
from flask import current_app


class PipeModel(db.Model):
    __tablename__ = 'pipes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('UserModel')
    status = db.Column(db.String(50))
    original_uploaded_file_name = db.Column(db.String(255))
    uploaded_file_name = db.Column(db.String(255))
    output_file_name = db.Column(db.String(255))
    output_file_path = db.Column(db.String(255))
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    def __init__(self,
                 status,
                 original_uploaded_file_name,
                 uploaded_file_name,
                 output_file_name="",
                 output_file_path=""
                 ):
        self.user_id = get_jwt_identity()
        self.status = status
        self.original_uploaded_file_name = original_uploaded_file_name
        self.uploaded_file_name = uploaded_file_name
        self.output_file_name = output_file_name
        self.output_file_path = output_file_path
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def json(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'status': self.status,
            'original_uploaded_file_name': self.original_uploaded_file_name,
            'uploaded_file_name': self.uploaded_file_name,
            'output_file_name': self.output_file_name,
            'output_file_path': self.output_file_path,
            'created_at': str(self.created_at)
        }

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
