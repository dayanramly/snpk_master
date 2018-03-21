from flask import Flask, render_template, redirect, url_for, request, flash
from os import environ, listdir, remove
from os.path import isfile, join
from werkzeug.utils import secure_filename
from pandas import DataFrame, read_csv
from itertools import combinations
from sklearn.preprocessing import LabelEncoder, LabelBinarizer
from json2html import *
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

def jsonDefault(object):
    return object.__dict__
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
		'row_total': len(snpkframe.index),
		'url_path': request.args.getlist('filename')
	}

	data = json.dumps(data, default=jsonDefault)

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
	con_dimensi_enc = []

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

	get_data = {
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

	datas = json.dumps(get_data)

	#kondisi dimensi 1
	if dimensi1_key:
		if dimensi1_key == 'tahun':
			if dimensi1 != 'all':
				con.append('(snpkframe2["tahun"]==' + dimensi1 + ')')
			else:
				con.append('(snpkframe2["tahun"].notnull())')
			con_dimensi.append('"tahun"')
			con_dimensi_enc.append('"1-" + snpkframe3["tahun"].astype(str)')
		elif dimensi1_key == 'bulan':
			if dimensi1 != 'all':
				con.append('(snpkframe2["bulan"]==' + dimensi1 + ')')
			else:
				con.append('(snpkframe2["bulan"].notnull())')
			con.append('(snpkframe2["tahun"].notnull())')
			con_dimensi.append('"tahun","bulan"')
			con_dimensi_enc.append('"1-" + snpkframe3["tahun"].astype(str) + "-" + snpkframe3["bulan"].astype(str)')  
		else:
			con_dimensi.append('"tahun","bulan"')
			con_dimensi_enc.append('"1-" + snpkframe3["tahun"].astype(str) + "-" + snpkframe3["bulan"].astype(str)')

	#kondisi dimensi 2
	if dimensi2_key:
		if dimensi2_key == 'provinsi':
			if dimensi2 != 'all':
				con.append('(snpkframe2["provinsi"]=="' + dimensi2 + '")')
			else:
				con.append('(snpkframe2["provinsi"].notnull())')
			con_dimensi.append('"provinsi"')
			con_dimensi_enc.append('"2-" + snpkframe3["provinsi"].astype(str)')
		elif dimensi2_key == 'kabupaten':
			if dimensi2 != 'all':
				con.append('(snpkframe2["kabupaten"]=="' + dimensi2 + '")')
			else:
				con.append('(snpkframe2["kabupaten"].notnull())')
			con.append('(snpkframe2["provinsi"].notnull())')
			con_dimensi.append('"provinsi","kabupaten"')
			con_dimensi_enc.append('"2-" + snpkframe3["provinsi"].astype(str) + "-" + snpkframe3["kabupaten"].astype(str)')
		else:
			con_dimensi.append('"provinsi","kabupaten"')
			con_dimensi_enc.append('"2-" + snpkframe3["provinsi"].astype(str) + "-" + snpkframe3["kabupaten"].astype(str)')

	#kondisi dimensi 3
	if dimensi3_key:
		if dimensi3_key == 'actor1':
			if dimensi3 != 'all':
				con.append('(snpkframe2["actor_s1_tp"]==' + dimensi3 + ')')
			else:
				con.append('(snpkframe2["actor_s1_tp"].notnull())')
			con_dimensi.append('"actor_s1_tp"')
			con_dimensi_enc.append('"3-" + snpkframe3["actor_s1_tp"].astype(str)')
		elif dimensi3_key == 'actor2':
			if dimensi3 != 'all':
				con.append('(snpkframe2["actor_s2_tp"]==' + dimensi3 + ')')
			else:
				con.append('(snpkframe2["actor_s1_tp"].notnull())')
			con.append('(snpkframe2["actor_s1_tp"].notnull())')
			con_dimensi.append('"actor_s1_tp","actor_s2_tp"')
			con_dimensi_enc.append('"3-" + snpkframe3["actor_s1_tp"].astype(str) + "-" + snpkframe3["actor_s2_tp"].astype(str)')
		else:
			con_dimensi.append('"actor_s1_tp","actor_s2_tp"')
			con_dimensi_enc.append('"3-" + snpkframe3["actor_s1_tp"].astype(str) + "-" + snpkframe3["actor_s2_tp"].astype(str)')

	# kondisi dimensi 4
	if dimensi4_key:
		if dimensi4_key == 'dampak-all':
			if dimensi4 != 'all':
				con.append('(snpkframe2["' + dimensi4 + '"] > 0)')
				con_dimensi_enc.append('"4-" + snpkframe3["' + dimensi4 + '"].astype(str)')
				con_dimensi.append('"'+ dimensi4 + '"')
			else:
				con.append('(snpkframe2["kil_total"].notnull())')
				con.append('(snpkframe2["inj_total"].notnull())')
				con.append('(snpkframe2["kidnap_tot"].notnull())')
				con.append('(snpkframe2["sex_as_tot"].notnull())')
				con_dimensi.append('"kil_total"')
				con_dimensi.append('"inj_total"')
				con_dimensi.append('"kidnap_tot"')
				con_dimensi.append('"sex_as_tot"')
				con_dimensi_enc.append('"4-" + snpkframe3["kil_total"].astype(str) + "-" + snpkframe3["inj_total"].astype(str)+ "-" + snpkframe3["kidnap_tot"].astype(str) + "-" + snpkframe3["sex_as_tot"].astype(str)')
			
		elif dimensi4_key == 'dampak-f':
			if dimensi4 != 'all':
				con.append('(snpkframe2["' + dimensi4 + '"] > 0)')
				con_dimensi.append('"'+ dimensi4 + '"')
				con_dimensi_enc.append('"4-" + snpkframe3["' + dimensi4 + '"].astype(str)')
			else:
				con.append('(snpkframe2["kil_f"].notnull())')
				con.append('(snpkframe2["inj_f"].notnull())')
				con.append('(snpkframe2["kid_f"].notnull())')
				con.append('(snpkframe2["sex_f"].notnull())')
				con_dimensi.append('"kil_f"')
				con_dimensi.append('"inj_f"')
				con_dimensi.append('"kid_f"')
				con_dimensi.append('"sex_f"')
				con_dimensi_enc.append('"4-" + snpkframe3["kil_f"].astype(str) + "-" + snpkframe3["inj_f"].astype(str)+ "-" + snpkframe3["kid_f"].astype(str) + "-" + snpkframe3["sex_f"].astype(str)')
		else:
			con_dimensi.append('"kil_total","kil_f","inj_total","inj_f","kidnap_tot","kid_f","sex_as_tot","sex_f"')
			con_dimensi_enc.append('"4-" + snpkframe3["kil_total"].astype(str) + "-" + snpkframe3["kil_f"].astype(str)+ "-" + snpkframe3["inj_total"].astype(str)+ "-" + snpkframe3["inj_f"].astype(str) + "-" + snpkframe3["kidnap_tot"].astype(str) + "-" + snpkframe3["kid_f"].astype(str) + snpkframe3["sex_as_tot"].astype(str) + "-" + snpkframe3["sex_f"].astype(str)')

	#kondisi dimensi 5
	if dimensi5_key:
		if dimensi5_key == 'weapon_1':
			if dimensi5 != 'all':
				con.append('(snpkframe2["weapon_1"]==' + dimensi5 + ')')
			else:
				con.append('(snpkframe2["weapon_1"].notnull())')
			con_dimensi.append('"weapon_1"')
			con_dimensi_enc.append('"5-" + snpkframe3["weapon_1"].astype(str)')
		elif dimensi5_key == 'weapon_2':
			if dimensi5 != 'all':
				con.append('(snpkframe2["weapon_2"]==' + dimensi5 + ')')
			else:
				con.append('(snpkframe2["weapon_2"].notnull())')
			con_dimensi.append('"weapon_1","weapon_2"')
			con_dimensi_enc.append('"5-" + snpkframe3["weapon_1"].astype(str) + "-" + snpkframe3["weapon_2"].astype(str)')
		else:
			con_dimensi.append('"weapon_1","weapon_2"')
			con_dimensi_enc.append('"5-" + snpkframe3["weapon_1"].astype(str) + "-" + snpkframe3["weapon_2"].astype(str)')

	#kondisi dimensi 6
	if dimensi6_key:
		if dimensi6_key == 'jenis_kek':
			if dimensi6 != 'all':
				con.append('(snpkframe2["jenis_kek"]==' + dimensi6 + ')')
			else:
				con.append('(snpkframe2["jenis_kek"].notnull())')
		con_dimensi.append('"jenis_kek"')
		con_dimensi_enc.append('"6-" + snpkframe3["jenis_kek"].astype(str)')

	#kondisi dimensi 7
	if dimensi7_key:
		if dimensi7_key == 'tp_kek_new':
			if dimensi7 != 'all':
				con.append('(snpkframe2["tp_kek1_new"]==' + dimensi7 + ')')
			else:
				con.append('(snpkframe2["tp_kek1_new"].notnull())')
		con_dimensi.append('"tp_kek1_new"')
		con_dimensi_enc.append('"7-" + snpkframe3["tp_kek1_new"].astype(str)')

	#kondisi dimensi 8
	if dimensi8_key:
		if dimensi8_key == 'ben_kek':
			if dimensi8 != 'all':
				con.append('(snpkframe2["ben_kek1"]==' + dimensi8 + ')')
			else:
				con.append('(snpkframe2["ben_kek1"].notnull())')
		con_dimensi.append('"ben_kek1"')
		con_dimensi_enc.append('"8-" + snpkframe3["ben_kek1"].astype(str)')

	#kondisi dimensi 9
	if dimensi9_key:
		if dimensi9_key == 'meta_kek':
			if dimensi9 != 'all':
				con.append('(snpkframe2["meta_tp_kek1_new"]==' + dimensi9 + ')')
			else:
				con.append('(snpkframe2["meta_tp_kek1_new"].notnull())')
		con_dimensi.append('"meta_tp_kek1_new"')
		con_dimensi_enc.append('"9-" + snpkframe3["meta_tp_kek1_new"].astype(str)')

	#join array dan konversi ke string
	sep = " & ";
	sep_dim = ","
	rules_filter = sep.join(con)
	rules_dimensi = sep_dim.join(con_dimensi)

	print_con = {
		'con': con,
		'con_dim': con_dimensi
	}

	#seleksi kolom sebelum difilter
	snpkframe2 = eval('snpkframe[['+ rules_dimensi +']]')
	row_total = len(snpkframe2.index)
	# min_sup = int((float(minsup1) / 100) * row_total)
	if minsup1:
		min_sup = int((float(minsup1) / 100) * row_total)
	else:
		min_sup = 10

	if minconf1:
		min_conf = float(minconf1) / 100
	else:
		min_conf = 0

	# print_supp = {
	# 	'min_sup': min_sup,
	# 	'min_conf': min_conf
	# }

	#seleksi data dengan kriteria yang ditentukan
	if rules_filter == '':
		snpkframe3 = snpkframe2.copy()
	else:
		snpkframe3 = eval('snpkframe2['+ rules_filter +']')


	for index, x in enumerate(con_dimensi_enc):
	    snpkframe3["dim"+str(index+1)] = eval(x)

	snpkframe31 = snpkframe3.loc[:, snpkframe3.columns.to_series().str.contains('dim').tolist()]

	json_before_fpgrowth = snpkframe31.to_json(orient='split')

	#convert into matrix
	convMatrix = snpkframe31.as_matrix()

	#mencari pattern pada data kek_uji
	patterns = pyfpgrowth.find_frequent_patterns(convMatrix, min_sup)

	#mencari rules dari pattern yang telah dibuat
	rules = pyfpgrowth.generate_association_rules(patterns, min_conf)

	if rules:
		dim1_list=list(rules.keys())
		df_key = pd.DataFrame(dim1_list)
		total_columns = len(df_key.columns)
		new_cols = ['key' + str(i) for i in df_key.columns]
		df_key.columns = new_cols[:total_columns]

	
		dim2_list=list(rules.values())
		df_values = pd.DataFrame(dim2_list)
		df_values.rename(columns={0:'first'}, inplace=True)
		df_values.rename(columns={1:'confident'}, inplace=True)

		df_values['first'] = df_values['first'].astype(str).str.strip('()')
		df_values_key = df_values['first'].str.split(',', expand=True)
		df_values_key = df_values_key.replace('', "None")

		df_values_conf = df_values['confident']
		df_values_key = df_values_key.apply(lambda x: x.str.strip("'")).apply(lambda x: x.str.strip(" '"))

		total_columns_value = len(df_values_key.columns)
		new_cols = ['values' + str(i) for i in df_values_key.columns] 
		df_values_key.columns = new_cols[:total_columns_value]
	
		result_join = pd.concat([df_key, df_values_key, df_values_conf], axis=1, join_axes=[df_key.index])

		def f(row):
			for col in row.index:
				if (row[col] != None) & (not isinstance(row[col], float)):
					if row[col][0] == '2':
						a = row[col].split("-")
						return a[1]
					else:
						return "Nasional"

		result_join['Result'] = result_join.apply(f, axis=1)

		group_true = result_join.Result.notnull()
		filter_result = result_join[group_true]

		html_filter_result = filter_result.groupby(['Result'])
		# outs_filter_result = filter_result.to_json(orient='split')

		# test_result = filter_result.to_json(orient='split')

		# out_filter_result = filter_result.groupby('Result').apply(lambda x: x.to_json(orient='records'))

		out_filter_result = (filter_result.groupby(['Result'])
		 .apply(lambda x: x.to_dict('r'))
		 .reset_index()
		 .rename(columns={0:'Value'})
		 .to_json(orient='records'))

		print_html = json2html.convert(json = out_filter_result, table_attributes="id=\"info-table\" class=\"table table-bordered table-hover\"")
	else:
		print_html = "Tidak ada rules"

	# data_html = result_join.to_html(classes="table table-data")
	# data_html = data_html.replace('NaN', '')

	# filter_result = json.dumps(filter_result)
	# return redirect(url_for('load_selection', snpkframe=data_html))
	return render_template('show_selection.html', data=print_html)


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