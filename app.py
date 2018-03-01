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

from util import translate_bulan, translate_actor, translate_weapon, translate_jenis_kek, translate_tipe_kekerasan, translate_bentuk_kekerasan, translate_meta_kekerasan

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

	kek_all = ['Terbunuh','Luka-Luka','Penculikan','Pelecehan Seksual','Bangunan Rusak']
	kek_all_key = ['kil_total','inj_total','kidnap_tot','sex_as_tot','build_dmg_total']
	kek_f = ['Perempuan Terbunuh','Perempuan Luka-Luka','Penculikan Perempuan','Pelecehan Seksual Perempuan']
	kek_f_key = ['kil_f','inj_f','kid_f','sex_f','build_dmg_total']

	data = {
		'tahun': [x for x in snpkframe.tahun.unique()],
		'bulan_val': [x for x in snpkframe.bulan.unique()],
		'provinsi': [x for x in snpkframe.provinsi.unique()],
		'kabupaten': [x for x in snpkframe.kabupaten.unique()],
		'kek_all': [x for x in kek_all],
		'kek_all_key': [x for x in kek_all_key],
		'kek_f': [x for x in kek_f],
		'kek_f_key': [x for x in kek_f_key],
		'actor_s1_val': [x for x in snpkframe.actor_s1_tp.unique()],
		'actor_s2_val': [x for x in snpkframe.actor_s2_tp.unique()],
		'weapon_1_val': [x for x in snpkframe.weapon_1.unique()],
		'weapon_2_val': [x for x in snpkframe.weapon_2.unique()],
		'jenis_kek_val': [x for x in snpkframe.jenis_kek.unique()],
		'tp_kek1_val': [x for x in snpkframe.tp_kek1_new.unique()],
		'ben_kek1_val': [x for x in snpkframe.ben_kek1.unique()],
		'meta_kek_val': [x for x in snpkframe.meta_tp_kek1_new.unique()],
		'bulan': [translate_bulan(x) for x in snpkframe.bulan.unique()],
		'actor_s1_tp': [translate_actor(x) for x in snpkframe.actor_s1_tp.unique()],
		'actor_s2_tp': [translate_actor(x) for x in snpkframe.actor_s2_tp.unique()],
		'weapon_1': [translate_weapon(x) for x in snpkframe.weapon_1.unique()],
		'weapon_2': [translate_weapon(x) for x in snpkframe.weapon_2.unique()],
		'jenis_kek': [translate_jenis_kek(x) for x in snpkframe.jenis_kek.unique()],
		'tp_kek1_new': [translate_tipe_kekerasan(x) for x in snpkframe.tp_kek1_new.unique()],
		'ben_kek1': [translate_bentuk_kekerasan(x) for x in snpkframe.ben_kek1.unique()],
		'meta_kek': [translate_meta_kekerasan(x) for x in snpkframe.meta_tp_kek1_new.unique()]
	}

	data = json.dumps(data)

	return render_template('selection.html', rows=data)

