# -*- coding: utf-8 -*-
"""Generator mod 'Al-Muhit Italy' (mod terpisah, fokus Italia).

Isi:
  - Semua state yang di-owner ITA pada 1936: manpower x2.
  - Resource: steel/aluminium x10 dari vanilla; coal/chromium/tungsten
    serta oil/rubber diset ke target total tertentu.
  - 3 kota utama jadi megalopolis: Roma, Milano, Napoli.
  - 200 tech dari mod Al-Muhit (sumber: save 1941.12.1) dipakai Italia.
  - History negara, OOB, fokus, bendera tetap vanilla.
  - Tanpa override map/ supaya tidak ada error 'Failed to load the map'.

Usage:  python tools/generate.py
"""
import os
import re

GAME = r"D:\SteamLibrary\steamapps\common\Hearts of Iron IV"
MOD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE_MOD = os.path.join(os.path.dirname(MOD), "Al-Muhit")

MANPOWER_MULTIPLIER = 2
RESOURCE_MULTIPLIER = 10
RESOURCE_KEYS = ("steel", "tungsten", "rubber", "chromium", "coal",
                 "aluminium", "oil")

# Total resource nasional yang diinginkan.
RESOURCE_TARGETS = {
    "steel": 620, "tungsten": 50, "rubber": 100, "chromium": 130,
    "coal": 120, "aluminium": 600, "oil": 100,
}

# Nilai final (bukan kelipatan) untuk state tertentu supaya total di atas
# tercapai. Steel & aluminium tetap hasil x10 dari vanilla.
RESOURCE_FIXES = {
    "114-Sardinia.txt": {"coal": 30},
    "158-Piedmont.txt": {"coal": 30, "chromium": 130, "tungsten": 50},
    "852-Istria.txt": {"coal": 60},
    "115-Sicily.txt": {"oil": 100},
    "844-jubaland.txt": {"rubber": 100},
}

# State yang di-owner ITA pada 1 Januari 1936 (termasuk koloni).
ITALY_STATES = [
    "2-Italy.txt",
    "114-Sardinia.txt",
    "115-Sicily.txt",
    "117-Napoli.txt",
    "157-Abruzzo.txt",
    "158-Piedmont.txt",
    "159-Lombardy.txt",
    "160-Veneto.txt",
    "161-Emilia Romagna.txt",
    "162-Tuscany.txt",
    "163-Dalmatia.txt",
    "156-Calabria.txt",
    "164-Dodecanese.txt",
    "273-Italian Africa.txt",
    "39-South Tyrol.txt",
    "448-Tripoli.txt",
    "449-Libyan Coast.txt",
    "450-Benghasi.txt",
    "451-Derna.txt",
    "550-Eritrea.txt",
    "559-Somaliland.txt",
    "661-Tripolitania.txt",
    "662-Sirte.txt",
    "663-Cyrenaica.txt",
    "736-Litorale.txt",
    "844-jubaland.txt",
    "849-Puglia.txt",
    "850-Trentino.txt",
    "852-Istria.txt",
]

# Roma, Milano, Napoli.
MEGA_STATES = [
    "2-Italy.txt",          # Roma / Lazio
    "159-Lombardy.txt",     # Milano
    "117-Napoli.txt",       # Napoli
]


