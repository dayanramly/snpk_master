import json
from ast import literal_eval
from os import environ, listdir, remove
from os.path import isfile, join

import pandas as pd
import numpy as np
import pyfpgrowth
import plotly
import plotly.plotly as py
import plotly.graph_objs as gox
from flask import Flask, render_template, redirect, url_for, request, flash
from json2html import *
from werkzeug.utils import secure_filename
from itertools import chain
from itertools import combinations
from collections import defaultdict
from plotly.graph_objs import *
import time
import math

from util import translate_bulan, translate_actor, translate_weapon, translate_jenis_kek, translate_tipe_kekerasan, \
	translate_bentuk_kekerasan, translate_meta_kekerasan

app = Flask('snpk', template_folder='templates')
app.config['UPLOAD_FOLDER'] = 'uploadfiles'
app.config['SESSION_TYPE'] = 'filesystem'
upload_path = join(app.config['UPLOAD_FOLDER'], 'csv')

ALLOWED_EXTENSIONS = ['csv']


def allowed_file(filename):
	return '.' in filename and \
		   filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

	return redirect(url_for('main'))


@app.route('/')
def welcome():
	return render_template('login.html')

@app.route('/start')
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

	#data yang diambil hanya data kekerasan terhadap perempuan (EKSTRAKSI DATA)
	snpkframe = snpkframe.loc[(snpkframe["kil_f"] > 0) | (snpkframe["inj_f"] > 0) | (snpkframe["kid_f"] > 0) | (snpkframe["sex_f"] > 0)]

	kek_all = ['Terbunuh', 'Luka-Luka', 'Penculikan', 'Pelecehan Seksual', 'Bangunan Rusak']
	kek_all_key = ['kil_total', 'inj_total', 'kidnap_tot', 'sex_as_tot', 'build_dmg_total']
	kek_f = ['Perempuan Terbunuh', 'Perempuan Luka-Luka', 'Penculikan Perempuan', 'Pelecehan Seksual Perempuan']
	kek_f_key = ['kil_f', 'inj_f', 'kid_f', 'sex_f', 'build_dmg_total']

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

	data = json.dumps(data)

	return render_template('selection.html', rows=data)


