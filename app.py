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
		'meta_kek': [translate_meta_kekerasan(x) for x in snpkframe.meta_tp_kek1_new.unique()],
		'url_path': request.args.getlist('filename')
	}

	data = json.dumps(data)

	return render_template('selection.html', rows=data)

@app.route('/seleksi_data', methods=['GET', 'POST'])
def show_selection():
	merge_rows = []
	file_select = str(request.form.get('file_selected'))
	array_select = file_select.split(',')

	for filename in array_select:
		merge_rows.append(pd.read_csv(join(upload_path, filename), encoding='ISO-8859-1', low_memory=False))

	snpkframe = pd.concat(merge_rows)

	#cleaning data - remove not useful column
	snpkframe = snpkframe.drop(['area','tanggal_kejadian','quarter','idkejadian','kodebpsprop','kodebpskab','kodebpskec1','kecamatan1','kodebpskec2','kecamatan2','desa1','desa2','desa3','actor_s1_tp_o','actor_s1_tot','actor_s2_tp_o','actor_s2_tot','int1','int2','int1_res','int2_res','int1_o','int2_o','int1_res_o','int2_res_o','build_dmg_total','bdg_des','oth_impact','weapon_oth','isu_indv','tp_kek1_o','ben_kek1_o','ben_kek2','ben_kek2_o','insd_desc','full_coverage','s1','s2','s3','s4','s5','s6','s7','s8','weapon','wpnfarm','wpnfarmman','wpnfarmhmde','wpnexpl','wpnshrp','wpnblunt','wpnfire','intervention','intvnrsecforfrml','intvnrtni','intvnrpol','intvnrbrimob','intvnrcvln','intvntnressucces','intvntnviolup','actcountrelormas','actcountparpol','actcountseprtst','actcountgov','actcountstudents','secvssec','onewayformconf','twowayformconf','death1','death3','death5','death10','largeinc','evperiod','pevperiod','preevperiod','ev2period','pev2period','create','last_update'],axis=1) 

	con = []
	con_dimensi = []

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
		'minconf1': request.form.get('minconf-1')
	}

	#kondisi dimensi 1
	if dimensi1_key == 'tahun':
	    con.append('(snpkframe2["tahun"]==' + dimensi1 + ')')
	    con_dimensi.append('"tahun"')
	elif dimensi1_key == 'bulan':
	    con.append('(snpkframe2["tahun"].notnull())')
	    con.append('(snpkframe2["bulan"]==' + dimensi1 + ')')
	    con_dimensi.append('"tahun","bulan"')
	else:
	    con_dimensi.append('"tahun","bulan"')

	#kondisi dimensi 2
	if dimensi2_key == 'provinsi':
	    con.append('(snpkframe2["provinsi"]=="' + dimensi2 + '")')
	    con_dimensi.append('"provinsi"')
	elif dimensi2_key == 'kabupaten':
	    con.append('(snpkframe2["provinsi"].notnull())')
	    con.append('(snpkframe2["kabupaten"]=="' + dimensi2 + '")')
	    con_dimensi.append('"provinsi","kabupaten"')
	else:
	    con_dimensi.append('"provinsi","kabupaten"')

	#kondisi dimensi 3
	if dimensi3_key == 'actor1':
	    con.append('(snpkframe2["actor_s1_tp"]==' + dimensi3 + ')')
	    con_dimensi.append('"actor_s1_tp"')
	elif dimensi3_key == 'actor2':
	    con.append('(snpkframe2["actor_s1_tp"].notnull())')
	    con.append('(snpkframe2["actor_s2_tp"]==' + dimensi3 + ')')
	    con_dimensi.append('"actor_s1_tp","actor_s2_tp"')
	else:
	    con_dimensi.append('"actor_s1_tp","actor_s2_tp"')

		    # kondisi dimensi 4
	if dimensi4_key == 'dampak-all':
	    con.append('(snpkframe2["' + dimensi4 + '"] > 0)')
	    con_dimensi.append('"'+ dimensi4 + '"')
	elif dimensi4_key == 'dampak-f':
	    con.append('(snpkframe2["' + dimensi4 + '"] > 0)')
	    con_dimensi.append('"'+ dimensi4 + '"')
	else:
	    con_dimensi.append('"kil_total","kil_f","inj_total","inj_f","kidnap_tot","kid_f","sex_as_tot","sex_f"')

	#kondisi dimensi 5
	if dimensi5_key == 'weapon_1':
	    con.append('(snpkframe2["weapon_1"]==' + dimensi5 + ')')
	    con_dimensi.append('"weapon_1"')
	elif dimensi5_key == 'weapon_2':
	    con.append('(snpkframe2["weapon_2"]==' + dimensi5 + ')')
	    con_dimensi.append('"weapon_1","weapon_2"')
	else:
	    con_dimensi.append('"weapon_1","weapon_2"')

	#kondisi dimensi 6
	if dimensi6_key == 'jenis_kek':
	    con.append('(snpkframe2["jenis_kek"]==' + dimensi6 + ')')
	con_dimensi.append('"jenis_kek"')

	#kondisi dimensi 7
	if dimensi7_key == 'tp_kek_new':
	    con.append('(snpkframe2["tp_kek1_new"]==' + dimensi7 + ')')
	con_dimensi.append('"tp_kek1_new"')

	#kondisi dimensi 8
	if dimensi8_key == 'ben_kek':
	    con.append('(snpkframe2["ben_kek1"]==' + dimensi8 + ')')
	con_dimensi.append('"ben_kek1"')

	#kondisi dimensi 9
	if dimensi9_key == 'meta_kek':
	    con.append('(snpkframe2["meta_tp_kek1_new"]==' + dimensi9 + ')')
	con_dimensi.append('"meta_tp_kek1_new"')

	#menampilkan array hasil kondisi
	con
	
	#menampilkan array hasil kondisi
	con_dimensi

	#join array dan konversi ke string
	sep = " & ";
	sep_dim = ","
	rules_filter = sep.join(con)
	rules_dimensi = sep_dim.join(con_dimensi)

	#seleksi kolom sebelum difilter
	snpkframe2 = eval('snpkframe[['+ rules_dimensi +']]')

	#seleksi data dengan kriteria yang ditentukan
	if rules_filter == '':
	    snpkframe3 = snpkframe2.copy()
	else:
	    snpkframe3 = eval('snpkframe2['+ rules_filter +']')


	snpkframe3["dim1"] = '1-' + snpkframe3['tahun'].astype(str) + '-' + snpkframe3['bulan'].astype(str)
	snpkframe3["dim2"] = '2-' + snpkframe3['provinsi'].astype(str) + '-' + snpkframe3['kabupaten'].astype(str)
	snpkframe3["dim3"] = '3-' + snpkframe3['actor_s1_tp'].astype(str) + '-' + snpkframe3['actor_s1_tp'].astype(str)

	snpkframe31 = snpkframe3.loc[:, snpkframe3.columns.to_series().str.contains('dim').tolist()]

	#convert into matrix
	convMatrix = snpkframe31.as_matrix()

	#mencari pattern pada data kek_uji
	patterns = pyfpgrowth.find_frequent_patterns(convMatrix, 10)

	#mencari rules dari pattern yang telah dibuat
	rules = pyfpgrowth.generate_association_rules(patterns, 0.3)

	dim1_list=list(rules.keys())
	df_key = pd.DataFrame(dim1_list)
	total_columns = len(df_key.columns)
	new_cols = ['key' + str(i) for i in df_key.columns]
	df_key.columns = new_cols[:total_columns]

	dim2_list=list(rules.values())
	df_values = pd.DataFrame(dim2_list)
	total_columns_value = len(df_values.columns)
	new_cols = ['values' + str(i) for i in df_values.columns] 
	df_values.columns = new_cols[:total_columns_value]

	for col in df_values.columns.values:
	    # Encoding only categorical variables
	    if df_values[col].dtypes=='object':
	        df_values[col] = df_values[col].astype(str).map(lambda x: x.lstrip("('").rstrip("',)"))
	        df_values[col].astype(object)

	result_join = pd.concat([df_key, df_values], axis=1, join_axes=[df_key.index])

	def f(row):
	    for col in row.index:
	        if (row[col] != None) & (not isinstance(row[col], float)):
	            if row[col][0] == '2':
	                a = row[col].split("-")
	                return a[1] 
	result_join['Result'] = result_join.apply(f, axis=1)

	group_true = result_join.Result.notnull()
	filter_result = result_join[group_true]
	

	# data_html = result_join.to_html(classes="table table-data")
	# data_html = data_html.replace('NaN', '')

	# patterns = json.dumps(patterns)
	# return redirect(url_for('load_selection', snpkframe=data_html))
	return render_template('show_selection.html', data=filter_result.to_json(orient='split'))


	# return json.dumps(merge_rows)

	# return render_template('show_selection.html', data=snpkframe)

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