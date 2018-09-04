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
	translate_bentuk_kekerasan, translate_dampak

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

	kek_f = ['Terbunuh', 'Luka-Luka', 'Penculikan', 'Pelecehan Seksual']
	kek_f_key = ['kil_f', 'inj_f', 'kid_f', 'sex_f']

	data = {
		'tahun': [x for x in snpkframe.tahun.unique()],
		'bulan_val': [x for x in snpkframe.bulan.unique()],
		'provinsi': [x for x in snpkframe.provinsi.unique()],
		'kabupaten': [x for x in snpkframe.kabupaten.unique()],
		'kek_f': [x for x in kek_f],
		'kek_f_key': [x for x in kek_f_key],
		'actor_s1_val': [x for x in snpkframe.actor_s1_tp.unique()],
		'actor_s2_val': [x for x in snpkframe.actor_s2_tp.unique()],
		'weapon_1_val': [x for x in snpkframe.weapon_1.unique()],
		'weapon_2_val': [x for x in snpkframe.weapon_2.unique()],
		'jenis_kek_val': [x for x in snpkframe.jenis_kek.unique()],
		'tp_kek1_val': [x for x in snpkframe.tp_kek1_new.unique()],
		'ben_kek1_val': [x for x in snpkframe.ben_kek1.unique()],
		'bulan': [translate_bulan(x) for x in snpkframe.bulan.unique()],
		'actor_s1_tp': [translate_actor(x) for x in snpkframe.actor_s1_tp.unique()],
		'actor_s2_tp': [translate_actor(x) for x in snpkframe.actor_s2_tp.unique()],
		'weapon_1': [translate_weapon(x) for x in snpkframe.weapon_1.unique()],
		'weapon_2': [translate_weapon(x) for x in snpkframe.weapon_2.unique()],
		'jenis_kek': [translate_jenis_kek(x) for x in snpkframe.jenis_kek.unique()],
		'tp_kek1_new': [translate_tipe_kekerasan(x) for x in snpkframe.tp_kek1_new.unique()],
		'ben_kek1': [translate_bentuk_kekerasan(x) for x in snpkframe.ben_kek1.unique()],
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
			 'build_dmg_total', 'oth_impact', 'weapon_oth', 'isu_indv',  'tp_kek1_o', 'ben_kek1_o', 'ben_kek2',
			 'ben_kek2_o', 'insd_desc', 'full_coverage', 's1', 's2', 's3', 's4', 's5', 's6', 's7', 's8', 'weapon',
			 'wpnfarm', 'wpnfarmman', 'wpnfarmhmde', 'wpnexpl', 'wpnshrp', 'wpnblunt', 'wpnfire', 'intervention',
			 'intvnrsecforfrml', 'intvnrtni', 'intvnrpol', 'intvnrbrimob', 'intvnrcvln', 'intvntnressucces',
			 'intvntnviolup', 'actcountrelormas', 'actcountparpol', 'actcountseprtst', 'actcountgov', 'actcountstudents',
			 'secvssec', 'onewayformconf', 'twowayformconf', 'death1', 'death3', 'death5', 'death10', 'largeinc',
			 'evperiod', 'pevperiod', 'preevperiod', 'ev2period', 'pev2period', 'create', 'last_update', 'meta_tp_kek1_new', 
			 'build_dmg_total', 'kil_total', 'inj_total', 'kidnap_tot', 'sex_as_tot'], axis=1)

		#data yang diambil hanya data kekerasan terhadap perempuan (EKSTRAKSI DATA)
		snpkframe = snpkframe.loc[(snpkframe["kil_f"] > 0) | (snpkframe["inj_f"] > 0) | (snpkframe["kid_f"] > 0) | (snpkframe["sex_f"] > 0)]

		def clean_dampak(value):
			if value > 0:
				return 1
			else:
				return 0

		#konversi biner data dimensi 4
		snpkframe["kil_f"] = snpkframe["kil_f"].apply(clean_dampak)
		snpkframe["inj_f"] = snpkframe["inj_f"].apply(clean_dampak)
		snpkframe["kid_f"] = snpkframe["kid_f"].apply(clean_dampak)
		snpkframe["sex_f"] = snpkframe["sex_f"].apply(clean_dampak)

		#konversi ke kode dimensi
		snpkframe.loc[snpkframe['kil_f'] > 0, 'kil_f'] = "kil_f"
		snpkframe.loc[snpkframe['inj_f'] > 0, 'inj_f'] = "inj_f"
		snpkframe.loc[snpkframe['kid_f'] > 0, 'kid_f'] = "kid_f"
		snpkframe.loc[snpkframe['sex_f'] > 0, 'sex_f'] = "sex_f"
		snpkframe.loc[snpkframe['bdg_des'] > 0, 'bdg_des'] = "bdg_des"

		#mengganti kode 'tidak ada'
		snpkframe["actor_s1_tp"] = snpkframe["actor_s1_tp"].replace(2, 1)
		snpkframe["actor_s2_tp"] = snpkframe["actor_s2_tp"].replace(2, 1)
		snpkframe["weapon_1"] = snpkframe["weapon_1"].replace(3, 1)
		snpkframe["weapon_2"] = snpkframe["weapon_2"].replace(3, 1)
		snpkframe["jenis_kek"] = snpkframe["jenis_kek"].replace(2, 1)
		snpkframe["ben_kek1"] = snpkframe["ben_kek1"].replace(0, 1)
		snpkframe["ben_kek1"] = snpkframe["ben_kek1"].replace(2, 1)

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
			if dimensi4_key == 'dampak-f':
				if dimensi4 != 'all':
					con.append('(snpkframe2["' + dimensi4 + '"] > 0)')
					con_dimensi.append('"'+ dimensi4 + '"')
					con_dimensi_enc.append('"4-" + snpkframe3["' + dimensi4 + '"].astype(str)')
			else:
				con_dimensi.append('"kil_f","inj_f","kid_f","sex_f","bdg_des"')
				con_dimensi_enc.append('"4-" + snpkframe3["kil_f"].astype(str)+ "-" + snpkframe3["inj_f"].astype(str) + "-" + snpkframe3["kid_f"].astype(str) + "-" + snpkframe3["sex_f"].astype(str) + "-" + snpkframe3["bdg_des"].astype(str)')

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

		if minsup1:
			min_sup = int(minsup1)
		else:
			min_sup = 10

		if minconf1:
			min_conf = float(minconf1) / 100
		else:
			min_conf = 0

		# seleksi data dengan kriteria yang ditentukan
		if rules_filter == '':
			snpkframe3 = snpkframe2.copy()
		else:
			snpkframe3 = eval('snpkframe2[' + rules_filter + ']')

		#group by berdasarkan dimensi yang dipilih
		listgroupby = {}
		for index, x in enumerate(con_dimensi):
			con_split = x.split(',')
			# print con_split
			for dim in con_split:
				dim = dim.replace('"', '')
				listgroupby[dim] = eval('snpkframe3["'+dim+'"].groupby(snpkframe3["'+dim+'"]).count()')
				if dim=='bulan':
					for key, value in listgroupby["bulan"].iteritems():
						listgroupby["bulan"][translate_bulan(key)] = listgroupby["bulan"].pop(key)
				elif (dim=='actor_s1_tp'):
					for key, value in listgroupby["actor_s1_tp"].iteritems():
						listgroupby["actor_s1_tp"][translate_actor(key)] = listgroupby["actor_s1_tp"].pop(key)
				elif (dim=='actor_s2_tp'):
					for key, value in listgroupby["actor_s2_tp"].iteritems():
						listgroupby["actor_s2_tp"][translate_actor(key)] = listgroupby["actor_s2_tp"].pop(key)
				elif (dim=='weapon_1'):
					for key, value in listgroupby["weapon_1"].iteritems():
						listgroupby["weapon_1"][translate_weapon(key)] = listgroupby["weapon_1"].pop(key)
				elif (dim=='weapon_2'):
					for key, value in listgroupby["weapon_2"].iteritems():
						listgroupby["weapon_2"][translate_weapon(key)] = listgroupby["weapon_2"].pop(key)
				elif (dim=='jenis_kek'):
					for key, value in listgroupby["jenis_kek"].iteritems():
						listgroupby["jenis_kek"][translate_jenis_kek(key)] = listgroupby["jenis_kek"].pop(key)
				elif (dim=='tp_kek1_new'):
					for key, value in listgroupby["tp_kek1_new"].iteritems():
						listgroupby["tp_kek1_new"][translate_tipe_kekerasan(key)] = listgroupby["tp_kek1_new"].pop(key)
				elif (dim=='ben_kek1'):
					for key, value in listgroupby["ben_kek1"].iteritems():
						listgroupby["ben_kek1"][translate_bentuk_kekerasan(key)] = listgroupby["ben_kek1"].pop(key)

		#merubah nama column dengan prefix dim
		for index, x in enumerate(con_dimensi_enc):
			snpkframe3["dim" + str(index + 1)] = eval(x)

		#mengambil nama column dengan prefix dim ke dalam dataframe snpkframe31
		snpkframe31 = snpkframe3.loc[:, snpkframe3.columns.to_series().str.contains('dim').tolist()]
		trans_total = len(snpkframe31.index)

		# json_before_fpgrowth = snpkframe31.to_json(orient='split')

		# diubah ke dalam matrix array
		convMatrix = snpkframe31.as_matrix()

		# mencari pattern dengan menggunakan pypfpgrowth
		patterns = pyfpgrowth.find_frequent_patterns(convMatrix, min_sup)

		# mencari rules dari pattern yang telah dibuat
		rules = pyfpgrowth.generate_association_rules(patterns, min_conf, trans_total)
		
		timer = (time.time() - start_time)
		#jika terdapat rules yang di generate
		if rules:
			total_rules = len(rules)
			dim1_list = list(rules.keys())
			df_key = pd.DataFrame(dim1_list)
			total_columns = len(df_key.columns)
			#merubah nama column dengan prefix key
			new_cols = ['key' + str(i) for i in df_key.columns]
			df_key.columns = new_cols[:total_columns]

			# menyalin dataframe key ke dalam dataframe df_key_decode untuk proses decoding
			df_key_decode = df_key.copy()
			df_key_decode

			#iterasi di dalam dataframe df_key_decode
			for index, row in df_key_decode.iterrows():
				arr = []
				arr_tahun = []
				arr_bulan = []
				arr_loc = []
				arr_kab = []
				arr_act1 = []
				arr_act2 = []
				arr_vict = []
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
								arr.append("terdapat korban " + translate_dampak(splitCol[1]))
								arr_vict.append(translate_dampak(splitCol[1]))
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
							elif splitCol[0] == '5':
								arr.append("dengan senjata 1 " + translate_weapon(int(splitCol[1])))
								arr.append("dan senjata 2 " + translate_weapon(int(splitCol[2])))
								arr_weap1.append(translate_weapon(int(splitCol[1])))
								arr_weap2.append(translate_weapon(int(splitCol[2])))
						elif len(splitCol) == 6:
							arr.append("terdapat korban")
							if splitCol[1] != '0':
								arr.append("terbunuh ")  
								arr_vict.append(translate_dampak(splitCol[1]))
							elif splitCol[2] != '0':
								arr.append("luka-luka ")
								arr_vict.append(translate_dampak(splitCol[2]))
							elif splitCol[3] != '0':
								arr.append("penculikan ")
								arr_vict.append(translate_dampak(splitCol[3]))
							elif splitCol[4] != '0':
								arr.append("pelecehan seksual ")
								arr_vict.append(translate_dampak(splitCol[4]))
							elif splitCol[5] != '0':
								arr.append("bangunan rusak ")
								arr_vict.append(translate_dampak(splitCol[5]))
								
				combine_arr = ' '.join(arr)
			#     print combine_arr
				df_key_decode.loc[index,'List'] = combine_arr
					
				if arr_tahun:
					df_key_decode.loc[index,'List_tahun'] = ' '.join(arr_tahun)
				else:
					df_key_decode.loc[index,'List_tahun'] = 0
				if arr_bulan:
					df_key_decode.loc[index,'List_bulan'] = ' '.join(arr_bulan)
				else:
					df_key_decode.loc[index,'List_bulan'] = np.nan
				if arr_kab:
					df_key_decode.loc[index,'List_kabupaten'] = ' '.join(arr_kab)
				else:
					df_key_decode.loc[index,'List_kabupaten'] = np.nan
				if arr_act1: 
					df_key_decode.loc[index,'List_act1'] = ' '.join(arr_act1)
				else:
					df_key_decode.loc[index,'List_act1'] = np.nan
				if arr_act2:
					df_key_decode.loc[index,'List_act2'] = ' '.join(arr_act2)
				else:
					df_key_decode.loc[index,'List_act2'] = np.nan
				if arr_vict:
					df_key_decode.loc[index,'List_dampak'] = ' '.join(arr_vict)
				else:
					df_key_decode.loc[index,'List_dampak'] = np.nan
				if arr_weap1: 
					df_key_decode.loc[index,'List_weap1'] = ' '.join(arr_weap1)
				else:
					df_key_decode.loc[index,'List_weap1'] = np.nan
				if arr_weap2:
					df_key_decode.loc[index,'List_weap2'] = ' '.join(arr_weap2)
				else:
					df_key_decode.loc[index,'List_weap2'] = np.nan
				if arr_jkek:
					df_key_decode.loc[index,'List_jenis_kek'] = ' '.join(arr_jkek)
				else:
					df_key_decode.loc[index,'List_jenis_kek'] = np.nan
				if arr_katkek: 
					df_key_decode.loc[index,'List_kat_kek'] = ' '.join(arr_katkek)
				else:
					df_key_decode.loc[index,'List_kat_kek'] = np.nan
				if arr_benkek:
					df_key_decode.loc[index,'List_ben_kek'] = ' '.join(arr_benkek)
				else:
					df_key_decode.loc[index,'List_ben_kek'] = np.nan
				if arr_metkek:
					df_key_decode.loc[index,'List_met_kek'] = ' '.join(arr_metkek)
				else:
					df_key_decode.loc[index,'List_met_kek'] = np.nan
				if arr_loc:
					df_key_decode.loc[index,'Loc'] = ' '.join(arr_loc)
				else:
					df_key_decode.loc[index,'Loc'] = 'Nasional'
		
			# dataframe untuk rules value
			dim2_list = list(rules.values())
			df_values = pd.DataFrame(dim2_list)
			df_values.rename(columns={0: 'first'}, inplace=True)
			df_values.rename(columns={1: 'confident'}, inplace=True)
			df_values.rename(columns={2:'liftratio'}, inplace=True)

			# menghapus karakter yang tidak diperlukan
			df_values['first'] = df_values['first'].astype(str).str.strip('()')
			df_values_key = df_values['first'].str.split(',', expand=True)
			df_values_key = df_values_key.replace('', "None")

			df_values_conf = df_values['confident']
			df_values_lift = df_values['liftratio']
			lift_max = (df_values_lift.max()).round(4)
			lift_min = (df_values_lift.min()).round(4)
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
				arr_vict = []
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
								arr.append("terdapat korban " + translate_dampak(splitCol[1]))
								arr_vict.append(translate_dampak(splitCol[1]))
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
							elif splitCol[0] == '5':
								arr.append("dengan senjata 1 " + translate_weapon(int(splitCol[1])))
								arr.append("dan senjata 2 " + translate_weapon(int(splitCol[2])))
								arr_weap1.append(translate_weapon(int(splitCol[1])))
								arr_weap2.append(translate_weapon(int(splitCol[2])))
						elif len(splitCol) == 6:
							arr.append("terdapat korban")
							if splitCol[1] != '0':
								arr.append("terbunuh ")  
								arr_vict.append(translate_dampak(splitCol[1]))
							elif splitCol[2] != '0':
								arr.append("luka-luka ")
								arr_vict.append(translate_dampak(splitCol[2]))
							elif splitCol[3] != '0':
								arr.append("penculikan ")
								arr_vict.append(translate_dampak(splitCol[3]))
							elif splitCol[4] != '0':
								arr.append("pelecehan seksual ")
								arr_vict.append(translate_dampak(splitCol[4]))
							elif splitCol[5] != '0':
								arr.append("bangunan rusak ")
								arr_vict.append(translate_dampak(splitCol[5]))
								
				combine_arr = ' '.join(arr)
			#     print combine_arr
				df_values_decode.loc[index,'ListValues'] = 'cenderung terjadi ' + combine_arr
			#     print arr_tahun
				if arr_tahun:
					df_values_decode.loc[index,'tahun'] = ' '.join(arr_tahun)
				else:
					df_values_decode.loc[index,'tahun'] = 0
				if arr_bulan:
					df_values_decode.loc[index,'bulan'] = ' '.join(arr_bulan)
				else:
					df_values_decode.loc[index,'bulan'] = np.nan
				if arr_kab:
					df_values_decode.loc[index,'kabupaten'] = ' '.join(arr_kab)
				else:
					df_values_decode.loc[index,'kabupaten'] = np.nan
				if arr_act1: 
					df_values_decode.loc[index,'act1'] = ' '.join(arr_act1)
				else:
					df_values_decode.loc[index,'act1'] = np.nan
				if arr_act2:
					df_values_decode.loc[index,'act2'] = ' '.join(arr_act2)
				else:
					df_values_decode.loc[index,'act2'] = np.nan
				if arr_vict:
					df_values_decode.loc[index,'dampak'] = ' '.join(arr_vict)
				else:
					df_values_decode.loc[index,'dampak'] = np.nan
				if arr_weap1: 
					df_values_decode.loc[index,'weap1'] = ' '.join(arr_weap1)
				else:
					df_values_decode.loc[index,'weap1'] = np.nan
				if arr_weap2:
					df_values_decode.loc[index,'weap2'] = ' '.join(arr_weap2)
				else:
					df_values_decode.loc[index,'weap2'] = np.nan
				if arr_jkek:
					df_values_decode.loc[index,'jenis_kek'] = ' '.join(arr_jkek)
				else:
					df_values_decode.loc[index,'jenis_kek'] = np.nan
				if arr_katkek: 
					df_values_decode.loc[index,'kat_kek'] = ' '.join(arr_katkek)
				else:
					df_values_decode.loc[index,'kat_kek'] = np.nan
				if arr_benkek:
					df_values_decode.loc[index,'ben_kek'] = ' '.join(arr_benkek)
				else:
					df_values_decode.loc[index,'ben_kek'] = np.nan
				if arr_metkek:
					df_values_decode.loc[index,'met_kek'] = ' '.join(arr_metkek)
				else:
					df_values_decode.loc[index,'met_kek'] = np.nan
				if arr_loc:
					df_values_decode.loc[index,'LocValues'] = ' '.join(arr_loc)
				else:
					df_values_decode.loc[index,'LocValues'] = 'Nasional'

			# change confident value to percent
			df_values_conf = (df_values_conf*100).round(2)

			# Merge descriptive rules
			result_join_decode = pd.concat([df_key_decode, df_values_decode, df_values_conf, df_values_lift], axis=1, join_axes=[df_key.index])
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
				if (isinstance(row.List_tahun, str)) & (isinstance(row.tahun, int)):
					if (int(row.List_tahun) > (row.tahun)):
						return row.List_tahun
					else:
						return row.tahun
				elif (isinstance(row.List_tahun, str)) & (isinstance(row.tahun, float)):
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

			def check_dampak(row):
				if (isinstance(row.List_dampak, str)) & (isinstance(row.dampak, float)):
					return row.List_dampak
				elif (isinstance(row.dampak, str)) & (isinstance(row.List_dampak, float)):
					return row.dampak
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
				
			def check_jenis(row):
				if (isinstance(row.List_jenis_kek, str)) & (isinstance(row.jenis_kek, float)):
					return row.List_jenis_kek
				elif (isinstance(row.jenis_kek, str)) & (isinstance(row.List_jenis_kek, float)):
					return row.jenis_kek
				else:
					return np.nan
				
			def check_kat(row):
				if (isinstance(row.List_kat_kek, str)) & (isinstance(row.kat_kek, float)):
					return row.List_kat_kek
				elif (isinstance(row.kat_kek, str)) & (isinstance(row.List_kat_kek, float)):
					return row.kat_kek
				else:
					return np.nan
				
			def check_bentuk(row):
				if (isinstance(row.List_ben_kek, str)) & (isinstance(row.ben_kek, float)):
					return row.List_ben_kek
				elif (isinstance(row.ben_kek, str)) & (isinstance(row.List_ben_kek, float)):
					return row.ben_kek
				else:
					return np.nan

			# apply function for join two column
			if 'Loc' in result_join_decode.columns:
				result_join_decode['ResultLoc'] = result_join_decode.apply(check_loc, axis=1)
			if 'List_tahun' in result_join_decode.columns:
				result_join_decode['ResultTahun'] = result_join_decode.apply(check_tahun, axis=1)
			if 'List_bulan' in result_join_decode.columns:
				result_join_decode['ResultBulan'] = result_join_decode.apply(check_bulan, axis=1)
			if 'List_kabupaten' in result_join_decode.columns:
				result_join_decode['ResultKab'] = result_join_decode.apply(check_kab, axis=1)
			if 'List_act1' in result_join_decode.columns:
				result_join_decode['ResultActor1'] = result_join_decode.apply(check_act1, axis=1)
			if 'List_act2' in result_join_decode.columns:
				result_join_decode['ResultActor2'] = result_join_decode.apply(check_act2, axis=1)
			if 'List_dampak' in result_join_decode.columns:
				result_join_decode['ResultDampak'] = result_join_decode.apply(check_dampak, axis=1)
			if 'List_weap1' in result_join_decode.columns:
				result_join_decode['ResultWeap1'] = result_join_decode.apply(check_weap1, axis=1)
			if 'List_weap2' in result_join_decode.columns:
				result_join_decode['ResultWeap2'] = result_join_decode.apply(check_weap2, axis=1)
			if 'List_jenis_kek' in result_join_decode.columns:
				result_join_decode['ResultJenisKek'] = result_join_decode.apply(check_jenis, axis=1)
			if 'List_kat_kek' in result_join_decode.columns:
				result_join_decode['ResultKatKek'] = result_join_decode.apply(check_kat, axis=1)
			if 'List_ben_kek' in result_join_decode.columns:
				result_join_decode['ResultBenKek'] = result_join_decode.apply(check_bentuk, axis=1)
	
			# dataframe for table
			result_join_count = result_join_decode.loc[:, result_join_decode.columns.to_series().str.contains('Result').tolist()]
			result_join_count = result_join_count.loc[:, result_join_decode.notnull().any()]

			if 'ResultTahun' in result_join_count.columns:
				result_join_count['ResultTahun'] = pd.to_numeric(result_join_count['ResultTahun'], errors='coerce')
				result_join_count['ResultTahun'].fillna(0)
				group_tahun = result_join_count['ResultTahun'].groupby(result_join_count['ResultTahun']).count()
				group_result = result_join_count['Result'].groupby(result_join_count['ResultTahun'])
				dict_rules = defaultdict(list)
				for key, item in group_result:
					dict_rules[key].append(item)
				dict_tahun = defaultdict(list)
				for k, v in chain(listgroupby['tahun'].items(), group_tahun.items(), dict_rules.items()):
					if group_tahun.empty:
						v = 0
					dict_tahun[k].append(v)
				tahun_to_df = pd.DataFrame.from_dict(dict_tahun, orient='index').reset_index().fillna(0)
				tahun_to_df.columns = ['Tahun', 'semua', 'jml_rules', 'Rules']
				# chart tahun
				tahun_semua = Bar(x=tahun_to_df.Tahun,
					y=tahun_to_df.semua,
					name='Semua Data',
					marker=dict(color='rgb(55, 83, 109)'))
				tahun_rules = Bar(x=tahun_to_df.Tahun,
					y=tahun_to_df.jml_rules,
					name='Rules Yang Didapat',
					marker=dict(color='rgb(255, 145, 15)'))
				data = [tahun_semua, tahun_rules]
				layout = Layout(title="Data Tahun",
								yaxis=dict(title='Jumlah Data'),
								legend=dict(x=0,y=1.0),
								autosize=True,
								width=860)
				fig = Figure(data=data, layout=layout)
				tahunJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
				tahun_export_rules = tahun_to_df.loc[tahun_to_df['jml_rules'] > 0]
				tahun_export_rules = tahun_export_rules[['Tahun', 'Rules']]
				# data_rules_tahun = tahun_export_rules.to_json(orient='records')
				data_rules_tahun = json2html.convert(json=tahun_export_rules.to_json(orient='records'), table_attributes="id=\"info-table\" class=\"table\"")
			else:
				tahunJSON = {}
				data_rules_tahun = []
					
			if 'ResultBulan' in result_join_count.columns:
				group_bulan = result_join_count['ResultBulan'].groupby(result_join_count['ResultBulan']).count()
				group_bulan_result = result_join_count['Result'].groupby(result_join_count['ResultBulan'])
				dict_bulan_rules = defaultdict(list)
				for key, item in group_bulan_result:
					dict_bulan_rules[key].append(item)
				dict_bulan = defaultdict(list)
				for k, v in chain(listgroupby['bulan'].items(), group_bulan.items(), dict_bulan_rules.items()):
					if group_bulan.empty:
						v = 0
					dict_bulan[k].append(v)
				bulan_to_df = pd.DataFrame.from_dict(dict_bulan, orient='index').reset_index().fillna(0) 
				bulan_to_df.columns = ['Bulan', 'semua', 'jml_rules', 'Rules']
				# chart bulan
				bulan_semua = Bar(x=bulan_to_df.Bulan,
					y=bulan_to_df.semua,
					name='Semua Data',
					marker=dict(color='rgb(55, 83, 109)'))

				bulan_rules = Bar(x=bulan_to_df.Bulan,
					y=bulan_to_df.jml_rules,
					name='Rules Yang Didapat',
					marker=dict(color='rgb(255, 145, 15)'))

				data = [bulan_semua, bulan_rules]
				layout = Layout(title="Data Bulan",
								yaxis=dict(title='Jumlah Data'),
								legend=dict(x=0,y=1.0),
								autosize=True,
								width=860)
				bln = Figure(data=data, layout=layout)
				
				blnJSON = json.dumps(bln, cls=plotly.utils.PlotlyJSONEncoder)
				bulan_export_rules = bulan_to_df.loc[bulan_to_df['jml_rules'] > 0]
				bulan_export_rules = bulan_export_rules[['Bulan', 'Rules']]
				data_rules_bulan = json2html.convert(json=bulan_export_rules.to_json(orient='records'), table_attributes="id=\"info-table\" class=\"table\"")
			
			else:
				blnJSON = {}
				data_rules_bulan = []

			if 'ResultKab' in result_join_count.columns:
				group_kab = result_join_count['ResultKab'].groupby(result_join_count['ResultKab']).count()
				group_kab_result = result_join_count['Result'].groupby(result_join_count['ResultKab'])
				dict_kab_rules = defaultdict(list)
				for key, item in group_kab_result:
					dict_kab_rules[key].append(item)
				dict_kab = defaultdict(list)
				for k, v in chain(listgroupby['kabupaten'].items(), group_kab.items(), dict_kab_rules.items()):
					if (not listgroupby['kabupaten'].empty):
						dict_kab[k].append(v)
					if group_kab.empty:
						v = 0
						dict_kab[k].append(v)
				kab_to_df = pd.DataFrame.from_dict(dict_kab, orient='index').reset_index().fillna(0)
				kab_to_df.columns = ['Kabupaten', 'semua', 'jml_rules', 'Rules']
				# chart bulan
				kab_semua = Bar(x=kab_to_df.Kabupaten,
					y=kab_to_df.semua,
					name='Semua Data',
					marker=dict(color='rgb(55, 83, 109)'))
				kab_rules = Bar(x=kab_to_df.Kabupaten,
					y=kab_to_df.jml_rules,
					name='Rules Yang Didapat',
					marker=dict(color='rgb(255, 145, 15)'))
				data = [kab_semua, kab_rules]
				layout = Layout(title="Data Kabupaten",
								yaxis=dict(title='Jumlah Data'),
								legend=dict(x=0,y=1.0),
								autosize=True,
								width=860)
				kab = Figure(data=data, layout=layout)
				
				kabJSON = json.dumps(kab, cls=plotly.utils.PlotlyJSONEncoder)
				kab_export_rules = kab_to_df.loc[kab_to_df['jml_rules'] > 0]
				kab_export_rules = kab_export_rules[['Kabupaten', 'Rules']]
				data_rules_kab = json2html.convert(json=kab_export_rules.to_json(orient='records'), table_attributes="id=\"info-table\" class=\"table\"")
			else:
				kabJSON = {}
				data_rules_kab = []

			if 'ResultActor1' in result_join_count.columns:
				group_act1 = result_join_count['ResultActor1'].groupby(result_join_count['ResultActor1']).count()
				group_act1_result = result_join_count['Result'].groupby(result_join_count['ResultActor1'])
				dict_act1_rules = defaultdict(list)
				for key, item in group_act1_result:
					dict_act1_rules[key].append(item)
				dict_act1 = defaultdict(list)
				for k, v in chain(listgroupby['actor_s1_tp'].items(), group_act1.items(), dict_act1_rules.items()):
					if (not listgroupby['actor_s1_tp'].empty):
						dict_act1[k].append(v)
					if group_act1.empty:
						v = 0
						dict_act1[k].append(v)
				act1_to_df = pd.DataFrame.from_dict(dict_act1, orient='index').reset_index().fillna(0)
				act1_to_df.columns = ['Actor1', 'semua', 'jml_rules', 'Rules']
				# chart actor 1
				act1_semua = Bar(x=act1_to_df.Actor1,
					y=act1_to_df.semua,
					name='Semua Data',
					marker=dict(color='rgb(55, 83, 109)'))
				act1_rules = Bar(x=act1_to_df.Actor1,
					y=act1_to_df.jml_rules,
					name='Rules Yang Didapat',
					marker=dict(color='rgb(255, 145, 15)'))
				data = [act1_semua, act1_rules]
				layout = Layout(title="Data Aktor 1",
								yaxis=dict(title='Jumlah Data'),
								legend=dict(x=0,y=1.0),
								autosize=True,
								width=860)
				act1 = Figure(data=data, layout=layout)
				
				act1JSON = json.dumps(act1, cls=plotly.utils.PlotlyJSONEncoder)
				act1_export_rules = act1_to_df.loc[act1_to_df['jml_rules'] > 0]
				act1_export_rules = act1_export_rules[['Actor1', 'Rules']]
				data_rules_act1 = json2html.convert(json=act1_export_rules.to_json(orient='records'), table_attributes="id=\"info-table\" class=\"table\"")
			else:
				act1JSON = {}
				data_rules_act1 = []

			if 'ResultActor2' in result_join_count.columns:
				group_act2 = result_join_count['ResultActor2'].groupby(result_join_count['ResultActor2']).count()
				group_act2_result = result_join_count['Result'].groupby(result_join_count['ResultActor2'])
				dict_act2_rules = defaultdict(list)
				for key, item in group_act2_result:
					dict_act2_rules[key].append(item)
				dict_act2 = defaultdict(list)
				for k, v in chain(listgroupby['actor_s2_tp'].items(), group_act2.items(), dict_act2_rules.items()):
					if (not listgroupby['actor_s2_tp'].empty):
						dict_act2[k].append(v)
					if group_act2.empty:
						v = 0
						dict_act2[k].append(v)
				act2_to_df = pd.DataFrame.from_dict(dict_act2, orient='index').reset_index().fillna(0)
				act2_to_df.columns = ['Actor2', 'semua', 'jml_rules', 'Rules']
				# chart actor 2
				act2_semua = Bar(x=act2_to_df.Actor2,
					y=act2_to_df.semua,
					name='Semua Data',
					marker=dict(color='rgb(55, 83, 109)'))
				act2_rules = Bar(x=act2_to_df.Actor2,
					y=act2_to_df.jml_rules,
					name='Rules Yang Didapat',
					marker=dict(color='rgb(255, 145, 15)'))
				data = [act2_semua, act2_rules]
				layout = Layout(title="Data Aktor 2",
								yaxis=dict(title='Jumlah Data'),
								legend=dict(x=0,y=1.0),
								autosize=True,
								width=860)
				act2 = Figure(data=data, layout=layout)
				
				act2JSON = json.dumps(act2, cls=plotly.utils.PlotlyJSONEncoder)
				act2_export_rules = act2_to_df.loc[act2_to_df['jml_rules'] > 0]
				act2_export_rules = act2_export_rules[['Actor2', 'Rules']]
				data_rules_act2 = json2html.convert(json=act2_export_rules.to_json(orient='records'), table_attributes="id=\"info-table\" class=\"table\"")
			else:
				act2JSON = {}
				data_rules_act2 = []
				
			if 'ResultWeap1' in result_join_count.columns:
				group_weap1 = result_join_count['ResultWeap1'].groupby(result_join_count['ResultWeap1']).count()
				group_weap1_result = result_join_count['Result'].groupby(result_join_count['ResultWeap1'])
				dict_weap1_rules = defaultdict(list)
				for key, item in group_weap1_result:
					dict_weap1_rules[key].append(item)
				dict_weap1 = defaultdict(list)
				for k, v in chain(listgroupby['weapon_1'].items(), group_weap1.items(), dict_weap1_rules.items()):
					if (not listgroupby['weapon_1'].empty):
						dict_weap1[k].append(v)
					if group_weap1.empty:
						v = 0
						dict_weap1[k].append(v)
				weap1_to_df = pd.DataFrame.from_dict(dict_weap1, orient='index').reset_index().fillna(0)
				weap1_to_df.columns = ['Senjata1', 'semua', 'jml_rules', 'Rules']
				# chart weapon1
				weap1_semua = Bar(x=weap1_to_df.Senjata1,
					y=weap1_to_df.semua,
					name='Semua Data',
					marker=dict(color='rgb(55, 83, 109)'))
				weap1_rules = Bar(x=weap1_to_df.Senjata1,
					y=weap1_to_df.jml_rules,
					name='Rules Yang Didapat',
					marker=dict(color='rgb(255, 145, 15)'))
				data = [weap1_semua, weap1_rules]
				layout = Layout(title="Data Senjata 1",
								yaxis=dict(title='Jumlah Data'),
								legend=dict(x=0,y=1.0),
								autosize=True,
								width=860)
				weap1 = Figure(data=data, layout=layout)
				
				weap1JSON = json.dumps(weap1, cls=plotly.utils.PlotlyJSONEncoder)
				weap1_export_rules = weap1_to_df.loc[weap1_to_df['jml_rules'] > 0]
				weap1_export_rules = weap1_export_rules[['Senjata1', 'Rules']]
				data_rules_weap1 = json2html.convert(json=weap1_export_rules.to_json(orient='records'), table_attributes="id=\"info-table\" class=\"table\"")
			else:
				weap1JSON = {}
				data_rules_weap1 = []
				
			if 'ResultWeap2' in result_join_count.columns:
				group_weap2 = result_join_count['ResultWeap2'].groupby(result_join_count['ResultWeap2']).count()
				group_weap2_result = result_join_count['Result'].groupby(result_join_count['ResultWeap2'])
				dict_weap2_rules = defaultdict(list)
				for key, item in group_weap2_result:
					dict_weap2_rules[key].append(item)
				dict_weap2 = defaultdict(list)
				for k, v in chain(listgroupby['weapon_2'].items(), group_weap2.items(), dict_weap2_rules.items()):
					if (not listgroupby['weapon_2'].empty):
						dict_weap2[k].append(v)
					if group_weap2.empty:
						v = 0
						dict_weap2[k].append(v)
				weap2_to_df = pd.DataFrame.from_dict(dict_weap1, orient='index').reset_index().fillna(0)
				weap2_to_df.columns = ['Senjata2', 'semua', 'jml_rules', 'Rules']
				# chart weapon2
				weap2_semua = Bar(x=weap2_to_df.Senjata2,
					y=weap2_to_df.semua,
					name='Semua Data',
					marker=dict(color='rgb(55, 83, 109)'))
				weap2_rules = Bar(x=weap2_to_df.Senjata2,
					y=weap2_to_df.jml_rules,
					name='Rules Yang Didapat',
					marker=dict(color='rgb(255, 145, 15)'))
				data = [weap2_semua, weap2_rules]
				layout = Layout(title="Data Senjata 2",
								yaxis=dict(title='Jumlah Data'),
								legend=dict(x=0,y=1.0),
								autosize=True,
								width=860)
				weap2 = Figure(data=data, layout=layout)
				
				weap2JSON = json.dumps(weap2, cls=plotly.utils.PlotlyJSONEncoder)
				weap2_export_rules = weap2_to_df.loc[weap2_to_df['jml_rules'] > 0]
				weap2_export_rules = weap2_export_rules[['Senjata2', 'Rules']]
				data_rules_weap2 = json2html.convert(json=weap2_export_rules.to_json(orient='records'), table_attributes="id=\"info-table\" class=\"table\"")
			else:
				weap2JSON = {}
				data_rules_weap2 = []
				
			if 'ResultJenisKek' in result_join_count.columns:
				group_jenisKek = result_join_count['ResultJenisKek'].groupby(result_join_count['ResultJenisKek']).count()
				group_jenisKek_result = result_join_count['Result'].groupby(result_join_count['ResultJenisKek'])
				dict_jenisKek_rules = defaultdict(list)
				for key, item in group_jenisKek_result:
					dict_jenisKek_rules[key].append(item)
				dict_jenisKek = defaultdict(list)
				for k, v in chain(listgroupby['jenis_kek'].items(), group_jenisKek.items(), dict_jenisKek_rules.items()):
					if group_jenisKek.empty:
						v = 0
					dict_jenisKek[k].append(v)
				jenisKek_to_df = pd.DataFrame.from_dict(dict_jenisKek, orient='index').reset_index().fillna(0)
				jenisKek_to_df.columns = ['JenisKekerasan', 'semua', 'jml_rules', 'Rules']
				# chart jenis kekerasan
				jenisKek_semua = Bar(x=jenisKek_to_df.JenisKekerasan,
					y=jenisKek_to_df.semua,
					name='Semua Data',
					marker=dict(color='rgb(55, 83, 109)'))
				jenisKek_rules = Bar(x=jenisKek_to_df.JenisKekerasan,
					y=jenisKek_to_df.jml_rules,
					name='Rules Yang Didapat',
					marker=dict(color='rgb(255, 145, 15)'))
				data = [jenisKek_semua, jenisKek_rules]
				layout = Layout(title="Data Jenis kekerasan",
								yaxis=dict(title='Jumlah Data'),
								legend=dict(x=0,y=1.0),
								autosize=True,
								width=860)
				jenisKek = Figure(data=data, layout=layout)
				
				jenisKekJSON = json.dumps(jenisKek, cls=plotly.utils.PlotlyJSONEncoder)
				jenisKek_export_rules = jenisKek_to_df.loc[jenisKek_to_df['jml_rules'] > 0]
				jenisKek_export_rules = jenisKek_export_rules[['JenisKekerasan', 'Rules']]
				data_rules_jenisKek = json2html.convert(json=jenisKek_export_rules.to_json(orient='records'), table_attributes="id=\"info-table\" class=\"table\"")
			else:
				jenisKekJSON = {}
				data_rules_jenisKek = []
				
			if 'ResultKatKek' in result_join_count.columns:
				group_katKek = result_join_count['ResultKatKek'].groupby(result_join_count['ResultKatKek']).count()
				group_katKek_result = result_join_count['Result'].groupby(result_join_count['ResultKatKek'])
				dict_katKek_rules = defaultdict(list)
				for key, item in group_katKek_result:
					dict_katKek_rules[key].append(item)
				dict_katKek = defaultdict(list)
				for k, v in chain(listgroupby['tp_kek1_new'].items(), group_katKek.items(), dict_katKek_rules.items()):
					if (not listgroupby['tp_kek1_new'].empty):
						dict_katKek[k].append(v)
					if group_katKek.empty:
						v = 0
						dict_katKek[k].append(v)
				katKek_to_df = pd.DataFrame.from_dict(dict_katKek, orient='index').reset_index().fillna(0)
				katKek_to_df.columns = ['KategoriKekerasan', 'semua', 'jml_rules', 'Rules']
				# chart kategori kekerasan
				katKek_semua = Bar(x=katKek_to_df.KategoriKekerasan,
					y=katKek_to_df.semua,
					name='Semua Data',
					marker=dict(color='rgb(55, 83, 109)'))
				katKek_rules = Bar(x=katKek_to_df.KategoriKekerasan,
					y=katKek_to_df.jml_rules,
					name='Rules Yang Didapat',
					marker=dict(color='rgb(255, 145, 15)'))
				data = [katKek_semua, katKek_rules]
				layout = Layout(title="Data Kategori Kekerasan",
								yaxis=dict(title='Jumlah Data'),
								legend=dict(x=0,y=1.0),
								autosize=True,
								width=860)
				katKek = Figure(data=data, layout=layout)
				
				katKekJSON = json.dumps(katKek, cls=plotly.utils.PlotlyJSONEncoder)
				katKek_export_rules = katKek_to_df.loc[katKek_to_df['jml_rules'] > 0]
				katKek_export_rules = katKek_export_rules[['KategoriKekerasan', 'Rules']]
				data_rules_katKek = json2html.convert(json=katKek_export_rules.to_json(orient='records'), table_attributes="id=\"info-table\" class=\"table\"")

			else:
				katKekJSON = {}
				data_rules_katKek = []
				
			if 'ResultBenKek' in result_join_count.columns:
				group_benKek = result_join_count['ResultBenKek'].groupby(result_join_count['ResultBenKek']).count()
				group_benKek_result = result_join_count['Result'].groupby(result_join_count['ResultBenKek'])
				dict_benKek_rules = defaultdict(list)
				for key, item in group_benKek_result:
					dict_benKek_rules[key].append(item)
				dict_benKek = defaultdict(list)
				for k, v in chain(listgroupby['ben_kek1'].items(), group_benKek.items(), dict_benKek_rules.items()):
					if (not listgroupby['ben_kek1'].empty):
						dict_benKek[k].append(v)
					if group_benKek.empty:
						v = 0
						dict_benKek[k].append(v)
				benKek_to_df = pd.DataFrame.from_dict(dict_benKek, orient='index').reset_index().fillna(0)
				benKek_to_df.columns = ['BentukKekerasan', 'semua', 'jml_rules', 'Rules']
				# chart bentuk Kekerasan
				benKek_semua = Bar(x=benKek_to_df.BentukKekerasan,
					y=benKek_to_df.semua,
					name='Semua Data',
					marker=dict(color='rgb(55, 83, 109)'))
				benKek_rules = Bar(x=benKek_to_df.BentukKekerasan,
					y=benKek_to_df.jml_rules,
					name='Rules Yang Didapat',
					marker=dict(color='rgb(255, 145, 15)'))
				data = [benKek_semua, benKek_rules]
				layout = Layout(title="Data Bentuk Kekerasan",
								yaxis=dict(title='Jumlah Data'),
								legend=dict(x=0,y=1.0),
								autosize=True,
								width=860)
				benKek = Figure(data=data, layout=layout)
				
				benKekJSON = json.dumps(benKek, cls=plotly.utils.PlotlyJSONEncoder)
				benKek_export_rules = benKek_to_df.loc[benKek_to_df['jml_rules'] > 0]
				benKek_export_rules = benKek_export_rules[['BentukKekerasan', 'Rules']]
				data_rules_benKek = json2html.convert(json=benKek_export_rules.to_json(orient='records'), table_attributes="id=\"info-table\" class=\"table\"")
			else:
				benKekJSON = {}
				data_rules_benKek = []

			# dataframe for map
			result_join_decode['ResultLoc'] = result_join_decode.apply(check_loc, axis=1)
			result_join_print = result_join_decode[['Result', 'ResultLoc', 'liftratio']]

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

		else:
			tahunJSON = {}
			blnJSON = {}
			kabJSON = {}
			act1JSON = {}
			act2JSON = {}
			weap1JSON = {}
			weap2JSON = {}
			jenisKekJSON = {}
			katKekJSON = {}
			benKekJSON = {}
			lift_max = {}
			lift_min = {}
			data_rules_tahun = []
			data_rules_bulan = []
			data_rules_kab = []
			data_rules_act1 = []
			data_rules_act2 = []
			data_rules_weap1 = []
			data_rules_weap2 = []
			data_rules_jenisKek = []
			data_rules_katKek = []
			data_rules_benKek = []
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
		trans_total = len(snpkframe31.index)

		# json_before_fpgrowth = snpkframe31.to_json(orient='split')

		# convert into matrix
		convMatrix = snpkframe31.as_matrix()

		# mencari pattern pada data kek_uji
		patterns = pyfpgrowth.find_frequent_patterns(convMatrix, min_sup)

		# mencari rules dari pattern yang telah dibuat
		rules = pyfpgrowth.generate_association_rules(patterns, min_conf, trans_total)
		timer = (time.time() - start_time)

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
			df_values.rename(columns={2: 'liftratio'}, inplace=True)

			df_values['first'] = df_values['first'].astype(str).str.strip('()')
			df_values_key = df_values['first'].str.split(',', expand=True)
			df_values_key = df_values_key.replace('', "None")

			df_values_conf = df_values['confident']
			df_values_lift = df_values['liftratio']
			lift_max = (df_values_lift.max()).round(4)
			lift_min = (df_values_lift.min()).round(4)
			df_values_key = df_values_key.apply(lambda x: x.str.strip("'")).apply(lambda x: x.str.strip(" '"))

			total_columns_value = len(df_values_key.columns)
			new_cols = ['values' + str(i) for i in df_values_key.columns]
			df_values_key.columns = new_cols[:total_columns_value]

			result_join = pd.concat([df_key, df_values_key, df_values_conf, df_values_lift], axis=1, join_axes=[df_key.index])

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
			tahunJSON = {}
			blnJSON = {}
			kabJSON = {}
			act1JSON = {}
			act2JSON = {}
			weap1JSON = {}
			weap2JSON = {}
			jenisKekJSON = {}
			katKekJSON = {}
			benKekJSON = {}
			lift_max = {}
			lift_min = {}
			data_rules_tahun = []
			data_rules_bulan = []
			data_rules_kab = []
			data_rules_act1 = []
			data_rules_act2 = []
			data_rules_weap1 = []
			data_rules_weap2 = []
			data_rules_jenisKek = []
			data_rules_katKek = []
			data_rules_benKek = []
		else:
			tahunJSON = {}
			blnJSON = {}
			kabJSON = {}
			act1JSON = {}
			act2JSON = {}
			weap1JSON = {}
			weap2JSON = {}
			jenisKekJSON = {}
			katKekJSON = {}
			benKekJSON = {}
			lift_max = {}
			lift_min = {}
			data_rules_tahun = []
			data_rules_bulan = []
			data_rules_kab = []
			data_rules_act1 = []
			data_rules_act2 = []
			data_rules_weap1 = []
			data_rules_weap2 = []
			data_rules_jenisKek = []
			data_rules_katKek = []
			data_rules_benKek = []
			converted_data = []
			total_rules = 0
			print_html = "Tidak ada rules"
			out_filter_result = "Tidak ada rules"

	# data_html = result_join.to_html(classes="table table-data")
	# data_html = data_html.replace('NaN', '')
	return render_template('show_selection.html', data=print_html, converted_data=converted_data, raw_data = out_filter_result, time_exe = timer, total_rules = total_rules, lift_max = lift_max, lift_min = lift_min, kabupaten_data=kabJSON, bulan_data=blnJSON, tahun_data=tahunJSON, act1_data=act1JSON, act2_data=act2JSON, weap1_data=weap1JSON, weap2_data=weap2JSON, jenisKek_data=jenisKekJSON, katKek_data=katKekJSON, benKek_data=benKekJSON, data_rules_tahun = data_rules_tahun, data_rules_bulan = data_rules_bulan, data_rules_kab = data_rules_kab, data_rules_act1 = data_rules_act1, data_rules_act2 = data_rules_act2, data_rules_weap1 = data_rules_weap1, data_rules_weap2 = data_rules_weap2, data_rules_jenisKek = data_rules_jenisKek, data_rules_katKek = data_rules_katKek, data_rules_benKek = data_rules_benKek)

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
