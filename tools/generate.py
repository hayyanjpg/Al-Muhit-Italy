# -*- coding: utf-8 -*-
"""Generator mod 'Al-Muhit Italy' (mod terpisah, fokus Italia).

Isi:
  - Semua state yang di-owner ITA pada 1936: manpower x2, resource x10.
  - 3 kota utama jadi megalopolis: Roma, Milano, Napoli.
  - History negara, OOB, fokus, bendera, tech Italia tetap vanilla.
  - Tanpa override map/ supaya tidak ada error 'Failed to load the map'.

Usage:  python tools/generate.py
"""
import os
import re

GAME = r"D:\SteamLibrary\steamapps\common\Hearts of Iron IV"
MOD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MANPOWER_MULTIPLIER = 2
RESOURCE_MULTIPLIER = 10
RESOURCE_KEYS = ("steel", "tungsten", "rubber", "chromium", "coal",
                 "aluminium", "oil")

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


def multiply_manpower(txt, fn):
    def repl(m):
        return m.group(1) + str(int(m.group(2)) * MANPOWER_MULTIPLIER)

    txt, n = re.subn(r"(manpower[ \t]*=[ \t]*)(\d+)", repl, txt, count=1)
    if n == 0:
        raise RuntimeError("baris manpower hilang di %s" % fn)
    return txt


def multiply_resources(txt):
    keys = "|".join(RESOURCE_KEYS)
    return re.sub(r"(\b(?:%s)[ \t]*=[ \t]*)(\d+)" % keys,
                  lambda m: m.group(1) + str(int(m.group(2)) *
                                             RESOURCE_MULTIPLIER), txt)


def write_states():
    src = os.path.join(GAME, "history", "states")
    for fn in ITALY_STATES:
        with open(os.path.join(src, fn), encoding="utf-8-sig",
                  errors="replace") as f:
            txt = f.read()

        txt = multiply_manpower(txt, fn)
        txt = multiply_resources(txt)

        tag = "manpower x2, resource x10"
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
  manpower **x2** (89.899.336 total) dan resource **x10**.
- Resource nasional Italia jadi: steel 620, aluminium 600, coal 40,
  chromium 20, tungsten 10 (rubber & oil tetap 0 sesuai vanilla).
- 3 kota utama jadi **megalopolis**: Roma (`2-Italy`), Milano
  (`159-Lombardy`), Napoli (`117-Napoli`).
- History negara, OOB, pemimpin, tech, fokus, warna, dan bendera Italia
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
    print("RESOURCE x10: %s" % ", ".join("%s %d" % (k, v)
                                        for k, v in res.items() if v))
    print("MEGALOPOLIS: %s" % ", ".join(MEGA_STATES))
    print("MOD:", MOD)


if __name__ == "__main__":
    main()