@app.route('/seleksi_data', methods=['GET', 'POST'])
def show_selection():
	con = []
	# merge_rows = []

	# for filename in request.args.getlist('filename'):
	# 	merge_rows.append(pd.read_csv(join(csv_path, filename), encoding='ISO-8859-1', low_memory=False))

	# snpkframe = pd.concat(merge_rows)

	dimensi1_key = request.form.get('dimensi1_key')
	dimensi1 = request.form.get('dimensi1')	
	dimensi2_key = request.form.get('dimensi2_key')
	dimensi2 = request.form.get('dimensi2')	
	dimensi3_key = request.form.get('dimensi3_key')
	dimensi3 = request.form.get('dimensi3')	
	dimensi4_key = request.form.get('dimensi4_key')
	dimensi4 = request.form.get('dimensi4')	
	dimensi5_key = request.form.get('dimensi5_key')
	dimensi5 = request.form.get('dimensi5')	
	dimensi6_key = request.form.get('dimensi6_key')
	dimensi6 = request.form.get('dimensi6')	
	dimensi7_key = request.form.get('dimensi7_key')
	dimensi7 = request.form.get('dimensi7')	
	dimensi8_key = request.form.get('dimensi8_key')
	dimensi8 = request.form.get('dimensi8')	
	dimensi9_key = request.form.get('dimensi9_key')
	dimensi9 = request.form.get('dimensi9')
	minsup1 = request.form.get('minsup-1')
	minconf1 = request.form.get('minconf-1')	
	minsup2 = request.form.get('minsup-2')
	minconf2 = request.form.get('minconf-2')	
	minsup3 = request.form.get('minsup-3')
	minconf3 = request.form.get('minconf-3')

	data = {
		'dimensi1_key': request.form.get('dimensi1_key'),
		'dimensi1': request.form.get('dimensi1'),
		'dimensi2_key': request.form.get('dimensi2_key'),
		'dimensi2': request.form.get('dimensi2'),
		'dimensi3_key': request.form.get('dimensi3_key'),
		'dimensi3': request.form.get('dimensi3'),
		'dimensi4_key': request.form.get('dimensi4_key'),
		'dimensi4': request.form.get('dimensi4'),
		'dimensi5_key': request.form.get('dimensi5_key'),
		'dimensi5': request.form.get('dimensi5'),
		'dimensi6_key': request.form.get('dimensi6_key'),
		'dimensi6': request.form.get('dimensi6'),
		'dimensi7_key': request.form.get('dimensi7_key'),
		'dimensi7': request.form.get('dimensi7'),
		'dimensi8_key': request.form.get('dimensi8_key'),
		'dimensi8': request.form.get('dimensi8'),
		'dimensi9_key': request.form.get('dimensi9_key'),
		'dimensi9': request.form.get('dimensi9'),
		'minsup1': request.form.get('minsup-1'),
		'minconf1': request.form.get('minconf-1'),
		'minsup2': request.form.get('minsup-2'),
		'minconf2': request.form.get('minconf-2'),
		'minsup3': request.form.get('minsup-3'),
		'minconf3': request.form.get('minconf-3')
	}

		#kondisi dimensi 1
	if dimensi1_key == 'tahun':
		con.append('(snpkframe2["tahun"]==' + dimensi1 + ')')
	elif dimensi1_key == 'bulan':
		con.append('(snpkframe2["bulan"]==' + dimensi1 + ')')

	#kondisi dimensi 2
	if dimensi2_key == 'provinsi':
		con.append('(snpkframe2["provinsi"]=="' + dimensi2 + '")')
	elif dimensi2_key == 'kabupaten':
		con.append('(snpkframe2["kabupaten"]=="' + dimensi2 + '")')

		#kondisi dimensi 3
	if dimensi3_key == 'actor1':
		con.append('(snpkframe2["actor_s1_tp"]==' + dimensi3 + ')')
	elif dimensi3_key == 'actor2':
		con.append('(snpkframe2["actor_s2_tp"]==' + dimensi3 + ')')

		#kondisi dimensi 4
	if dimensi4_key == 'dampak-all':
		con.append('(snpkframe2["' + dimensi4 + '"] > 0)')
	elif dimensi4_key == 'dampak-f':
		con.append('(snpkframe2["' + dimensi4 + '"] > 0)')

		#kondisi dimensi 5
	if dimensi5_key == 'weapon_1':
		con.append('(snpkframe2["weapon_1"]==' + dimensi5 + ')')
	elif dimensi5_key == 'weapon_2':
		con.append('(snpkframe2["weapon_2"]==' + dimensi5 + ')')

		#kondisi dimensi 6
	if dimensi6_key == 'jenis_kek':
		con.append('(snpkframe2["jenis_kek"]==' + dimensi6 + ')')

		#kondisi dimensi 7
	if dimensi7_key == 'tp_kek_new':
		con.append('(snpkframe2["tp_kek_new"]==' + dimensi7 + ')')

		#kondisi dimensi 8
	if dimensi8_key == 'ben_kek':
		con.append('(snpkframe2["ben_kek1"]==' + dimensi8 + ')')

		#kondisi dimensi 9
	if dimensi9_key == 'meta_kek':
		con.append('(snpkframe2["meta_tp_kek1_new"]==' + dimensi9 + ')')

	separator = " & ";
	data_condition = separator.join(con)

	return render_template('show_selection.html', data=data_condition)

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