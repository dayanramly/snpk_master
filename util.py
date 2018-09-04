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
        1: "Tidak jelas / Lainnya",
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
        1: "Tidak Jelas / Lainnya",
        2: "Senjata Tumpul",
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
        1: "Tidak jelas / Sumber Daya Lainnya",
        4402: "Identitas Lainnya",
        4403: "Antaretnis/antarsuku",
        4404: "Antaragama",
        4405: "Intraagama",
        4406: "Antara migran/pengungsi dengan lokal",
        4407: "Antara migran/pengungsi dengan lokal dan etnis tertentu",
        4408: "Geografis",
        4409: "Gender",
        4410: "Identitas olahraga",
        4411: "Identitas sekolah atau universitas",
        5502: "Main hakim sendiri",
        5503: "Pembalasan atas penghinaan",
        5504: "Pembalasan atas kecelakaan",
        5505: "Pembalasan atas hutang",
        5507: "Pembalasan atas pengrusakan",
        5508: "Melawan / membalas perselingkuhan",
        5509: "Pembalasan atas penganiayaan",
        5510: "Melawan tempat maksiat",
        5511: "Melawan santet",
        6603: "Kekerasan dalam penegakan hukum",
        7703: "Kriminalitas",
        8803: "KDRT",
        9903: "Melawan tempat maksiat"

    }

    try:
        return tipe_kekerasan_definition[tipe_kekerasan_num]
    except KeyError:
        return "No translation for tipe kekerasan number {}".format(tipe_kekerasan_num)


def translate_bentuk_kekerasan(bentuk_kekerasan_num):
    bentuk_kekerasan_definition = {
        1: "Tidak Jelas / Lainnya / Tidak Ada",
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
    }

    try:
        return bentuk_kekerasan_definition[bentuk_kekerasan_num]
    except KeyError:
        return "No translation for bentuk kekerasan number {}".format(bentuk_kekerasan_num)

def translate_dampak(dampak_kode):
    dampak_kekerasan_definition = {
        'kil_f': "Terbunuh",
        'inj_f': "Luka-luka",
        'kid_f': "Penculikan",
        'sex_f': "Pelecehan Seksual",
        'bdg_des': "Bangunan Rusak",
        0: "Tidak Ada"
    }

    try:
        return dampak_kekerasan_definition[dampak_kode]
    except KeyError:
        return "No translation for bentuk kekerasan kode {}".format(dampak_kode)