def w(rel, text):
    path = os.path.join(MOD, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return path


def cleanup():
    state_dir = os.path.join(MOD, "history", "states")
    if os.path.isdir(state_dir):
        for fn in os.listdir(state_dir):
            if fn.endswith(".txt"):
                os.remove(os.path.join(state_dir, fn))
    hist = os.path.join(MOD, "history", "countries", "ITA - Italy.txt")
    if os.path.isfile(hist):
        os.remove(hist)


def read_tech_block():
    """Salin blok set_technology dari mod Al-Muhit (sumber 200 tech)."""
    path = os.path.join(SOURCE_MOD, "history", "countries",
                        "EGY - Egypt.txt")
    if not os.path.isfile(path):
        raise RuntimeError("Al-Muhit tidak ditemukan: %s" % path)
    with open(path, encoding="utf-8-sig", errors="replace") as f:
        txt = f.read()
    m = re.search(r"set_technology\s*=\s*\{.*?\n\}", txt, re.S)
    if m is None:
        raise RuntimeError("blok set_technology tidak ada di %s" % path)
    return m.group(0)


def write_country_history():
    src = os.path.join(GAME, "history", "countries", "ITA - Italy.txt")
    with open(src, encoding="utf-8-sig", errors="replace") as f:
        txt = f.read()
    tech = read_tech_block()
    marker = r"(capital\s*=\s*\d+[^\n]*\n)"
    txt, n = re.subn(marker,
                     lambda m: m.group(1) + "\n" + tech + "\n",
                     txt, count=1)
    if n == 0:
        raise RuntimeError("baris capital tidak ditemukan di history ITA")
    txt = ("# Al-Muhit Italy: 200 tech dari mod Al-Muhit "
           "(save 1941.12.1)\n" + txt)
    w("history/countries/ITA - Italy.txt", txt)


def multiply_manpower(txt, fn):
    def repl(m):
        return m.group(1) + str(int(m.group(2)) * MANPOWER_MULTIPLIER)

    txt, n = re.subn(r"(manpower[ \t]*=[ \t]*)(\d+)", repl, txt, count=1)
    if n == 0:
        raise RuntimeError("baris manpower hilang di %s" % fn)
    return txt


def parse_resources(txt):
    out = {}
    m = re.search(r"resources\s*=\s*\{([^}]*)\}", txt, re.S)
    if not m:
        return out
    for k in RESOURCE_KEYS:
        x = re.search(r"\b%s\s*=\s*(\d+)" % k, m.group(1))
        if x:
            out[k] = int(x.group(1))
    return out


def final_resources(txt, fn):
    values = {}
    for k, v in parse_resources(txt).items():
        values[k] = v * RESOURCE_MULTIPLIER
    values.update(RESOURCE_FIXES.get(fn, {}))
    return values


def set_resources(txt, values):
    if not any(values.get(k) for k in RESOURCE_KEYS):
        return txt

    block = "\tresources = {\n"
    for k in RESOURCE_KEYS:
        if values.get(k):
            block += "\t\t%s = %d\n" % (k, values[k])
    block += "\t}"

    txt, n = re.subn(r"^[ \t]*resources\s*=\s*\{[^}]*\}",
                     lambda _m: block, txt, count=1, flags=re.M)
    if n:
        return txt

    for pattern in (r"^([ \t]*state_category[ \t]*=[ \t]*\w+[^\n]*\n)",
                    r"^([ \t]*manpower[ \t]*=[ \t]*\d+[^\n]*\n)",
                    r"^([ \t]*id[ \t]*=[ \t]*\d+[^\n]*\n)"):
        m = re.search(pattern, txt, re.M)
        if m:
            return txt[:m.end()] + block + "\n" + txt[m.end():]
    raise RuntimeError("tidak ada tempat untuk memasang blok resources")


def write_states():
    src = os.path.join(GAME, "history", "states")
    for fn in ITALY_STATES:
        with open(os.path.join(src, fn), encoding="utf-8-sig",
                  errors="replace") as f:
            txt = f.read()

        values = final_resources(txt, fn)
        txt = multiply_manpower(txt, fn)
        txt = set_resources(txt, values)

        tag = "manpower x2, resource sesuai target"
        if fn in MEGA_STATES:
            txt, n = re.subn(r"state_category\s*=\s*\w+",
                             "state_category = megalopolis", txt, count=1)
            if n == 0:
                raise RuntimeError("state_category hilang di %s" % fn)
            tag += ", megalopolis"

        txt = "# Al-Muhit Italy: %s\n" % tag + txt
        w("history/states/" + fn, txt)
    return len(ITALY_STATES)


def write_descriptor():
    txt = ('name="Al-Muhit: Italian Mega"\n'
           'version="1.20.0.0"\n'
           'supported_version="1.20.*"\n'
           'path="mod/Al-Muhit Italy"\n')
    w("descriptor.mod", txt)
    w("Al-Muhit Italy.mod", txt)  # salinan di repo biar mudah dibagikan
    parent = os.path.join(os.path.dirname(MOD), "Al-Muhit Italy.mod")
    with open(parent, "w", encoding="utf-8", newline="\n") as f:
        f.write(txt)


def write_readme():
    txt = """# Al-Muhit: Italian Mega

Mod HOI4 1.20.x, **terpisah** dari mod Al-Muhit dan Al-Muhit Germany.
Tidak ada override `map/`.

## Isi mod
- Semua 29 state yang di-owner ITA pada 1936 (termasuk koloni):
  manpower **x2** (89.899.336 total). Steel & aluminium **x10**;
  resource lain mengikuti target di bawah.
- Resource nasional Italia jadi: steel 620, aluminium 600, coal 120,
  chromium 130, tungsten 50, oil 100, rubber 100.
- Oil 100 ditempatkan di Sicily (`115-Sicily.txt`), rubber 100 di
  Jubaland (`844-jubaland.txt`); sisanya mengikuti target di atas.
- 3 kota utama jadi **megalopolis**: Roma (`2-Italy`), Milano
  (`159-Lombardy`), Napoli (`117-Napoli`).
- **200 tech** dari mod Al-Muhit (save 1941.12.1) aktif sejak 1936.
- History negara, OOB, pemimpin, fokus, warna, dan bendera Italia
  tetap vanilla.

## Cara pakai
1. `python tools/generate.py`
2. Aktifkan mod **Al-Muhit: Italian Mega** di launcher.
3. Mainkan scenario 1936 sebagai Italia.
"""
    w("README.md", txt)


def main():
    cleanup()
    n = write_states()
    write_country_history()
    write_descriptor()
    write_readme()
    mp = 0
    res = {k: 0 for k in RESOURCE_KEYS}
    for fn in ITALY_STATES:
        txt = open(os.path.join(MOD, "history", "states", fn),
                   encoding="utf-8-sig", errors="replace").read()
        m = re.search(r"manpower\s*=\s*(\d+)", txt)
        if m:
            mp += int(m.group(1))
        rr = re.search(r"resources\s*=\s*\{([^}]*)\}", txt, re.S)
        if rr:
            for k in RESOURCE_KEYS:
                x = re.search(r"\b%s\s*=\s*(\d+)" % k, rr.group(1))
                if x:
                    res[k] += int(x.group(1))
    print("OK: %d state ITA, manpower x2 = %d" % (n, mp))
    if res != RESOURCE_TARGETS:
        raise RuntimeError("total resource %s (harap %s)" %
                           (res, RESOURCE_TARGETS))
    print("RESOURCE TARGET: %s" % ", ".join("%s %d" % (k, v)
                                            for k, v in res.items()))
    print("MEGALOPOLIS: %s" % ", ".join(MEGA_STATES))
    print("TECH       : 200 tech disalin dari mod Al-Muhit")
    print("MOD:", MOD)


if __name__ == "__main__":
    main()
