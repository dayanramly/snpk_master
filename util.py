def translate_bulan(bulan_num):
    bulan_definition = {
        1: "Januari",
        2: "Februari",
        3: "Maret",
        4: "April",
        5: "Mei",
        6: "Juni",
        7: "Juli",
        8: "Agustus",
        9: "September",
        10: "Oktober",
        11: "November",
        12: "Desember"
    }

    try:
        return bulan_definition[bulan_num]
    except KeyError:
        return "No translation for bulan number {}".format(bulan_num)

def translate_actor(actor_num):
    actor_definition = {
        1: "Tidak jelas",
        2: "Lainnya",
        3: "Milisi",
        4: "Warga",
        5: "Affiliasi dengan pemerintah",
        6: "Lembaga pemilihan",
        7: "Organisasi bantuan kemanusiaan asing / LSM Internasional (Termasuk Pekerjanya)",
        8: "LSM dalam negeri (Termasuk Pekerjanya)",
        9: "Perusahaan Swasta",
        10: "Partai Politik / Massa Pendukung",
        11: "Affiliasi dengan agama tertentu",
        12: "Serikat Buruh / Kelompok Pekerja (formal maupun informal)",
        13: "Ormas - bukan keagamaan",
        14: "TNI",
        15: "Polisi",
        16: "Brimob",
        17: "Kelompok Separatis",
        18: "Siswa Sekolah / Mahasiswa / Sekolah / Kampus",
        19: "Aparat Keamanan (Kesatuan Tidak Jelas)",
    }

    try:
        return actor_definition[actor_num]
    except KeyError:
        return "No translation for actor number {}".format(actor_num)


def translate_weapon(weapon_num):
    weapon_definition = {
        1: "Tidak Jelas",
        2: "Senjata Tumpul",
        3: "Lainnya",
        4: "Senjata Tajam",
        5: "Senjata Api Organik",
        6: "Bahan Peledak",
        7: "Senjata Api Rakitan",
        8: "Api",
        0: "Tidak Ada",
    }

    try:
        return weapon_definition[weapon_num]
    except KeyError:
        return "No translation for weapon number {}".format(weapon_num)

def translate_jenis_kek(jenis_kek_num):
    jenis_definition = {
        1: "Konflik",
        2: "Kekerasan dalam rumah tangga",
        3: "Kriminalitas ",
        4: "Kekerasan dalam penegakan hukum"
    }

    try:
        return jenis_definition[jenis_kek_num]
    except KeyError:
        return "No translation for jenis kekerasan number {}".format(jenis_kek_num)


def translate_tipe_kekerasan(tipe_kekerasan_num):
    tipe_kekerasan_definition = {
        1: "Tidak jelas",
        2: "Sumber Daya Lainnya",
        1102: "Isu Lahan",
        1103: "Isu Sumber Daya Alam",
        1104: "Isu Sumber Daya Buatan Manusia (Milik umum atau privat)",
        1105: "Isu Akses",
        1106: "Isu Lingkungan",
        1107: "Gaji/Upah/Perburuhan",
        1108: "Konflik Tata Kelola Pemerintahan",
        2202: "Tata Kelola Pemerintahan Lainnya",
        2203: "Tender",
        2204: "Korupsi",
        2205: "Pelayanan Publik",
        2206: "Harga Komoditas/Subsidi",
        2207: "Program Pemerintah",
        2211: "Pemekaran Wilayah",
        2212: "Penegakan Hukum",
        3302: "Konflik pemilihan dan jabatan",
        3303: "Pemilihan dan Jabatan Lain",
        3304: "Pemilihan/Jabatan Nasional",
        3305: "Pemilihan/Jabatan Provinsi",
        3306: "Pemilihan/Jabatan Kabupaten/Kota",
        3307: "Jabatan Kecamatan",
        3308: "Pemilihan/Jabatan Desa/Kelurahan",
        3309: "Jabata pemerintah lain",
        4402: "Jabatan/Pengaruh/Kekuasaan di dalam partai politik",
        4403: "Konflik Separatisme",
        4404: "Separatisme",
        4405: "Konflik Identitas",
        4406: "Identitas Lainnya",
        4407: "Antaretnis/antarsuku",
        4408: "Antaragama",
        4409: "Intraagama",
        4410: "Antara migran/pengungsi dengan lokal",
        4411: "Antara migran/pengungsi dengan lokal dan etnis tertentu",
        5503: "Gender",
        5504: "Identitas Olahraga",
        5505: "Identitas Sekolah/Universitas",
        5506: "Konflik main hakim sendiri",
        5507: "Main hakim sendiri lainnya",
        5508: "Pembalasan atas penghinaan",
        5509: "Pembalasan atas kecelakaan",
        5510: "Pembalasan atas hutang",
        5511: "Pembalasan atas pencurian",
        6603: "Pembalasan atas pengrusakan",
        7703: "Melawan/membalas perselingkuhan",
        8803: "Pembalasan atas penganiayaan",
        9903: "Melawan tempat maksiat",
    }

    try:
        return tipe_kekerasan_definition[tipe_kekerasan_num]
    except KeyError:
        return "No translation for tipe kekerasan number {}".format(tipe_kekerasan_num)


def translate_bentuk_kekerasan(bentuk_kekerasan_num):
    bentuk_kekerasan_definition = {
        1: "Tidak Jelas",
        2: "Lainnya",
        3: "Demonstrasi",
        4: "Blokade",
        5: "Kerusuhan",
        6: "Bentrokan",
        7: "Perkelahian",
        8: "Pengroyokan",
        9: "Serangan Teror",
        10: "Pengrusakan",
        11: "Penganiayaan",
        12: "Sweeping",
        13: "Penculikan",
        14: "Perampokan",
        0: "Tidak Ada",
    }

    try:
        return bentuk_kekerasan_definition[bentuk_kekerasan_num]
    except KeyError:
        return "No translation for bentuk kekerasan number {}".format(bentuk_kekerasan_num)

def translate_meta_kekerasan(meta_kekerasan_num):
    meta_kekerasan_definition = {
        88881: "Konflik Sumber Daya",
        88882: "Konflik Tata Kelola Pemerintahan",
        88883: "Konflik Pemilihan dan Jabatan",
        88884: "Konflik Identitas",
        88885: "Konflik main hakim sendiri",
        88886: "Kekerasan dalam penegakan hukum",
        88887: "Kriminalitas",
        88888: "Kekerasan dalam rumah tangga",
        88889: "Separatisme",
        88880: "Konflik Lainnya"
    }

    try:
        return meta_kekerasan_definition[meta_kekerasan_num]
    except KeyError:
        return "No translation for bentuk kekerasan number {}".format(meta_kekerasan_num)