@app.route('/seleksi_data', methods=['GET', 'POST'])
def show_selection():

	start_time = time.time()
	merge_rows = []
	file_select = str(request.form.get('file_selected'))
	array_select = file_select.split(',')

	for filename in array_select:
		merge_rows.append(pd.read_csv(join(upload_path, filename), encoding='ISO-8859-1', low_memory=False))

	snpkframe = pd.concat(merge_rows)

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

	if request.form.get('action') == 'MultiDimension':
		# cleaning data - remove not useful column
		snpkframe = snpkframe.drop(
			['area', 'tanggal_kejadian', 'quarter', 'idkejadian', 'kodebpsprop', 'kodebpskab', 'kodebpskec1', 'kecamatan1',
			 'kodebpskec2', 'kecamatan2', 'desa1', 'desa2', 'desa3', 'actor_s1_tp_o', 'actor_s1_tot', 'actor_s2_tp_o',
			 'actor_s2_tot', 'int1', 'int2', 'int1_res', 'int2_res', 'int1_o', 'int2_o', 'int1_res_o', 'int2_res_o',
			 'build_dmg_total', 'bdg_des', 'oth_impact', 'weapon_oth', 'isu_indv', 'tp_kek1_o', 'ben_kek1_o', 'ben_kek2',
			 'ben_kek2_o', 'insd_desc', 'full_coverage', 's1', 's2', 's3', 's4', 's5', 's6', 's7', 's8', 'weapon',
			 'wpnfarm', 'wpnfarmman', 'wpnfarmhmde', 'wpnexpl', 'wpnshrp', 'wpnblunt', 'wpnfire', 'intervention',
			 'intvnrsecforfrml', 'intvnrtni', 'intvnrpol', 'intvnrbrimob', 'intvnrcvln', 'intvntnressucces',
			 'intvntnviolup', 'actcountrelormas', 'actcountparpol', 'actcountseprtst', 'actcountgov', 'actcountstudents',
			 'secvssec', 'onewayformconf', 'twowayformconf', 'death1', 'death3', 'death5', 'death10', 'largeinc',
			 'evperiod', 'pevperiod', 'preevperiod', 'ev2period', 'pev2period', 'create', 'last_update'], axis=1)

		#data yang diambil hanya data kekerasan terhadap perempuan (EKSTRAKSI DATA)
		snpkframe = snpkframe.loc[(snpkframe["kil_f"] > 0) | (snpkframe["inj_f"] > 0) | (snpkframe["kid_f"] > 0) | (snpkframe["sex_f"] > 0)]

		def clean_dampak(value):
			if value > 0:
				return 1
			else:
				return 0

		#konversi biner data dimensi 4
		snpkframe["kil_total"] = snpkframe["kil_total"].apply(clean_dampak)
		snpkframe["kil_f"] = snpkframe["kil_f"].apply(clean_dampak)
		snpkframe["inj_total"] = snpkframe["inj_total"].apply(clean_dampak)
		snpkframe["inj_f"] = snpkframe["inj_f"].apply(clean_dampak)
		snpkframe["kidnap_tot"] = snpkframe["kidnap_tot"].apply(clean_dampak)
		snpkframe["kid_f"] = snpkframe["kid_f"].apply(clean_dampak)
		snpkframe["sex_as_tot"] = snpkframe["sex_as_tot"].apply(clean_dampak)
		snpkframe["sex_f"] = snpkframe["sex_f"].apply(clean_dampak)

		#initiate new array
		con = []
		con_dimensi = []
		con_dimensi_enc = []

		# kondisi dimensi 1
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

		# kondisi dimensi 2
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
				con_dimensi_enc.append(
					'"2-" + snpkframe3["provinsi"].astype(str) + "-" + snpkframe3["kabupaten"].astype(str)')
			else:
				con_dimensi.append('"provinsi","kabupaten"')
				con_dimensi_enc.append(
					'"2-" + snpkframe3["provinsi"].astype(str) + "-" + snpkframe3["kabupaten"].astype(str)')

		# kondisi dimensi 3
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
				con_dimensi_enc.append(
					'"3-" + snpkframe3["actor_s1_tp"].astype(str) + "-" + snpkframe3["actor_s2_tp"].astype(str)')
			else:
				con_dimensi.append('"actor_s1_tp","actor_s2_tp"')
				con_dimensi_enc.append(
					'"3-" + snpkframe3["actor_s1_tp"].astype(str) + "-" + snpkframe3["actor_s2_tp"].astype(str)')

		# kondisi dimensi 4
		if dimensi4_key:
			if dimensi4_key == 'dampak-all':
				if dimensi4 != 'all':
					con.append('(snpkframe2["' + dimensi4 + '"] > 0)')
					con_dimensi_enc.append('"4-" + snpkframe3["' + dimensi4 + '"].astype(str)')
					con_dimensi.append('"' + dimensi4 + '"')
				else:
					con.append('(snpkframe2["kil_total"].notnull())')
					con.append('(snpkframe2["inj_total"].notnull())')
					con.append('(snpkframe2["kidnap_tot"].notnull())')
					con.append('(snpkframe2["sex_as_tot"].notnull())')
					con_dimensi.append('"kil_total"')
					con_dimensi.append('"inj_total"')
					con_dimensi.append('"kidnap_tot"')
					con_dimensi.append('"sex_as_tot"')
					con_dimensi_enc.append(
						'"4-" + snpkframe3["kil_total"].astype(str) + "-" + snpkframe3["inj_total"].astype(str)+ "-" + snpkframe3["kidnap_tot"].astype(str) + "-" + snpkframe3["sex_as_tot"].astype(str)')

			elif dimensi4_key == 'dampak-f':
				if dimensi4 != 'all':
					con.append('(snpkframe2["' + dimensi4 + '"] > 0)')
					con_dimensi.append('"' + dimensi4 + '"')
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
					con_dimensi_enc.append(
						'"4-" + snpkframe3["kil_f"].astype(str) + "-" + snpkframe3["inj_f"].astype(str)+ "-" + snpkframe3["kid_f"].astype(str) + "-" + snpkframe3["sex_f"].astype(str)')
			else:
				con_dimensi.append('"kil_total","kil_f","inj_total","inj_f","kidnap_tot","kid_f","sex_as_tot","sex_f"')
				con_dimensi_enc.append(
					'"4-" + snpkframe3["kil_total"].astype(str) + "-" + snpkframe3["kil_f"].astype(str)+ "-" + snpkframe3["inj_total"].astype(str)+ "-" + snpkframe3["inj_f"].astype(str) + "-" + snpkframe3["kidnap_tot"].astype(str) + "-" + snpkframe3["kid_f"].astype(str) + "-" + snpkframe3["sex_as_tot"].astype(str) + "-" + snpkframe3["sex_f"].astype(str)')

		# kondisi dimensi 5
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
				con_dimensi_enc.append(
					'"5-" + snpkframe3["weapon_1"].astype(str) + "-" + snpkframe3["weapon_2"].astype(str)')
			else:
				con_dimensi.append('"weapon_1","weapon_2"')
				con_dimensi_enc.append(
					'"5-" + snpkframe3["weapon_1"].astype(str) + "-" + snpkframe3["weapon_2"].astype(str)')

		# kondisi dimensi 6
		if dimensi6_key:
			if dimensi6_key == 'jenis_kek':
				if dimensi6 != 'all':
					con.append('(snpkframe2["jenis_kek"]==' + dimensi6 + ')')
				else:
					con.append('(snpkframe2["jenis_kek"].notnull())')
			con_dimensi.append('"jenis_kek"')
			con_dimensi_enc.append('"6-" + snpkframe3["jenis_kek"].astype(str)')
		# kondisi dimensi 7
		if dimensi7_key:
			if dimensi7_key == 'tp_kek_new':
				if dimensi7 != 'all':
					con.append('(snpkframe2["tp_kek1_new"]==' + dimensi7 + ')')
				else:
					con.append('(snpkframe2["tp_kek1_new"].notnull())')
			con_dimensi.append('"tp_kek1_new"')
			con_dimensi_enc.append('"7-" + snpkframe3["tp_kek1_new"].astype(str)')

		# kondisi dimensi 8
		if dimensi8_key:
			if dimensi8_key == 'ben_kek':
				if dimensi8 != 'all':
					con.append('(snpkframe2["ben_kek1"]==' + dimensi8 + ')')
				else:
					con.append('(snpkframe2["ben_kek1"].notnull())')
			con_dimensi.append('"ben_kek1"')
			con_dimensi_enc.append('"8-" + snpkframe3["ben_kek1"].astype(str)')

		# kondisi dimensi 9
		if dimensi9_key:
			if dimensi9_key == 'meta_kek':
				if dimensi9 != 'all':
					con.append('(snpkframe2["meta_tp_kek1_new"]==' + dimensi9 + ')')
				else:
					con.append('(snpkframe2["meta_tp_kek1_new"].notnull())')
			con_dimensi.append('"meta_tp_kek1_new"')
			con_dimensi_enc.append('"9-" + snpkframe3["meta_tp_kek1_new"].astype(str)')

		# join array dan konversi ke string
		sep = " & "
		sep_dim = ","
		rules_filter = sep.join(con)
		rules_dimensi = sep_dim.join(con_dimensi)

		# print_con = {
		# 	'con': con,
		# 	'con_dim': con_dimensi
		# }

		# seleksi kolom sebelum difilter
		snpkframe2 = eval('snpkframe[[' + rules_dimensi + ']]')
		row_total = len(snpkframe2.index)
		# min_sup = int((float(minsup1) / 100) * row_total)
		if minsup1:
			min_sup = int(minsup1)
		# min_sup = int((float(minsup1) / 100) * row_total)
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

		# seleksi data dengan kriteria yang ditentukan
		if rules_filter == '':
			snpkframe3 = snpkframe2.copy()
		else:
			snpkframe3 = eval('snpkframe2[' + rules_filter + ']')

		listgroupby = {}
		for index, x in enumerate(con_dimensi):
			con_split = x.split(',')
			for dim in con_split:
				dim = dim.replace('"', '')
				listgroupby[dim] = eval('snpkframe3["'+dim+'"].groupby(snpkframe3["'+dim+'"]).count()')

		for index, x in enumerate(con_dimensi_enc):
			snpkframe3["dim" + str(index + 1)] = eval(x)

		snpkframe31 = snpkframe3.loc[:, snpkframe3.columns.to_series().str.contains('dim').tolist()]

		# json_before_fpgrowth = snpkframe31.to_json(orient='split')

		# convert into matrix
		convMatrix = snpkframe31.as_matrix()

		# mencari pattern pada data kek_uji
		patterns = pyfpgrowth.find_frequent_patterns(convMatrix, min_sup)

		# mencari rules dari pattern yang telah dibuat
		rules = pyfpgrowth.generate_association_rules(patterns, min_conf)

		if rules:
			total_rules = len(rules)
			dim1_list = list(rules.keys())
			df_key = pd.DataFrame(dim1_list)
			total_columns = len(df_key.columns)
			new_cols = ['key' + str(i) for i in df_key.columns]
			df_key.columns = new_cols[:total_columns]

			df_key_decode = df_key.copy()
			df_key_decode

			for index, row in df_key_decode.iterrows():
				arr = []
				arr_tahun = []
				arr_bulan = []
				arr_loc = []
				arr_kab = []
				arr_act1 = []
				arr_act2 = []
				arr_weap1 = []
				arr_weap2 = []
				arr_jkek = []
				arr_katkek = []
				arr_benkek = []
				arr_metkek = []
			#     print index, row
				for each_col in row:
					if (each_col != None):
						splitCol = each_col.split("-")
						if len(splitCol) == 2:
							if (splitCol[0] == '1'):
								arr.append("pada tahun " + splitCol[1])
								arr_tahun.append(splitCol[1])
							elif (splitCol[0] == '2'):
								arr.append("di provinsi " + splitCol[1])
								arr_loc.append(splitCol[1])
							elif splitCol[0] == '3':
								arr.append("dengan aktor " + translate_actor(int(splitCol[1])))
								arr_act1.append(translate_actor(int(splitCol[1])))
							elif splitCol[0] == '4':
								arr.append("terdapat korban terbunuh, luka-luka, penculikan, pelecehan seksual atau bangunan rusak")
							elif splitCol[0] == '5':
								arr.append("dengan senjata " + translate_weapon(int(splitCol[1])))
								arr_weap1.append(translate_actor(int(splitCol[1])))
							elif splitCol[0] == '6':
								arr.append("dengan jenis kekerasan " + translate_jenis_kek(int(splitCol[1])))
								arr_jkek.append(translate_jenis_kek(int(splitCol[1])))
							elif splitCol[0] == '7':
								arr.append("dengan kategori tipe kekerasan " + translate_tipe_kekerasan(int(splitCol[1])))
								arr_katkek.append(translate_tipe_kekerasan(int(splitCol[1])))
							elif splitCol[0] == '8':
								arr.append("dengan bentuk kekerasan " + translate_bentuk_kekerasan(int(splitCol[1])))
								arr_benkek.append(translate_bentuk_kekerasan(int(splitCol[1])))
							elif splitCol[0] == '9':
								arr.append("dengan meta jenis kekerasan " + translate_meta_kekerasan(int(splitCol[1])))
								arr_metkek.append(translate_meta_kekerasan(int(splitCol[1])))
						elif len(splitCol) == 3:
							if (splitCol[0] == '1'):
								arr.append("pada tahun " + splitCol[1])
								arr.append("bulan " + translate_bulan(int(splitCol[2])))
								arr_tahun.append(splitCol[1])
								arr_bulan.append(translate_bulan(int(splitCol[2])))
							elif (splitCol[0] == '2'):
								arr.append("di provinsi " + splitCol[1])
								arr.append("kabupaten " + splitCol[2])
								arr_loc.append(splitCol[1])
								arr_kab.append(splitCol[2])
							elif splitCol[0] == '3':
								arr.append("dengan aktor 1 " + translate_actor(int(splitCol[1])))
								arr.append("dan aktor 2 " + translate_actor(int(splitCol[2])))
								arr_act1.append(translate_actor(int(splitCol[1])))
								arr_act2.append(translate_actor(int(splitCol[2])))
							elif splitCol[0] == '4':
								arr.append("dengan dampak " + splitCol[1])
								arr.append("dan dampak " + splitCol[2])
							elif splitCol[0] == '5':
								arr.append("dengan senjata 1 " + translate_weapon(int(splitCol[1])))
								arr.append("dan senjata 2 " + translate_weapon(int(splitCol[2])))
								arr_weap1.append(translate_weapon(int(splitCol[1])))
								arr_weap2.append(translate_weapon(int(splitCol[2])))
						elif len(splitCol) == 4:
							arr.append("terdapat korban")
							if splitCol[1] == '1':
								arr.append("terbunuh,")        
							elif splitCol[2] == '1':
								arr.append("luka-luka,")
							elif splitCol[3] == '1':
								arr.append("penculikan,")
							elif splitCol[4] == '1':
								arr.append("pelecehan seksual,")
						elif len(splitCol) == 9:
							arr.append("terdapat korban")
							if splitCol[1] == '1':
								arr.append("terbunuh,")        
							if splitCol[2] == '1':
								arr.append("luka-luka,")
							if splitCol[3] == '1':
								arr.append("penculikan,")
							if splitCol[4] == '1':
								arr.append("pelecehan seksual,")
							if splitCol[5] == '1':
								arr.append("terbunuh berjenis kelamin perempuan,")        
							if splitCol[6] == '1':
								arr.append("luka-luka berjenis kelamin perempuan,")
							if splitCol[7] == '1':
								arr.append("penculikan berjenis kelamin perempuan,")
							if splitCol[8] == '1':
								arr.append("pelecehan seksual berjenis kelamin perempuan,")
								
				combine_arr = ' '.join(arr)
			#     print combine_arr
				df_key_decode.loc[index,'List'] = combine_arr
				
				if arr_tahun:
					df_key_decode.loc[index,'List_tahun'] = ' '.join(arr_tahun)
				if arr_bulan:
					df_key_decode.loc[index,'List_bulan'] = ' '.join(arr_bulan)
				if arr_kab:
					df_key_decode.loc[index,'List_kabupaten'] = ' '.join(arr_kab)
				if arr_act1: 
					df_key_decode.loc[index,'List_act1'] = ' '.join(arr_act1)
				if arr_act2:
					df_key_decode.loc[index,'List_act2'] = ' '.join(arr_act2)
				if arr_weap1: 
					df_key_decode.loc[index,'List_weap1'] = ' '.join(arr_weap1)
				if arr_weap2:
					df_key_decode.loc[index,'List_weap2'] = ' '.join(arr_weap2)
				if arr_jkek:
					df_key_decode.loc[index,'List_jenis_kek'] = ' '.join(arr_jkek)
				if arr_katkek: 
					df_key_decode.loc[index,'List_kat_kek'] = ' '.join(arr_katkek)
				if arr_benkek:
					df_key_decode.loc[index,'List_ben_kek'] = ' '.join(arr_benkek)
				if arr_metkek:
					df_key_decode.loc[index,'List_met_kek'] = ' '.join(arr_metkek)
				if arr_loc:
					df_key_decode.loc[index,'Loc'] = ' '.join(arr_loc)
				else:
					df_key_decode.loc[index,'Loc'] = 'Nasional'
		
		
			dim2_list = list(rules.values())
			df_values = pd.DataFrame(dim2_list)
			df_values.rename(columns={0: 'first'}, inplace=True)
			df_values.rename(columns={1: 'confident'}, inplace=True)

			df_values['first'] = df_values['first'].astype(str).str.strip('()')
			df_values_key = df_values['first'].str.split(',', expand=True)
			df_values_key = df_values_key.replace('', "None")

			df_values_conf = df_values['confident']
			df_values_key = df_values_key.apply(lambda x: x.str.strip("'")).apply(lambda x: x.str.strip(" '"))

			total_columns_value = len(df_values_key.columns)
			new_cols = ['values' + str(i) for i in df_values_key.columns]
			df_values_key.columns = new_cols[:total_columns_value]

			df_values_decode = df_values_key.copy()

			for index, row in df_values_decode.iterrows():
				arr = []
				arr_tahun = []
				arr_bulan = []
				arr_loc = []
				arr_kab = []
				arr_act1 = []
				arr_act2 = []
				arr_weap1 = []
				arr_weap2 = []
				arr_jkek = []
				arr_katkek = []
				arr_benkek = []
				arr_metkek = []
				for each_col in row:
					if (each_col != None):
						splitCol = each_col.split("-")
						if len(splitCol) == 2:
							if (splitCol[0] == '1'):
								arr.append("pada tahun " + splitCol[1])
								arr_tahun.append(splitCol[1])
							elif (splitCol[0] == '2'):
								arr.append("di provinsi " + splitCol[1])
								arr_loc.append(splitCol[1])
							elif splitCol[0] == '3':
								arr.append("dengan aktor " + translate_actor(int(splitCol[1])))
								arr_act1.append(translate_actor(int(splitCol[1])))
							elif splitCol[0] == '4':
								arr.append("terdapat korban terbunuh, luka-luka, penculikan, pelecehan seksual atau bangunan rusak")
							elif splitCol[0] == '5':
								arr.append("dengan senjata " + translate_weapon(int(splitCol[1])))
								arr_weap1.append(translate_actor(int(splitCol[1])))
							elif splitCol[0] == '6':
								arr.append("dengan jenis kekerasan " + translate_jenis_kek(int(splitCol[1])))
								arr_jkek.append(translate_jenis_kek(int(splitCol[1])))
							elif splitCol[0] == '7':
								arr.append("dengan kategori tipe kekerasan " + translate_tipe_kekerasan(int(splitCol[1])))
								arr_katkek.append(translate_tipe_kekerasan(int(splitCol[1])))
							elif splitCol[0] == '8':
								arr.append("dengan bentuk kekerasan " + translate_bentuk_kekerasan(int(splitCol[1])))
								arr_benkek.append(translate_bentuk_kekerasan(int(splitCol[1])))
							elif splitCol[0] == '9':
								arr.append("dengan meta jenis kekerasan " + translate_meta_kekerasan(int(splitCol[1])))
								arr_metkek.append(translate_meta_kekerasan(int(splitCol[1])))
						elif len(splitCol) == 3:
							if (splitCol[0] == '1'):
								arr.append("pada tahun " + splitCol[1])
								arr.append("bulan " + translate_bulan(int(splitCol[2])))
								arr_tahun.append(splitCol[1])
								arr_bulan.append(translate_bulan(int(splitCol[2])))
							elif (splitCol[0] == '2'):
								arr.append("di provinsi " + splitCol[1])
								arr.append("kabupaten " + splitCol[2])
								arr_loc.append(splitCol[1])
								arr_kab.append(splitCol[2])
							elif splitCol[0] == '3':
								arr.append("dengan aktor 1 " + translate_actor(int(splitCol[1])))
								arr.append("dan aktor 2 " + translate_actor(int(splitCol[2])))
								arr_act1.append(translate_actor(int(splitCol[1])))
								arr_act2.append(translate_actor(int(splitCol[2])))
							elif splitCol[0] == '4':
								arr.append("dengan dampak " + splitCol[1])
								arr.append("dan dampak " + splitCol[2])
							elif splitCol[0] == '5':
								arr.append("dengan senjata 1 " + translate_weapon(int(splitCol[1])))
								arr.append("dan senjata 2 " + translate_weapon(int(splitCol[2])))
								arr_weap1.append(translate_weapon(int(splitCol[1])))
								arr_weap2.append(translate_weapon(int(splitCol[2])))
						elif len(splitCol) == 4:
							arr.append("terdapat korban")
							if splitCol[1] == '1':
								arr.append("terbunuh,")        
							elif splitCol[2] == '1':
								arr.append("luka-luka,")
							elif splitCol[3] == '1':
								arr.append("penculikan,")
							elif splitCol[4] == '1':
								arr.append("pelecehan seksual,")
						elif len(splitCol) == 9:
							arr.append("terdapat korban")
							if splitCol[1] == '1':
								arr.append("terbunuh,")        
							if splitCol[2] == '1':
								arr.append("luka-luka,")
							if splitCol[3] == '1':
								arr.append("penculikan,")
							if splitCol[4] == '1':
								arr.append("pelecehan seksual,")
							if splitCol[5] == '1':
								arr.append("terbunuh berjenis kelamin perempuan,")        
							if splitCol[6] == '1':
								arr.append("luka-luka berjenis kelamin perempuan,")
							if splitCol[7] == '1':
								arr.append("penculikan berjenis kelamin perempuan,")
							if splitCol[8] == '1':
								arr.append("pelecehan seksual berjenis kelamin perempuan,")
								
				combine_arr = ' '.join(arr)
				df_values_decode.loc[index,'ListValues'] = 'cenderung terjadi ' + combine_arr
				
				if arr_tahun:
					df_values_decode.loc[index,'tahun'] = ' '.join(arr_tahun)
				if arr_bulan:
					df_values_decode.loc[index,'bulan'] = ' '.join(arr_bulan)
				if arr_kab:
					df_values_decode.loc[index,'kabupaten'] = ' '.join(arr_kab)
				if arr_act1: 
					df_values_decode.loc[index,'act1'] = ' '.join(arr_act1)
				if arr_act2:
					df_values_decode.loc[index,'act2'] = ' '.join(arr_act2)
				if arr_weap1: 
					df_values_decode.loc[index,'weap1'] = ' '.join(arr_weap1)
				if arr_weap2:
					df_values_decode.loc[index,'weap2'] = ' '.join(arr_weap2)
				if arr_jkek:
					df_values_decode.loc[index,'jenis_kek'] = ' '.join(arr_jkek)
				if arr_katkek: 
					df_values_decode.loc[index,'kat_kek'] = ' '.join(arr_katkek)
				if arr_benkek:
					df_values_decode.loc[index,'ben_kek'] = ' '.join(arr_benkek)
				if arr_metkek:
					df_values_decode.loc[index,'met_kek'] = ' '.join(arr_metkek)
				if arr_loc:
					df_values_decode.loc[index,'LocValues'] = ' '.join(arr_loc)
				else:
					df_values_decode.loc[index,'LocValues'] = 'Nasional'

			# change confident value to percent
			df_values_conf = (df_values_conf*100).round(2)

			# Merge descriptive rules
			result_join_decode = pd.concat([df_key_decode, df_values_decode, df_values_conf], axis=1, join_axes=[df_key.index])
			result_join_decode['Result']=result_join_decode['confident'].astype(str)+'% Kekerasan terjadi '+result_join_decode['List']+' '+result_join_decode['ListValues']

			# join two column with has same value
			def check_loc(row):
				if row.Loc == row.LocValues:
					return 'Nasional'
				elif (row.Loc == 'Nasional') & (row.LocValues != 'Nasional'):
					return row.LocValues
				elif (row.Loc != 'Nasional') & (row.LocValues == 'Nasional'):
					return row.Loc
				
			def check_tahun(row):
				if (isinstance(row.List_tahun, str)) & (isinstance(row.tahun, float)):
					return row.List_tahun
				elif (isinstance(row.tahun, str)) & (isinstance(row.List_tahun, float)):
					return row.tahun
				else:
					return np.nan
				
			def check_bulan(row):
				if (isinstance(row.List_bulan, str)) & (isinstance(row.bulan, float)):
					return row.List_bulan
				elif (isinstance(row.bulan, str)) & (isinstance(row.List_bulan, float)):
					return row.bulan
				else:
					return np.nan
				
			def check_kab(row):
				if (isinstance(row.List_kabupaten, str)) & (isinstance(row.kabupaten, float)):
					return row.List_kabupaten
				elif (isinstance(row.kabupaten, str)) & (isinstance(row.List_kabupaten, float)):
					return row.kabupaten
				else:
					return np.nan
				
			def check_act1(row):
				if (isinstance(row.List_act1, str)) & (isinstance(row.act1, float)):
					return row.List_act1
				elif (isinstance(row.act1, str)) & (isinstance(row.List_act1, float)):
					return row.act1
				else:
					return np.nan
				
			def check_act2(row):
				if (isinstance(row.List_act2, str)) & (isinstance(row.act2, float)):
					return row.List_act2
				elif (isinstance(row.act2, str)) & (isinstance(row.List_act2, float)):
					return row.act2
				else:
					return np.nan
				
			def check_weap1(row):
				if (isinstance(row.List_weap1, str)) & (isinstance(row.weap1, float)):
					return row.List_weap1
				elif (isinstance(row.weap1, str)) & (isinstance(row.List_weap1, float)):
					return row.weap1
				else:
					return np.nan
				
			def check_weap2(row):
				if (isinstance(row.List_weap2, str)) & (isinstance(row.weap2, float)):
					return row.List_weap2
				elif (isinstance(row.weap2, str)) & (isinstance(row.List_weap2, float)):
					return row.weap2
				else:
					return np.nan

			# apply function for join two column
			result_join_decode['ResultLoc'] = result_join_decode.apply(check_loc, axis=1)
			result_join_decode['ResultTahun'] = result_join_decode.apply(check_tahun, axis=1)
			result_join_decode['ResultBulan'] = result_join_decode.apply(check_bulan, axis=1)
			result_join_decode['ResultKab'] = result_join_decode.apply(check_kab, axis=1)
			result_join_decode['ResultActor1'] = result_join_decode.apply(check_act1, axis=1)
			result_join_decode['ResultActor2'] = result_join_decode.apply(check_act2, axis=1)
			result_join_decode['ResultWeap1'] = result_join_decode.apply(check_weap1, axis=1)
			result_join_decode['ResultWeap2'] = result_join_decode.apply(check_weap2, axis=1)
			# dataframe for table
			result_join_count = result_join_decode[['ResultTahun', 'ResultBulan', 'ResultLoc', 'ResultKab', 'ResultActor1', 'ResultActor2', 'ResultWeap1', 'ResultWeap2']]
			# convert column ResultTahun to int
			result_join_count['ResultTahun'] = pd.to_numeric(result_join_count['ResultTahun'], errors='coerce')

			group_tahun = result_join_count['ResultTahun'].groupby(result_join_count['ResultTahun']).count()
			group_bulan = result_join_count['ResultBulan'].groupby(result_join_count['ResultBulan']).count()
			group_prov = result_join_count['ResultLoc'].groupby(result_join_count['ResultLoc']).count()
			group_kab = result_join_count['ResultKab'].groupby(result_join_count['ResultKab']).count()

			# function to merge all data and rules in dictionary
			dict_tahun = defaultdict(list)
			for k, v in chain(group_tahun.items(), listgroupby['tahun'].items()):
				dict_tahun[k].append(v)
				
			dict_bulan = defaultdict(list)
			for k, v in chain(group_bulan.items(), listgroupby['bulan'].items()):
				dict_bulan[k].append(v)
				
			dict_prov = defaultdict(list)
			for k, v in chain(group_prov.items(), listgroupby['provinsi'].items()):
				dict_prov[k].append(v)

			dict_kab = defaultdict(list)
			for k, v in chain(group_kab.items(), listgroupby['kabupaten'].items()):
				dict_kab[k].append(v)

			# change to dataframe and fill nan values with 0
			tahun_to_df = pd.DataFrame.from_dict(dict_tahun, orient='index').reset_index().fillna(0)
			kab_to_df = pd.DataFrame.from_dict(dict_kab, orient='index').reset_index().fillna(0)
			prov_to_df = pd.DataFrame.from_dict(dict_prov, orient='index').reset_index().fillna(0)

			# change column name
			tahun_to_df.columns = ['nama', 'rules', 'semua']   
			kab_to_df.columns = ['nama', 'rules', 'semua']   
			prov_to_df.columns = ['nama', 'rules', 'semua']
			# chart tahun
			tahun_semua = Bar(x=tahun_to_df.nama,
				y=tahun_to_df.semua,
				name='Semua Data',
				marker=dict(color='#ffcdd2'))

			tahun_rules = Bar(x=tahun_to_df.nama,
				y=tahun_to_df.rules,
				name='Rules Yang Didapat',
				marker=dict(color='#A2D5F2'))

			data = [tahun_semua, tahun_rules]
			layout = Layout(title="Data Tahun",
							yaxis=dict(title='Jumlah Data'))
			fig = Figure(data=data, layout=layout)

			tahunJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
			# chart provinsi
			provinsi_semua = Bar(x=prov_to_df.nama,
				y=prov_to_df.semua,
				name='Semua Data',
				marker=dict(color='#ffcdd2'))

			provinsi_rules = Bar(x=prov_to_df.nama,
				y=prov_to_df.rules,
				name='Rules Yang Didapat',
				marker=dict(color='#A2D5F2'))

			data = [provinsi_semua, provinsi_rules]
			layout = Layout(title="Data Provinsi",
							yaxis=dict(title='Jumlah Data'))
			prv = Figure(data=data, layout=layout)
			
			provJSON = json.dumps(prv, cls=plotly.utils.PlotlyJSONEncoder)

			# dataframe for map
			result_join_decode['ResultLoc'] = result_join_decode.apply(check_loc, axis=1)
			result_join_print = result_join_decode[['Result', 'ResultLoc']]

			html_filter_result = result_join_print.groupby(['ResultLoc'])

			out_filter_result = (result_join_print.groupby(['ResultLoc'])
				.apply(lambda x: x.to_dict('r'))
				.reset_index()
				.rename(columns={0:'Value'})
				.to_json(orient='records'))

			converted_data = json.loads(out_filter_result)
			national_data = {}

			for v in converted_data:
				if v['ResultLoc'] == 'Nasional':
					national_data = v
				else:
					html = json2html.convert(json=v,
											 table_attributes="id=\"info-table\" class=\"table\"")
					v['html'] = html

			print_html = json2html.convert(json=national_data,
										   table_attributes="id=\"info-table\" class=\"table\"")

			# result_join = pd.concat([df_key, df_values_key, df_values_conf], axis=1, join_axes=[df_key.index])

			# def f(row):
			# 	for col in row.index:
			# 		if (row[col] is not None) & (not isinstance(row[col], float)):
			# 			if row[col][0] == '2':
			# 				a = row[col].split("-")
			# 				return a[1]

			# result_join['Result'] = result_join.apply(f, axis=1)

			# result_join['Result'] = result_join['Result'].fillna('Nasional')

			# group_true = result_join.Result.notnull()
			# filter_result = result_join[group_true]

			# html_filter_result = filter_result.groupby(['Result'])

			# out_filter_result = (filter_result.groupby(['Result'])
			# 					 .apply(lambda x: x.to_dict('r'))
			# 					 .reset_index()
			# 					 .rename(columns={0: 'Value'})
			# 					 .to_json(orient='records'))

			# converted_data = json.loads(out_filter_result)
			# national_data = {}

			# for v in converted_data:
			# 	if v['Result'] == 'Nasional':
			# 		national_data = v
			# 	else:
			# 		html = json2html.convert(json=v,
			# 								 table_attributes="id=\"info-table\" class=\"table\"")
			# 		v['html'] = html

			# print_html = json2html.convert(json=national_data,
			# 							   table_attributes="id=\"info-table\" class=\"table\"")
		else:
			converted_data = []
			total_rules = 0
			print_html = "Tidak ada rules"
			out_filter_result = "Tidak ada rules"

	elif request.form.get('action') == 'SingleDimension':
		#data yang diambil hanya data kekerasan terhadap perempuan (EKSTRAKSI DATA)
		snpkframe = snpkframe.loc[(snpkframe["kil_f"] > 0) | (snpkframe["inj_f"] > 0) | (snpkframe["kid_f"] > 0) | (snpkframe["sex_f"] > 0)]

		def clean_dampak(value):
			if value > 0:
				return 1
			else:
				return 0

		#konversi biner data dimensi 4
		snpkframe["kil_total"] = snpkframe["kil_total"].apply(clean_dampak)
		snpkframe["kil_f"] = snpkframe["kil_f"].apply(clean_dampak)
		snpkframe["inj_total"] = snpkframe["inj_total"].apply(clean_dampak)
		snpkframe["inj_f"] = snpkframe["inj_f"].apply(clean_dampak)
		snpkframe["kidnap_tot"] = snpkframe["kidnap_tot"].apply(clean_dampak)
		snpkframe["kid_f"] = snpkframe["kid_f"].apply(clean_dampak)
		snpkframe["sex_as_tot"] = snpkframe["sex_as_tot"].apply(clean_dampak)
		snpkframe["sex_f"] = snpkframe["sex_f"].apply(clean_dampak)

		#initiate new array
		con = []
		con_dimensi = []
		con_dimensi_enc = []

		# kondisi dimensi 1
		if dimensi1_key:
			if dimensi1_key == 'tahun':
				if dimensi1 != 'all':
					con.append('(snpkframe2["tahun"]==' + dimensi1 + ')')
				else:
					con.append('(snpkframe2["tahun"].notnull())')
				con_dimensi.append('"tahun"')
				con_dimensi_enc.append('"1-1-" + snpkframe3["tahun"].astype(str)')
			elif dimensi1_key == 'bulan':
				if dimensi1 != 'all':
					con.append('(snpkframe2["bulan"]==' + dimensi1 + ')')
				else:
					con.append('(snpkframe2["bulan"].notnull())')
				con.append('(snpkframe2["tahun"].notnull())')
				con_dimensi.append('"tahun","bulan"')
				con_dimensi_enc.append('"1-2-" + snpkframe3["bulan"].astype(str)')
			else:
				con_dimensi.append('"tahun","bulan"')
				con_dimensi_enc.append('"1-1-" + snpkframe3["tahun"].astype(str)')
				con_dimensi_enc.append('"1-2-" + snpkframe3["bulan"].astype(str)')

		# kondisi dimensi 2
		if dimensi2_key:
			if dimensi2_key == 'provinsi':
				if dimensi2 != 'all':
					con.append('(snpkframe2["provinsi"]=="' + dimensi2 + '")')
				else:
					con.append('(snpkframe2["provinsi"].notnull())')
				con_dimensi.append('"provinsi"')
				con_dimensi_enc.append('"2-1-" + snpkframe3["provinsi"].astype(str)')
			elif dimensi2_key == 'kabupaten':
				if dimensi2 != 'all':
					con.append('(snpkframe2["kabupaten"]=="' + dimensi2 + '")')
				else:
					con.append('(snpkframe2["kabupaten"].notnull())')
				con.append('(snpkframe2["provinsi"].notnull())')
				con_dimensi.append('"provinsi","kabupaten"')
				con_dimensi_enc.append('"2-2-" + snpkframe3["kabupaten"].astype(str)')
			else:
				con_dimensi.append('"provinsi","kabupaten"')
				con_dimensi_enc.append('"2-1-" + snpkframe3["provinsi"].astype(str)')
				con_dimensi_enc.append('"2-2-" + snpkframe3["kabupaten"].astype(str)')

		# kondisi dimensi 3
		if dimensi3_key:
			if dimensi3_key == 'actor1':
				if dimensi3 != 'all':
					con.append('(snpkframe2["actor_s1_tp"]==' + dimensi3 + ')')
				else:
					con.append('(snpkframe2["actor_s1_tp"].notnull())')
				con_dimensi.append('"actor_s1_tp"')
				con_dimensi_enc.append('"3-1-" + snpkframe3["actor_s1_tp"].astype(str)')
			elif dimensi3_key == 'actor2':
				if dimensi3 != 'all':
					con.append('(snpkframe2["actor_s2_tp"]==' + dimensi3 + ')')
				else:
					con.append('(snpkframe2["actor_s1_tp"].notnull())')
				con.append('(snpkframe2["actor_s1_tp"].notnull())')
				con_dimensi.append('"actor_s1_tp","actor_s2_tp"')
				con_dimensi_enc.append('"3-2-" + snpkframe3["actor_s2_tp"].astype(str)')
			else:
				con_dimensi.append('"actor_s1_tp","actor_s2_tp"')
				con_dimensi_enc.append('"3-1-" + snpkframe3["actor_s1_tp"].astype(str)')
				con_dimensi_enc.append('"3-2-" + snpkframe3["actor_s2_tp"].astype(str)')

		# kondisi dimensi 4
		if dimensi4_key:
			if dimensi4_key == 'dampak-all':
				if dimensi4 != 'all':
					con.append('(snpkframe2["' + dimensi4 + '"] > 0)')
					con_dimensi_enc.append('"4-1-" + snpkframe3["' + dimensi4 + '"].astype(str)')
					con_dimensi.append('"' + dimensi4 + '"')
				else:
					con.append('(snpkframe2["kil_total"].notnull())')
					con.append('(snpkframe2["inj_total"].notnull())')
					con.append('(snpkframe2["kidnap_tot"].notnull())')
					con.append('(snpkframe2["sex_as_tot"].notnull())')
					con_dimensi.append('"kil_total"')
					con_dimensi.append('"inj_total"')
					con_dimensi.append('"kidnap_tot"')
					con_dimensi.append('"sex_as_tot"')
					con_dimensi_enc.append('"4-1-" + snpkframe3["kil_total"].astype(str)')
					con_dimensi_enc.append('"4-1-" + snpkframe3["inj_total"].astype(str)')
					con_dimensi_enc.append('"4-1-" + snpkframe3["kidnap_tot"].astype(str)')
					con_dimensi_enc.append('"4-1-" + snpkframe3["sex_as_tot"].astype(str)')

			elif dimensi4_key == 'dampak-f':
				if dimensi4 != 'all':
					con.append('(snpkframe2["' + dimensi4 + '"] > 0)')
					con_dimensi.append('"' + dimensi4 + '"')
					con_dimensi_enc.append('"4-2-" + snpkframe3["' + dimensi4 + '"].astype(str)')
				else:
					con.append('(snpkframe2["kil_f"].notnull())')
					con.append('(snpkframe2["inj_f"].notnull())')
					con.append('(snpkframe2["kid_f"].notnull())')
					con.append('(snpkframe2["sex_f"].notnull())')
					con_dimensi.append('"kil_f"')
					con_dimensi.append('"inj_f"')
					con_dimensi.append('"kid_f"')
					con_dimensi.append('"sex_f"')
					con_dimensi_enc.append('"4-2-" + snpkframe3["kil_f"].astype(str)')
					con_dimensi_enc.append('"4-2-" + snpkframe3["inj_f"].astype(str)')
					con_dimensi_enc.append('"4-2-" + snpkframe3["kid_f"].astype(str)')
					con_dimensi_enc.append('"4-2-" + snpkframe3["sex_f"].astype(str)')
			else:
				con_dimensi.append('"kil_total","kil_f","inj_total","inj_f","kidnap_tot","kid_f","sex_as_tot","sex_f"')
				con_dimensi_enc.append('"4-1-" + snpkframe3["kil_total"].astype(str)')
				con_dimensi_enc.append('"4-1-" + snpkframe3["inj_total"].astype(str)')
				con_dimensi_enc.append('"4-1-" + snpkframe3["kidnap_tot"].astype(str)')
				con_dimensi_enc.append('"4-1-" + snpkframe3["sex_as_tot"].astype(str)')
				con_dimensi_enc.append('"4-2-" + snpkframe3["kil_f"].astype(str)')
				con_dimensi_enc.append('"4-2-" + snpkframe3["inj_f"].astype(str)')
				con_dimensi_enc.append('"4-2-" + snpkframe3["kid_f"].astype(str)')
				con_dimensi_enc.append('"4-2-" + snpkframe3["sex_f"].astype(str)')

		# kondisi dimensi 5
		if dimensi5_key:
			if dimensi5_key == 'weapon_1':
				if dimensi5 != 'all':
					con.append('(snpkframe2["weapon_1"]==' + dimensi5 + ')')
				else:
					con.append('(snpkframe2["weapon_1"].notnull())')
				con_dimensi.append('"weapon_1"')
				con_dimensi_enc.append('"5-1-" + snpkframe3["weapon_1"].astype(str)')
			elif dimensi5_key == 'weapon_2':
				if dimensi5 != 'all':
					con.append('(snpkframe2["weapon_2"]==' + dimensi5 + ')')
				else:
					con.append('(snpkframe2["weapon_2"].notnull())')
				con_dimensi.append('"weapon_1","weapon_2"')
				con_dimensi_enc.append('"5-2-" + snpkframe3["weapon_2"].astype(str)')
			else:
				con_dimensi.append('"weapon_1","weapon_2"')
				con_dimensi_enc.append('"5-1-" + snpkframe3["weapon_1"].astype(str)')
				con_dimensi_enc.append('"5-2-" + snpkframe3["weapon_2"].astype(str)')

		# kondisi dimensi 6
		if dimensi6_key:
			if dimensi6_key == 'jenis_kek':
				if dimensi6 != 'all':
					con.append('(snpkframe2["jenis_kek"]==' + dimensi6 + ')')
				else:
					con.append('(snpkframe2["jenis_kek"].notnull())')
			con_dimensi.append('"jenis_kek"')
			con_dimensi_enc.append('"6-" + snpkframe3["jenis_kek"].astype(str)')
		# kondisi dimensi 7
		if dimensi7_key:
			if dimensi7_key == 'tp_kek_new':
				if dimensi7 != 'all':
					con.append('(snpkframe2["tp_kek1_new"]==' + dimensi7 + ')')
				else:
					con.append('(snpkframe2["tp_kek1_new"].notnull())')
			con_dimensi.append('"tp_kek1_new"')
			con_dimensi_enc.append('"7-" + snpkframe3["tp_kek1_new"].astype(str)')

		# kondisi dimensi 8
		if dimensi8_key:
			if dimensi8_key == 'ben_kek':
				if dimensi8 != 'all':
					con.append('(snpkframe2["ben_kek1"]==' + dimensi8 + ')')
				else:
					con.append('(snpkframe2["ben_kek1"].notnull())')
			con_dimensi.append('"ben_kek1"')
			con_dimensi_enc.append('"8-" + snpkframe3["ben_kek1"].astype(str)')

		# kondisi dimensi 9
		if dimensi9_key:
			if dimensi9_key == 'meta_kek':
				if dimensi9 != 'all':
					con.append('(snpkframe2["meta_tp_kek1_new"]==' + dimensi9 + ')')
				else:
					con.append('(snpkframe2["meta_tp_kek1_new"].notnull())')
			con_dimensi.append('"meta_tp_kek1_new"')
			con_dimensi_enc.append('"9-" + snpkframe3["meta_tp_kek1_new"].astype(str)')


		# join array dan konversi ke string
		sep = " & "
		sep_dim = ","
		rules_filter = sep.join(con)
		rules_dimensi = sep_dim.join(con_dimensi)

		# print_con = {
		# 	'con': con,
		# 	'con_dim': con_dimensi
		# }

		# seleksi kolom sebelum difilter
		snpkframe2 = eval('snpkframe[[' + rules_dimensi + ']]')
		row_total = len(snpkframe2.index)
		# min_sup = int((float(minsup1) / 100) * row_total)
		if minsup1:
			min_sup = int(minsup1)
		# min_sup = int((float(minsup1) / 100) * row_total)
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

		# seleksi data dengan kriteria yang ditentukan
		if rules_filter == '':
			snpkframe3 = snpkframe2.copy()
		else:
			snpkframe3 = eval('snpkframe2[' + rules_filter + ']')

		for index, x in enumerate(con_dimensi_enc):
			snpkframe3["dim" + str(index + 1)] = eval(x)

		snpkframe31 = snpkframe3.loc[:, snpkframe3.columns.to_series().str.contains('dim').tolist()]

		# json_before_fpgrowth = snpkframe31.to_json(orient='split')

		# convert into matrix
		convMatrix = snpkframe31.as_matrix()

		# mencari pattern pada data kek_uji
		patterns = pyfpgrowth.find_frequent_patterns(convMatrix, min_sup)

		# mencari rules dari pattern yang telah dibuat
		rules = pyfpgrowth.generate_association_rules(patterns, min_conf)

		if rules:
			total_rules = len(rules)
			dim1_list = list(rules.keys())
			df_key = pd.DataFrame(dim1_list)
			total_columns = len(df_key.columns)
			new_cols = ['key' + str(i) for i in df_key.columns]
			df_key.columns = new_cols[:total_columns]

			dim2_list = list(rules.values())
			df_values = pd.DataFrame(dim2_list)
			df_values.rename(columns={0: 'first'}, inplace=True)
			df_values.rename(columns={1: 'confident'}, inplace=True)

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
						if (row[col][0] == '2') & (row[col][2] == '1') :
							a = row[col].split("-")
							return a[2]

			result_join['ResultLoc'] = result_join.apply(f, axis=1)

			result_join['ResultLoc'] = result_join['ResultLoc'].fillna('Nasional')

			group_true = result_join.ResultLoc.notnull()
			filter_result = result_join[group_true]

			html_filter_result = filter_result.groupby(['ResultLoc'])

			out_filter_result = (filter_result.groupby(['ResultLoc'])
								 .apply(lambda x: x.to_dict('r'))
								 .reset_index()
								 .rename(columns={0: 'Value'})
								 .to_json(orient='records'))

			converted_data = json.loads(out_filter_result)
			national_data = {}

			for v in converted_data:
				if v['ResultLoc'] == 'Nasional':
					national_data = v
				else:
					html = json2html.convert(json=v,
											 table_attributes="id=\"info-table\" class=\"table\"")
					v['html'] = html

			print_html = json2html.convert(json=national_data,
										   table_attributes="id=\"info-table\" class=\"table\"")
		else:
			converted_data = []
			total_rules = 0
			print_html = "Tidak ada rules"
			out_filter_result = "Tidak ada rules"


	timer = (time.time() - start_time)
	# data_html = result_join.to_html(classes="table table-data")
	# data_html = data_html.replace('NaN', '')
	return render_template('show_selection.html', data=print_html, converted_data=converted_data, raw_data = out_filter_result, time_exe = timer, total_rules = total_rules, kabupaten_data=kab_to_df.as_matrix(), provinsi_data=provJSON, tahun_data=tahunJSON)

@app.route('/selection')
def load_selection():
	return render_template('selection.html')


if __name__ == '__main__':
	host = environ.get('APP_HOST', '0.0.0.0')
	port = int(environ.get('APP_PORT', 5000))
	debug = bool(int(environ.get('APP_DEBUG', 1)))

	app.secret_key = 'super secret key'

	app.run(host=host,
			port=port,
			debug=debug)
