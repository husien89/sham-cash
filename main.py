from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from google.cloud import datastore
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import uuid
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'sham-cash-secret-key')
client = datastore.Client()