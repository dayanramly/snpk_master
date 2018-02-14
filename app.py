from flask import Flask, render_template, redirect, url_for, request, flash
from os import environ, listdir, remove
from os.path import isfile, join
from werkzeug.utils import secure_filename
from pandas import DataFrame, read_csv
from itertools import combinations
from sklearn.preprocessing import LabelEncoder, LabelBinarizer
import csv
import pandas as pd
import numpy as np
import pyfpgrowth
import json

from util import translate_actor, translate_weapon, translate_tipe_kekerasan, translate_bentuk_kekerasan

app = Flask('snpk', template_folder='templates')
app.config['UPLOAD_FOLDER'] = 'uploadfiles'
app.config['SESSION_TYPE'] = 'filesystem'
upload_path = join(app.config['UPLOAD_FOLDER'], 'csv')

ALLOWED_EXTENSIONS = ['csv']


def allowed_file(filename):
	return '.' in filename and \
		filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# @app.route("/")
# def main():
# 	datasnpk = ['snpk_source/SNPK1997.csv']
# 	# datasnpk = ['snpk_source/SNPK1997.csv', 'snpk_source/SNPK1998.csv', 'snpk_source/SNPK1999.csv']
# 	snpklist = []
# 	for f in datasnpk : 
# 		snpklist.append(pd.read_csv(f, encoding = "ISO-8859-1", low_memory=False))
# 		snpkframe = pd.concat(snpklist)

# 	# df = pd.read_csv('snpk_source/SNPK1997.csv', low_memory=False)
# 	data_html = snpkframe.to_html(classes="table table-data")
# 	data_html = data_html.replace('NaN', '')
# 	# return redirect(url_for('load_selection', snpkframe=data_html))
# 	return render_template('index.html', snpkframe=data_html)

@app.route('/import/upload', methods=['GET', 'POST'])
def upload():
	
	if request.method == 'POST':
		if 'csv' in request.files:
			uploaded_csv = request.files['csv']
			filename = secure_filename(uploaded_csv.filename)
			uploaded_csv.save(join(app.config['UPLOAD_FOLDER'], 'csv', filename))
			flash("csv saved.")
		else:
			flash('no files uploaded')

	# return render_template('import.html', files=files)
	return redirect(url_for('main'))

@app.route('/')
def main():
	files = []

	for f in listdir(upload_path):
		if isfile(join(upload_path, f)):
			files.append(f)

	return render_template('import.html', files=files)

@app.route('/<string:filename>/delete')
def delete_csv(filename):
	remove(join(upload_path, filename))
	flash("{} deleted".format(filename))

	return redirect(url_for('main'))
	
@app.route('/selected')
def selected_files():

	merge_rows = []

	for filename in request.args.getlist('filename'):
		merge_rows.append(pd.read_csv(join(upload_path, filename), encoding='ISO-8859-1', low_memory=False))

	snpkframe = pd.concat(merge_rows)

	data = {
		'tahun': [x for x in snpkframe.tahun.unique()],
		'bulan': [x for x in snpkframe.bulan.unique()],
		'quarter': [x for x in snpkframe.quarter.unique()],
		'provinsi': [x for x in snpkframe.provinsi.unique()],
		'kabupaten': [x for x in snpkframe.kabupaten.unique()],
		'kecamatan1': [x for x in snpkframe.kecamatan1.unique()],
		'kecamatan2': [x for x in snpkframe.kecamatan2.unique()],
		'actor_s1_tp': [translate_actor(x) for x in snpkframe.actor_s1_tp.unique()],
		'actor_s2_tp': [translate_actor(x) for x in snpkframe.actor_s2_tp.unique()],
		'weapon_1': [translate_weapon(x) for x in snpkframe.weapon_1.unique()],
		'weapon_2': [translate_weapon(x) for x in snpkframe.weapon_2.unique()],
		'tp_kek1_new': [translate_tipe_kekerasan(x) for x in snpkframe.tp_kek1_new.unique()],
		'ben_kek1': [translate_bentuk_kekerasan(x) for x in snpkframe.ben_kek1.unique()],
		'ben_kek2': [translate_bentuk_kekerasan(x) for x in snpkframe.ben_kek2.unique()],
	}

	data = json.dumps(data)

	return render_template('selection.html', rows=data)

@app.route('/seleksi_data', methods=['GET', 'POST'])
def show_selection():
	merge_rows = []

	for filename in request.args.getlist('filename'):
		merge_rows.append(pd.read_csv(join(csv_path, filename), encoding='ISO-8859-1', low_memory=False))

	snpkframe = pd.concat(merge_rows)

	dimensi1_key = request.form.get('dimensi1_key')
	dimensi1 = request.form.get('dimensi1')

	data = {
		'dimensi1_key': request.form.get('dimensi1_key'),
		'dimensi1': request.form.get('dimensi1')
	}

	return render_template('show_selection.html', data=data)

@app.route('/selection')
def load_selection():
	return render_template('selection.html')

@app.route('/login')
def login():
	return render_template('login.html')

if __name__ == '__main__':
	host = environ.get('APP_HOST', '0.0.0.0')
	port = int(environ.get('APP_PORT', 5000))
	debug = bool(int(environ.get('APP_DEBUG', 1)))

	app.secret_key = 'super secret key'

	app.run(host=host,
		port=port,
		debug=debug)

def classifier(row):
	if row["kil_f"] > 0 or row["inj_f"] > 0 or row["kid_f"] > 0 or row["sex_f"] > 0:
		return "KtP"
	else:
		return "Tidak"