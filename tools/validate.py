# -*- coding: utf-8 -*-
"""Validator statis mod Al-Muhit Italy."""
import os
import re
import sys

MOD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARENT = os.path.dirname(MOD)

RESOURCE_TOTALS = {
    "steel": 620, "tungsten": 50, "rubber": 100, "chromium": 130,
    "coal": 120, "aluminium": 600, "oil": 100,
}

# fn: (manpower x2, resource final sesuai target)
STATE_EXPECT = {
    "2-Italy.txt": (5563942, {}),
    "114-Sardinia.txt": (1983842, {"coal": 30}),
    "115-Sicily.txt": (7673142, {"oil": 100}),
    "117-Napoli.txt": (8480000, {"steel": 150, "aluminium": 100}),
    "156-Calabria.txt": (3544000, {}),
    "157-Abruzzo.txt": (5958670, {}),
    "158-Piedmont.txt": (9530952, {"steel": 240, "tungsten": 50,
                                   "chromium": 130, "coal": 30,
                                   "aluminium": 160}),
    "159-Lombardy.txt": (11195408, {}),
    "160-Veneto.txt": (7926302, {"steel": 200, "aluminium": 110}),
    "161-Emilia Romagna.txt": (6404802, {"aluminium": 90}),
    "162-Tuscany.txt": (6169866, {}),
    "163-Dalmatia.txt": (36000, {}),
    "164-Dodecanese.txt": (240000, {}),
    "273-Italian Africa.txt": (85266, {}),
    "39-South Tyrol.txt": (596580, {"aluminium": 140}),
    "448-Tripoli.txt": (938272, {}),
    "449-Libyan Coast.txt": (80862, {}),
    "450-Benghasi.txt": (165070, {}),
    "451-Derna.txt": (91256, {}),
    "550-Eritrea.txt": (1201200, {"steel": 20}),
    "559-Somaliland.txt": (1543342, {"steel": 10}),
    "661-Tripolitania.txt": (35234, {}),
    "662-Sirte.txt": (26426, {}),
    "663-Cyrenaica.txt": (17616, {}),
    "736-Litorale.txt": (2076318, {}),
    "844-jubaland.txt": (2057790, {"rubber": 100}),
    "849-Puglia.txt": (5284000, {}),
    "850-Trentino.txt": (741478, {}),
    "852-Istria.txt": (251700, {"coal": 60}),
}

MEGA_STATES = ("2-Italy.txt", "159-Lombardy.txt", "117-Napoli.txt")

errors = []


def check(cond, msg):
    if not cond:
        errors.append(msg)


resource_sum = {k: 0 for k in RESOURCE_TOTALS}
mp_total = 0
for fn, (mp_expect, res_expect) in STATE_EXPECT.items():
    p = os.path.join(MOD, "history", "states", fn)
    check(os.path.isfile(p), "state hilang: %s" % fn)
    if not os.path.isfile(p):
        continue
    txt = open(p, encoding="utf-8-sig", errors="replace").read()

    m = re.search(r"manpower\s*=\s*(\d+)", txt)
    check(m is not None, "%s: baris manpower hilang" % fn)
    if m:
        got = int(m.group(1))
        mp_total += got
        check(got == mp_expect,
              "%s: manpower %d (harap %d)" % (fn, got, mp_expect))

    got_res = {}
    rr = re.search(r"resources\s*=\s*\{([^}]*)\}", txt, re.S)
    if rr:
        for k in RESOURCE_TOTALS:
            x = re.search(r"\b%s\s*=\s*(\d+)" % k, rr.group(1))
            if x:
                got_res[k] = int(x.group(1))
                resource_sum[k] += int(x.group(1))
    check(got_res == res_expect,
          "%s: resource %s (harap %s)" % (fn, got_res, res_expect))

    if fn in MEGA_STATES:
        check(re.search(r"state_category\s*=\s*megalopolis", txt) is not None,
              "%s: bukan megalopolis" % fn)

check(mp_total == 89899336,
      "total manpower = %d (harap 89899336)" % mp_total)
for k, v in RESOURCE_TOTALS.items():
    check(resource_sum[k] == v,
          "total %s = %d (harap %d)" % (k, resource_sum[k], v))

# --- country history: 200 tech dari Al-Muhit ---
hist = os.path.join(MOD, "history", "countries", "ITA - Italy.txt")
check(os.path.isfile(hist), "history country ITA hilang")
if os.path.isfile(hist):
    t = open(hist, encoding="utf-8-sig", errors="replace").read()
    check("capital = 2" in t, "capital Italia bukan 2")
    m = re.search(r"set_technology\s*=\s*\{(.*?)\n\}", t, re.S)
    check(m is not None, "blok set_technology hilang")
    if m:
        techs = re.findall(r"(?m)^\t([a-z0-9_]+) = (\d+)[ \t]*$",
                           m.group(1))
        check(len(techs) == 200,
              "jumlah tech = %d (harap 200)" % len(techs))
        check(dict(techs).get("mechanised_infantry2") == "2",
              "mechanised_infantry2 harus level 2 seperti save Al-Muhit")

# --- tidak ada override peta ---
mapdir = os.path.join(MOD, "map")
check(not os.path.isdir(mapdir) or not os.listdir(mapdir),
      "mod tidak boleh meng-override map/")

# --- descriptor ---
for p in (os.path.join(MOD, "descriptor.mod"),
          os.path.join(PARENT, "Al-Muhit Italy.mod"),
          os.path.join(MOD, "Al-Muhit Italy.mod")):
    check(os.path.isfile(p), "descriptor hilang: %s" % p)
    if os.path.isfile(p):
        t = open(p, encoding="utf-8-sig", errors="replace").read()
        check('version="1.20.0.0"' in t, "versi descriptor salah: %s" % p)
        check('supported_version="1.20.*"' in t,
              "supported_version salah: %s" % p)
        check('path="mod/Al-Muhit Italy"' in t,
              "path descriptor salah: %s" % p)

if errors:
    print("VALIDASI GAGAL:")
    for e in errors:
        print(" -", e)
    sys.exit(1)
print("VALIDASI OK: 29 state ITA (manpower x2, resource sesuai target), "
      "3 megalopolis (Roma/Milano/Napoli), 200 tech Al-Muhit, "
      "tanpa override map/.")
