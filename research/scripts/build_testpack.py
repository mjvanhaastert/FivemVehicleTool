#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bouwt het testpakket [vehicletests] uit de downloads in [Vehicles].

Gebruik (op de computer met de server):

  python3 -I build_testpack.py <resources-map> <scan-map> plan  <geval> [<geval> ...]
  python3 -I build_testpack.py <resources-map> <scan-map> build <geval> [<geval> ...]
  python3 -I build_testpack.py <resources-map> <scan-map> rewrite <geval> [<geval> ...]
  python3 -I build_testpack.py <resources-map> <scan-map> index

<geval> is een naam (vt_00_baseline), een begin van namen (vt_0), of all, wild,
made. <scan-map> bevat de units_*.json van scan_vehicles.py (modus units).
"index" schrijft alleen [vehicletests]/README.md opnieuw. "rewrite" schrijft van een gebouwd
geval alleen de eigen bestanden opnieuw (README.md, sources.json, fxmanifest.lua en
gewijzigde meta's) en controleert dat de gekopieerde bestanden gelijk zijn aan de bron.

Leest alleen uit [Vehicles]; schrijft alleen in [vehicletests]. Een geval waarvan
de map al bestaat, wordt overgeslagen. Bestanden worden alleen nieuw geschreven
(nooit overschreven), en er wordt niets verwijderd of hernoemd. Bestanden uit een
download blijven byte voor byte gelijk; alleen hun plek verandert (indeling B24).
Een gemaakt geval is een schoon voertuig met precies één wijziging.
"""
import hashlib
import json
import os
import posixpath as pp
import re
import sys
import xml.etree.ElementTree as ET

TODAY = '21 okt 2026'
OUT_CATEGORY = '[vehicletests]'

# pack-sleutel: (map in [Vehicles], scanbestand, resource in de scan)
PACKS = {
    'PLOKS': ('PLOKS_CARS', 'units_civ.json', 'PLOKS_CARS'),
    'LORE': ('Lore_Friendly_Car_Pack', 'units_lore.json', 'Lore_Friendly_Car_Pack'),
    'LDS': ('lds-lorevehicles', 'units_lds.json', ''),
    'ZACC': ('zaccflatlit', 'units_zaccflatlit.json', ''),
    'KRIEGER': ('kriegerty2', 'units_kriegerty2.json', ''),
    'STRMAN': ('strman', 'units_strman.json', ''),
}

DATA_FILE_TYPES = [  # volgorde in het manifest
    ('vehiclelayouts', 'VEHICLE_LAYOUTS_FILE'),
    ('handling', 'HANDLING_FILE'),
    ('vehicles', 'VEHICLE_METADATA_FILE'),
    ('carcols', 'CARCOLS_FILE'),
    ('carvariations', 'VEHICLE_VARIATION_FILE'),
]
REGISTERED = [t for t, _ in DATA_FILE_TYPES]

ROOT_TYPES = {
    'CVehicleModelInfo__InitDataList': 'vehicles',
    'CHandlingDataMgr': 'handling',
    'CVehicleModelInfoVariation': 'carvariations',
    'CVehicleModelInfoVarGlobal': 'carcols',
    'CVehicleMetadataMgr': 'vehiclelayouts',
    'CExtraTextMetaFile': 'dlctext',
    'ShopVehicleDataArray': 'shop_vehicle',
    'SContentUnlocks': 'contentunlocks',
}
NAME_TYPES = ('carvariations', 'carcols', 'handling', 'vehiclelayouts', 'vehicles',
              'dlctext', 'shop_vehicle', 'contentunlocks')


# ------------------------------------------------------------------ bronnen

def joaat(text):
    """Hash zoals GetHashKey (Jenkins one-at-a-time, kleine letters)."""
    h = 0
    for ch in text.lower().encode('utf-8'):
        h = (h + ch) & 0xFFFFFFFF
        h = (h + (h << 10)) & 0xFFFFFFFF
        h ^= h >> 6
    h = (h + (h << 3)) & 0xFFFFFFFF
    h ^= h >> 11
    h = (h + (h << 15)) & 0xFFFFFFFF
    return h


RX_TE = re.compile(r'AddTextEntry\s*\(\s*(["\'])(.+?)\1\s*,\s*(["\'])(.*?)\3\s*\)')
RX_TEH = re.compile(r'AddTextEntryByHash\s*\(\s*(0x[0-9A-Fa-f]+|\d+|`[^`]+`)\s*,\s*(["\'])(.*?)\2\s*\)')


class Src:
    _json = {}

    def __init__(self, ctx, key, upath=None):
        folder, jname, default_upath = PACKS[key]
        self.key = key
        self.folder = folder
        self.upath = default_upath if upath is None else upath
        if jname not in Src._json:
            Src._json[jname] = json.load(open(os.path.join(ctx['scan'], jname), encoding='utf-8'))
        for u in Src._json[jname]['units']:
            if u['path'] == self.upath:
                self.unit = u
                break
        else:
            raise SystemExit('resource %r niet in %s' % (self.upath, jname))
        # de packs staan nu direct in [Vehicles]/<map>; een geneste resource ligt daaronder
        self.nested = self.upath if self.upath != default_upath else ''
        self.root = os.path.join(ctx['res'], '[Vehicles]', folder, *([self.nested] if self.nested else []))
        self.files = self.unit['files']
        mi = self.unit.get('manifest_info') or {}
        self.author = mi.get('author')
        self.version = mi.get('version')
        self.manifest_info = mi

    def where(self, rel=''):
        p = '[Vehicles]/' + self.folder + ('/' + self.nested if self.nested else '')
        return p + ('/' + rel if rel else '')

    def label(self):
        extra = []
        if self.author:
            extra.append('maker volgens het manifest: %s' % self.author)
        if self.version:
            extra.append('versie %s' % self.version)
        return '`%s`%s' % (self.where(), (' (' + ', '.join(extra) + ')') if extra else '')

    def abs(self, rel):
        return os.path.join(self.root, *rel.split('/'))

    def raw(self, rel):
        with open(self.abs(rel), 'rb') as fh:
            return fh.read()

    def text_entries(self):
        """(per sleutel, per hash) uit AddTextEntry en AddTextEntryByHash in de .lua-bestanden."""
        if getattr(self, '_te', None) is None:
            bykey, byhash = {}, {}
            for f in sorted(self.files):
                if not f.lower().endswith('.lua'):
                    continue
                txt = self.raw(f).decode('utf-8', errors='replace')
                for _q, k, _q2, t in RX_TE.findall(txt):
                    bykey.setdefault(k.lower(), t)
                for h, _q, t in RX_TEH.findall(txt):
                    hv = joaat(h[1:-1]) if h.startswith('`') else int(h, 0) & 0xFFFFFFFF
                    byhash.setdefault(hv, t)
            self._te = (bykey, byhash)
        return self._te

    def label_for(self, model, game):
        bykey, byhash = self.text_entries()
        for k in (game, model):
            if k.lower() in bykey:
                return bykey[k.lower()], 'AddTextEntry'
            if joaat(k) in byhash:
                return byhash[joaat(k)], 'AddTextEntryByHash'
        return None, None


def meta_type(raw, name):
    try:
        root = ET.fromstring(raw).tag
    except ET.ParseError:
        root = None
    if root in ROOT_TYPES:
        return ROOT_TYPES[root]
    base = pp.basename(name).lower()
    for key in NAME_TYPES:
        if key in base:
            return key
    return None


def kit_parts(carcols_text):
    """(modelName, type) van de onderdelen in de kits; werkt ook bij kapotte XML."""
    parts = []
    for block in re.findall(r'<visibleMods>(.*?)</visibleMods>', carcols_text, flags=re.S):
        for item in re.findall(r'<Item>(.*?)</Item>', block, flags=re.S):
            mn = re.search(r'<modelName>\s*([^<]+?)\s*</modelName>', item)
            tp = re.search(r'<type>\s*([^<]+?)\s*</type>', item)
            if mn:
                parts.append((mn.group(1).lower(), tp.group(1) if tp else ''))
    for block in re.findall(r'<linkMods>(.*?)</linkMods>', carcols_text, flags=re.S):
        for item in re.findall(r'<Item>(.*?)</Item>', block, flags=re.S):
            mn = re.search(r'<modelName>\s*([^<]+?)\s*</modelName>', item)
            if mn:
                parts.append((mn.group(1).lower(), 'LINK'))
    return parts


class Plan:
    def __init__(self, case_id, c):
        self.case_id = case_id
        self.c = c
        self.files = {}      # doelpad -> ('copy', src, rel) of ('bytes', data, src, rel, wat)
        self.notes = []
        self.manifest = None
        self.readme_info = []
        self.skip = None     # reden om niet te bouwen

    def size(self):
        n = 0
        for spec in self.files.values():
            if spec[0] == 'copy':
                n += os.path.getsize(spec[1].abs(spec[2]))
            else:
                n += len(spec[1])
        return n


# ------------------------------------------------------------------ een voertuig uit een pack

def find_vehicle_meta(src, model):
    pat = re.compile(r'<modelName>\s*%s\s*</modelName>' % re.escape(model), re.I)
    for f in src.files:
        fl = f.lower()
        if not fl.endswith('.meta') or fl.startswith('stream/'):
            continue
        raw = src.raw(f)
        if pat.search(raw.decode('utf-8', errors='replace')) and meta_type(raw, f) == 'vehicles':
            return f
    return None


def collect_vehicle(src, model):
    vf = find_vehicle_meta(src, model)
    if vf is None:
        raise SystemExit('geen vehicles.meta met %s in %s' % (model, src.where()))
    data_dir = pp.dirname(vf)
    metas = sorted(f for f in src.files if pp.dirname(f) == data_dir and f.lower().endswith('.meta'))
    typed = [(f, meta_type(src.raw(f), f)) for f in metas]
    vtext = ''.join(src.raw(f).decode('utf-8', errors='replace') for f, t in typed if t == 'vehicles')
    ctext = ''.join(src.raw(f).decode('utf-8', errors='replace') for f, t in typed if t == 'carcols')
    # modellen en hun gameName: uit de scan als de XML te lezen was, anders uit de tekst
    vehicles = []
    for f, t in typed:
        if t != 'vehicles':
            continue
        parsed = ((src.unit.get('metas') or {}).get(f) or {}).get('vehicles')
        if parsed:
            vehicles += [(v['modelName'].lower(), v.get('gameName') or v['modelName'], v.get('txdName') or v['modelName']) for v in parsed if v.get('modelName')]
        else:
            txt = src.raw(f).decode('utf-8', errors='replace')
            vehicles += [(m.lower(), m, m) for m in re.findall(r'<modelName>\s*([^<]+?)\s*</modelName>', txt)]
    family = [m for m, _g, _t in vehicles]
    txds = {t.lower() for _m, _g, t in vehicles}
    stream = [f for f in src.files if f.lower().startswith('stream/')]
    base = set()
    for m in family:
        base |= {m + '.yft', m + '_hi.yft'}
    for t in txds:
        base |= {t + '.ytd', t + '+hi.ytd'}
    dirs = {pp.dirname(f).lower() for f in stream if pp.basename(f).lower() in base}
    for d in list(dirs):
        if d.startswith('stream/vehicles/'):
            dirs.add('stream/vehmods/' + d.split('/', 2)[2])
    sel = [f for f in stream if pp.dirname(f).lower() in dirs]
    parts = kit_parts(ctext)
    livery = {m for m, t in parts if t == 'VMT_LIVERY_MOD'}
    mods = {m for m, t in parts if t != 'VMT_LIVERY_MOD'}
    notes = []
    if 'stream' in dirs:  # alles plat in stream/: alleen wat bij dit voertuig hoort
        def mine(f):
            stem = pp.splitext(pp.basename(f))[0].lower()
            return (pp.dirname(f).lower() != 'stream' or stem in livery or stem in mods
                    or any(stem.startswith(x) for x in family) or any(stem.startswith(x) for x in txds))
        before = len(sel)
        sel = [f for f in sel if mine(f)]
        notes.append('stream/ van de bron is plat: %d van %d bestanden horen bij dit voertuig' % (len(sel), before))
    have = {pp.splitext(pp.basename(f))[0].lower() for f in sel}
    for p in sorted((livery | mods) - have):
        cands = [f for f in stream if pp.splitext(pp.basename(f))[0].lower() == p and f.lower().endswith(('.yft', '.ydr'))]
        if cands:
            sel.append(cands[0])
            notes.append('onderdeel %s staat elders in de bron: %s' % (p, cands[0]))
    missing_parts = sorted((livery | mods) - {pp.splitext(pp.basename(f))[0].lower() for f in sel})
    files = {}
    seen = {}
    counts = {'liveries': 0, 'mods': 0, 'stream': 0}
    for f in sorted(sel, key=lambda x: x.lower()):
        b = pp.basename(f)
        stem, ext = pp.splitext(b.lower())
        core = stem[:-3] if stem.endswith('_hi') else stem
        if ext in ('.yft', '.ydr') and core in livery:
            sub = 'liveries'
        elif ext in ('.yft', '.ydr') and core in mods:
            sub = 'mods'
        else:
            sub = 'stream'
        if b.lower() in seen:
            notes.append('naam twee keer in de bron: %s en %s (eerste gehouden)' % (seen[b.lower()], f))
            continue
        seen[b.lower()] = f
        counts[sub] += 1
        files['stream/' + b if sub == 'stream' else 'stream/%s/%s' % (sub, b)] = ('copy', src, f)
    skipped = []
    for f, t in typed:
        if t in REGISTERED:
            dest = 'data/%s.meta' % t
            n = 2
            while dest in files:
                dest = 'data/%s_%d.meta' % (t, n)
                n += 1
            files[dest] = ('copy', src, f)
        else:
            skipped.append((f, t))
    info = dict(src=src, data_dir=data_dir, stream_dirs=sorted({pp.dirname(f) for f in sel}),
                vehicles=vehicles, family=family, skipped=skipped, counts=counts,
                missing_parts=missing_parts, notes=notes, n_livery=len(livery), n_mods=len(mods))
    return files, info


def audio_for(src, name):
    """Eigen geluid van een voertuig uit een pack.

    De regels in het manifest van de pack staan per voertuig bij elkaar: GAMEDATA en
    SOUNDDATA (<naam>_game.dat, <naam>_sounds.dat) en daarna de WAVEPACK, waarvan de
    naam kan afwijken (rh4_game.dat hoort bij dlc_rh4elegy). Geeft terug: bestanden
    (doelpad -> spec), regels met nieuwe paden, regels met de paden van de pack,
    en wat ontbreekt.
    """
    a = name.lower()
    lines_orig = []
    missing = []
    take_wave = False
    for t, path in src.manifest_info.get('data_files') or []:
        if not t.startswith('AUDIO_'):
            continue
        last = path.rstrip('/').split('/')[-1].lower()
        if t == 'AUDIO_WAVEPACK':
            if take_wave or last == 'dlc_' + a:
                lines_orig.append((t, path))
            take_wave = False
        elif last.startswith(a + '_'):
            lines_orig.append((t, path))
            take_wave = True
        else:
            take_wave = False
    files = {}
    lines_new = []
    kept_orig = []
    missing_lines = []
    for t, path in lines_orig:
        base = path.rstrip('/')
        last = base.split('/')[-1]
        if t == 'AUDIO_WAVEPACK':
            hits = [f for f in src.files if f.lower().startswith(base.lower() + '/')]
            if not hits:
                missing.append('%s %s (map bestaat niet in de bron)' % (t, path))
                missing_lines.append((t, 'audio/sfx/' + last))
                continue
            for f in hits:
                files['audio/sfx/%s/%s' % (last, f[len(base) + 1:])] = ('copy', src, f)
            lines_new.append((t, 'audio/sfx/' + last))
        else:
            d = pp.dirname(base)
            hits = [f for f in src.files if pp.dirname(f).lower() == d.lower() and pp.basename(f).lower().startswith(last.lower())]
            if not hits:
                missing.append('%s %s (bestand bestaat niet in de bron)' % (t, path))
                continue
            for f in hits:
                files['audio/audioconfig/' + pp.basename(f)] = ('copy', src, f)
            lines_new.append((t, 'audio/audioconfig/' + last))
        kept_orig.append((t, path))
    # ook losse bestanden van dit voertuig (bijv. .nametable) in audio/audioconfig
    for f in src.files:
        low = f.lower()
        if low.startswith('audio/audioconfig/') and pp.basename(low).startswith(a + '_'):
            files.setdefault('audio/audioconfig/' + pp.basename(f), ('copy', src, f))
    return dict(files=files, lines=lines_new, lines_orig=kept_orig, missing=missing, missing_lines=missing_lines)


# ------------------------------------------------------------------ manifest en README

def lua_str(s):
    return "'" + s.replace('\\', '\\\\').replace("'", "\\'") + "'"


def default_files_list(files):
    out = []
    if any(k.startswith('data/') and k.endswith('.meta') for k in files):
        out.append('data/*.meta')
    exts = sorted({pp.splitext(k)[1] for k in files if k.startswith('audio/audioconfig/')})
    out += ['audio/audioconfig/*' + e for e in exts]
    for d in sorted({pp.dirname(k) for k in files if k.startswith('audio/sfx/')}):
        out.append(d + '/*.awc')
    return out


def default_data_lines(files):
    lines = []
    for t, dtype in DATA_FILE_TYPES:
        for k in sorted(files):
            if k == 'data/%s.meta' % t or re.fullmatch(r'data/%s_\d+\.meta' % t, k):
                lines.append((dtype, k))
    return lines


def manifest_text(p, title, author=None, files_list=None, data_lines=None, audio_lines=(), labels=(), extra=(), games=None):
    files = p.files
    L = ['-- %s: %s' % (p.case_id, title),
         '-- Testgeval in [vehicletests], gemaakt op %s. Zie README.md.' % TODAY, '',
         "fx_version 'cerulean'"]
    L.append(games or "game 'gta5'")
    L.append('')
    if author:
        L.append('author %s' % lua_str(author))
    L.append('description %s' % lua_str('Testgeval %s' % p.case_id))
    L.append('')
    if files_list is None:
        files_list = default_files_list(files)
    if files_list:
        L.append('files {')
        L += ['    %s,' % lua_str(x) for x in files_list]
        L += ['}', '']
    if data_lines is None:
        data_lines = default_data_lines(files)
    w = max([len(lua_str(t)) for t, _ in list(data_lines) + list(audio_lines)] + [0])
    for t, path in data_lines:
        L.append('data_file %s %s' % (lua_str(t).ljust(w), lua_str(path)))
    if audio_lines:
        L.append('')
        for t, path in audio_lines:
            L.append('data_file %s %s' % (lua_str(t).ljust(w), lua_str(path)))
    if labels:
        L += ['', '-- Naam in de game (B26 b): dev_vehicletools leest dit en zet de tekst.']
        for m, lab in labels:
            L.append('vehicle_label %s %s' % (lua_str(m), lua_str(lab)))
    if extra:
        L.append('')
        L += list(extra)
    return '\n'.join(L) + '\n'


def readme_text(p):
    c = p.c
    rows = ['# %s: %s' % (p.case_id, c['title']), '',
            '| | |', '|---|---|',
            '| **Probleem** | %s |' % c['problem'],
            '| **Bron** | %s |' % c.get('source_text', '–'),
            '| **Verwacht van de tool** | %s |' % c.get('expect', '–'),
            '| **Vraag** | %s |' % c.get('question', '–'),
            '| **In-game kijken** | %s |' % c.get('ingame', 'console en F8 bij het starten; spawnen; naam, kleuren, mods, geluid'),
            '| **Uitkomst** | nog niet getest |', '']
    if p.readme_info:
        rows += ['## Wat er in deze map staat', ''] + p.readme_info + ['']
    if p.notes:
        rows += ['## Opmerkingen bij het kopiëren', ''] + ['- ' + n for n in p.notes] + ['']
    rows += ['Gemaakt op %s met `build_testpack.py` (repo FivemVehicleTool, `research/scripts/`). '
             'Waar elk bestand vandaan komt: `sources.json`. De voertuigbestanden zijn van hun makers: '
             'alleen voor tests op de dev-server, niet in git en niet delen.' % TODAY, '']
    return '\n'.join(rows)


def info_lines(info, labels):
    src = info['src']
    L = ['- Bron: %s' % src.label(),
         '- Meta\'s uit `%s/`' % (info['data_dir'] or '.'),
         '- Modelbestanden uit %s' % ', '.join('`%s/`' % d for d in info['stream_dirs']),
         '- Modellen: %s' % ', '.join('`%s` (gameName `%s`)' % (m, g) for m, g, _t in info['vehicles']),
         '- In `stream/`: %d bestanden; `stream/mods/`: %d; `stream/liveries/`: %d (de kit noemt %d onderdelen, waarvan %d livery)'
         % (info['counts']['stream'], info['counts']['mods'], info['counts']['liveries'],
            info['n_mods'] + info['n_livery'], info['n_livery'])]
    if info['missing_parts']:
        L.append('- Onderdelen uit de kit zonder bestand in de bron (vanilla of ontbrekend): %s'
                 % ', '.join('`%s`' % x for x in info['missing_parts'][:12]) + (' …' if len(info['missing_parts']) > 12 else ''))
    if info['skipped']:
        L.append('- Niet meegenomen (geen van de vijf voertuig-types): %s'
                 % ', '.join('`%s` (%s)' % (pp.basename(f), t or 'onbekend') for f, t in info['skipped']))
    if labels:
        L.append('- Naam: %s (uit `%s` in de bron; nu als `vehicle_label` in het manifest, B26 b)'
                 % (', '.join('`%s` = "%s"' % (m, lab) for m, lab in labels), info.get('label_via') or 'AddTextEntry'))
    else:
        L.append('- Naam: de bron geeft geen tekst voor de gameName')
    return L


# ------------------------------------------------------------------ de gevallen

WILD = {
    'vt_00_baseline': dict(unit='PLOKS', model='tltypes', title='Schoon basisvoertuig (auto)',
        problem='Geen: de scan vond niets, niets boven 16 MiB. Basis voor de gemaakte gevallen (vt_6x en vt_7x).',
        expect='geen meldingen', question='B24 en B26 in de game (Q-S1, Q-S4)', ingame='spawnen; naam (via `vehicle_label`); kleuren'),
    'vt_01_nested_resource': dict(unit='LDS', model='zionks', mode='nested', title='Geluids-resource in de resource',
        problem='De geluids-resource van zionks staat als `[sounds]/zionks/` binnen deze resource, zoals in lds. Een resource in een resource laadt nooit, dus het eigen geluid ontbreekt. Start daarna ook `vt_01b_zionks_sounds` (dezelfde geluids-resource, nu los): dan hoort het eigen geluid er wel te zijn.',
        expect='R13 (resource in een resource)', question='R13; geluid uit een andere resource', ingame='motorgeluid zonder en met vt_01b'),
    'vt_01b_zionks_sounds': dict(unit='LDS', upath='[lorevehicles-sounds]/zionks', mode='unitcopy', title='Geluids-resource los (hoort bij vt_01)',
        problem='De geluids-resource van zionks uit lds, ongewijzigd, nu als eigen resource. Start na vt_01.',
        expect='geen', question='R13', ingame='motorgeluid van zionks'),
    'vt_02_xml_comment': dict(unit='PLOKS', model='bolide', title='XML: -- in een commentaar',
        problem='`vehicles.meta` heeft `<!------…---->`; een strikte XML-lezer weigert dat.',
        expect='M1', question='Q-M16: slikt de game dit?', ingame='bestaat het model als voertuig; spawnen'),
    'vt_03_xml_wrong_close': dict(unit='PLOKS', model='84rx7k', title='XML: <Kits> gaat nooit dicht',
        problem='`carcols.meta`: `<Kits>` wordt niet gesloten, en de kit staat binnen `<Lights>`.',
        expect='M1', question='Q-M16', ingame='mod-kit en onderdelen'),
    'vt_04_xml_nul_bytes': dict(unit='LDS', model='imperial', title='XML: NUL-bytes aan het eind',
        problem='`carvariations.meta` eindigt met NUL-bytes.', expect='M1', question='Q-M16, Q-M9', ingame='kleuren; mod-kit'),
    'vt_05_xml_space_before_decl': dict(unit='LDS', model='gstghell1', title='XML: spaties voor <?xml',
        problem='`carcols.meta` begint met drie spaties voor `<?xml`. Bijvangst: het eigen geluid zit in de geneste geluids-resource van lds en ontbreekt hier.',
        expect='M1', question='Q-M16', ingame='mod-kit en onderdelen'),
    'vt_06_model_without_yft': dict(unit='LDS', model='accolade', title='Voertuig zonder model',
        problem='`vehicles.meta` noemt ook `accolade2`, maar daar is geen `.yft` voor.', expect='M4',
        question='wat doet de game met een voertuig zonder model', ingame='accolade en accolade2 spawnen'),
    'vt_07_no_carvariations': dict(unit='PLOKS', model='sandero', title='Geen carvariations.meta',
        problem='Het voertuig heeft alleen `vehicles.meta`: geen `carvariations.meta`, `carcols.meta` of `handling.meta`. Het gebruikt de handling van de vanilla `Baller`.',
        expect='M2 (info), M28', question='Q-M9: wat mis je zonder carvariations', ingame='kleuren; mod-kit'),
    'vt_08_invalid_class': dict(unit='PLOKS', model='stingray', title='vehicleClass die niet bestaat',
        problem='`vehicleClass` is `VC_SPORTS` (bestaat niet; wel `VC_SPORT`). `gameName` heeft een spatie: `Corvette C8`.',
        expect='M27', question='Q-M17: welke klasse krijgt het voertuig', ingame='GetVehicleClass; naam'),
    'vt_09_no_label': dict(unit='LDS', model='blistacr', title='Geen tekst voor de naam',
        problem='Er is geen `AddTextEntry` voor de `gameName`.', expect='M16', question='Q-M18: wat ziet de speler', ingame='naam (GetLabelText)'),
    'vt_10_unknown_audio': dict(unit='LDS', model='hellenstorm', title='Onbekend geluid',
        problem='`audioNameHash` `hellenstorm` staat niet in de downloads en is geen vanilla-voertuignaam.',
        expect='M12', question='wat hoort de speler', ingame='motorgeluid'),
    'vt_11_vanilla_handling': dict(unit='LDS', model='surano3', title='Handling van een vanilla-voertuig',
        problem='`handlingId` is `SURANO` (vanilla). Mag; verwacht geen fout.', expect='M28 (info)', question='–', ingame='rijdt als een Surano'),
    'vt_12_kit_not_defined': dict(unit='LDS', model='yosemiteswb', title='Kit die niet in de eigen carcols staat',
        problem='`carvariations` noemt `0_suv_modkit`; het voertuig heeft geen eigen `carcols.meta`.', expect='M8',
        question='Q-M19: bestaat die kit in vanilla', ingame='mod-kit en onderdelen'),
    'vt_13_livery_mods': dict(unit='LDS', model='atlas', title='Liveries als mod-onderdeel',
        problem='Geen echt probleem: liveries als mod-onderdeel (soort 2), hier in `stream/liveries/`, en onderdelen in `stream/mods/`. Test voor de indeling met submappen.',
        expect='geen', question='Q-S4 in de game: werken submappen in stream/', ingame='aantal liveries en onderdelen in het mod-menu'),
    'vt_14_missing_wavepack': dict(unit='LORE', model='bati901', audio='bati901', keep_missing_audio=True, title='Geluidsmap die ontbreekt',
        problem='Het manifest noemt `AUDIO_WAVEPACK audio/sfx/dlc_bati901`, maar die map bestaat niet; `bati901_sounds.dat54.rel` verwijst naar `dlc_bati901/bati901` en `dlc_bati901/bati901_npc`. `vehicles.meta` heeft een lege `<audioNameHash />`.',
        expect='R4 (pad uit het manifest bestaat niet), M12', question='wat hoort de speler; geeft FiveM een melding', ingame='console en F8; motorgeluid'),
    'vt_20_unknown_types': dict(unit='KRIEGER', mode='asis', title='Onofficiële data_file-types',
        problem='Het manifest gebruikt `DLCTEXT_FILE` en `VEHICLE_SHOP_FILE`, die niet in de officiële lijst staan. Originele indeling van de converter (`common/`).',
        expect='R14', question='Q-M15: negeert FiveM ze, of komt er een melding', ingame='console en F8'),
    'vt_21_all_types_glob': dict(unit='LORE', model='buffaloh', mode='lore_style', title='Elke meta onder elk type',
        problem='Manifest zoals de Lore-pack: `data/**/*.meta` onder elk type, ook twee onofficiële. Originele mappen van de pack.',
        expect='R6, R14', question='Q-S13: wat doet de game met een meta onder het verkeerde type', ingame='spawnen; kleuren; mods; geluid'),
    'vt_22_old_manifest': dict(unit='ZACC', mode='asis', title='__resource.lua en ontbrekende bestanden',
        problem='Oud manifest (`__resource.lua`); `carcols.meta` en `vehiclelayouts.meta` uit het manifest bestaan niet.',
        expect='R2, R3, R4', question='Q-S9 (de start is getest); werkt de trailer', ingame='trailer spawnen'),
    'vt_30a_kit_id_rcf': dict(unit='PLOKS', model='rcf', title='Kit-id 689 (paar met vt_30b)',
        problem='Kit-id 689, net als `dubstag` in vt_30b. Start ze allebei.', expect='X4', question='Q-S6: welke kit wint', ingame='onderdelen van allebei'),
    'vt_30b_kit_id_dubstag': dict(unit='LDS', model='dubstag', title='Kit-id 689 (paar met vt_30a)',
        problem='Kit-id 689, net als `rcf` in vt_30a.', expect='X4', question='Q-S6', ingame='onderdelen van allebei'),
    'vt_31a_stream_name_f430s': dict(unit='PLOKS', model='f430s', title='Zelfde bestandsnamen (paar met vt_31b)',
        problem='`spoiler_2.yft` en `spoiler_3.yft` bestaan ook in vt_31b, met andere inhoud.', expect='X1', question='Q-S6: welk bestand wint', ingame='spoilers van allebei'),
    'vt_31b_stream_name_gs350': dict(unit='PLOKS', model='gs350', title='Zelfde bestandsnamen (paar met vt_31a)',
        problem='`spoiler_2.yft` en `spoiler_3.yft` bestaan ook in vt_31a.', expect='X1', question='Q-S6', ingame='spoilers van allebei'),
    'vt_32a_vorstand_lds': dict(unit='LDS', model='vorstand', title='Zelfde voertuig twee keer (lds)',
        problem='`vorstand` uit lds; vt_32b is dezelfde auto uit de Lore-pack (zelfde model, bestandsnamen en kit-id 701).',
        expect='X1, X2, X4', question='Q-S6: welke versie wint', ingame='welke versie verschijnt'),
    'vt_32b_vorstand_lore': dict(unit='LORE', model='vorstand', audio='vorstand', title='Zelfde voertuig twee keer (Lore)',
        problem='`vorstand` uit de Lore-pack, met eigen geluid; zie vt_32a.', expect='X1, X2, X4', question='Q-S6', ingame='welke versie verschijnt'),
    'vt_33_vanilla_vehicle': dict(unit='LORE', model='futo2', title='Vervangt een vanilla-voertuig',
        problem='`futo2` is ook een vanilla-voertuig (Futo GTX). Bijvangst: `fInitialDriveForce` 4,79.',
        expect='X5', question='Q-T6: vervangt het de vanilla-versie', ingame='futo2 spawnen'),
    'vt_34_vanilla_kit': dict(unit='PLOKS', model='wildtrak', title='Kits met een vanilla-naam',
        problem='`carcols.meta` definieert `268_hermes_modkit` en `269_revolter_modkit`.', expect='M21',
        question='Q-M19: raakt dit de vanilla Hermes en Revolter', ingame='mods van wildtrak, hermes en revolter'),
    'vt_40_over_16': dict(unit='PLOKS', model='cutlass', title='Te groot: boven 16 MiB',
        problem='Een bestand van 26 MiB in het geheugen: blauwe melding.', expect='T1', question='Q-T1 (getest), Q-T2', ingame='laadt alles; laat'),
    'vt_41_over_32': dict(unit='LDS', model='rhinetaxi', title='Te groot: boven 32 MiB',
        problem='Een bestand van 40 MiB: gele melding.', expect='T1', question='Q-T2', ingame='laadt alles'),
    'vt_42_over_48': dict(unit='PLOKS', model='nissantitan17', title='Te groot: boven 48 MiB',
        problem='Een bestand van 52 MiB: gele melding met "WILL lead to streaming issues".', expect='T1', question='Q-T2', ingame='laadt alles'),
    'vt_43_over_64_ytd': dict(unit='PLOKS', model='i8', title='Te groot: .ytd van 128 MiB',
        problem='`i8.ytd`: 128 MiB in het geheugen, 1,5 MB op schijf. Ook om te verkleinen (Q-T4).', expect='T1', question='Q-T2, Q-T4', ingame='textures'),
    'vt_44_yft_with_textures': dict(unit='LDS', model='ingotc', title='Textures in het model',
        problem='`ingotc_interiormod.yft`: 128 MiB phys, textures in het model.', expect='T1', question='Q-T2', ingame='interieur-onderdeel'),
    'vt_45_escrow': dict(unit='STRMAN', mode='asis', title='Escrow',
        problem='Versleutelde bestanden; zonder recht op het asset start de resource niet (getest). 76 MiB; `carcols.meta` uit het manifest ontbreekt.',
        expect='R9, T2', question='Q-T7', ingame='console'),
    'vt_46_rpf_in_stream': dict(unit='PLOKS', model='rculi', title='.rpf in stream/',
        problem='`rculi_mods.rpf` staat in `stream/`.', expect='F9', question='Q-S14: wat doet FiveM ermee', ingame='console; mods'),
    'vt_50_ten_gears': dict(unit='PLOKS', model='720s', title='Tien versnellingen',
        problem='`nInitialDriveGears` is 10.', expect='M19', question='Q-H14: kapt de game af op een maximum', ingame='GetVehicleHandlingInt nInitialDriveGears; rijden'),
    'vt_51_extreme_force': dict(unit='LORE', model='ruiner6str', title='Extreme aandrijfkracht',
        problem='`fInitialDriveForce` 4,79 (90% van de downloads zit tussen 0,20 en 0,525).', expect='M19', question='Q-H4, Q-H5', ingame='optrekken'),
}

# Gemaakt: een schoon voertuig (standaard vt_00) met precies één wijziging
MADE = {
    'vt_13b_atlas_kit_948': dict(base=dict(unit='LDS', model='atlas'), title='Als vt_13, met kit-id 948',
        problem='Kopie van vt_13 (atlas uit lds) met één wijziging: in `data/carcols.meta` is `<id value="620"/>` nu `<id value="948"/>`, het id dat bij vt_00 werkte. Werkt de kit nu wel, dan ligt het aan id 620. Niet tegelijk met vt_00 of vt_6x/vt_7x starten (die gebruiken 948).',
        expect='geen', question='X4: waarom heeft atlas met kit-id 620 geen kit', change='sub:carcols:<id value="620"\\s*/>:<id value="948"/>', ingame='GetNumModKits; liveries (mod 48)'),
    'vt_13c_atlas_kit_1500': dict(base=dict(unit='LDS', model='atlas'), title='Als vt_13, met kit-id 1500',
        problem='Kopie van vt_13 (atlas uit lds) met één wijziging: in `data/carcols.meta` is `<id value="620"/>` nu `<id value="1500"/>`. Werkt een kit-id boven 1023?',
        expect='geen', question='Q-M4: werkt een kit-id boven 1023', change='sub:carcols:<id value="620"\\s*/>:<id value="1500"/>', ingame='GetNumModKits; liveries (mod 48)'),
    'vt_60_no_carvariations': dict(title='Zonder carvariations.meta', problem='`data/carvariations.meta` weggelaten.',
        expect='M2', question='Q-S8, Q-M9', change='drop:carvariations', ingame='spawnen; kleuren; mod-kit'),
    'vt_61_no_carcols': dict(title='Zonder carcols.meta', problem='`data/carcols.meta` weggelaten (de kit `948_tltypes_modkit` en licht 948 vallen weg).',
        expect='M2, M8', question='Q-S8', change='drop:carcols', ingame='spawnen; mod-kit; lichten'),
    'vt_62_no_layouts': dict(title='Zonder vehiclelayouts.meta', problem='`data/vehiclelayouts.meta` weggelaten.',
        expect='M2', question='Q-S8', change='drop:vehiclelayouts'),
    'vt_63_with_dlctext': dict(title='Met dlctext.meta', problem='`dlctext.meta` uit de bron erbij, als `DLCTEXT_FILE` (vt_00 laat hem weg, zoals B24 zegt).',
        expect='R14', question='Q-M2, Q-M15: doet `DLCTEXT_FILE` iets, en komt er een melding', change='add:dlctext', ingame='console en F8; naam'),
    'vt_65_no_audioname': dict(title='Zonder audioNameHash', problem='`<audioNameHash>` uit `vehicles.meta` gehaald.',
        expect='M3', question='Q-M14', change='sub:vehicles:\\s*<audioNameHash>[^<]*</audioNameHash>:', ingame='motorgeluid'),
    'vt_66_xml_bom': dict(title='XML met BOM', problem='Een UTF-8-BOM voor `vehicles.meta`.',
        expect='M1 (info)', question='Q-M16', change='bom:vehicles', ingame='bestaat het voertuig'),
    'vt_67_xml_ampersand': dict(title='XML met een losse &', problem='`vehicleMakeName` is `Acura&Co` (een losse `&`, ongeldige XML).',
        expect='M1', question='Q-M16', change='sub:vehicles:<vehicleMakeName>([^<]*)</vehicleMakeName>:<vehicleMakeName>\\1&Co</vehicleMakeName>', ingame='bestaat het voertuig'),
    'vt_68_txd_missing': dict(title='txdName die niet bestaat', problem='`txdName` is `tltypes_bestaatniet`.',
        expect='M5', question='wat zie je zonder textures', change='sub:vehicles:<txdName>[^<]*</txdName>:<txdName>tltypes_bestaatniet</txdName>', ingame='uiterlijk'),
    'vt_69_bad_layout': dict(title='Layout die niet bestaat', problem='`layout` is `LAYOUT_BESTAATNIET`.',
        expect='M11', question='kun je instappen', change='sub:vehicles:<layout>[^<]*</layout>:<layout>LAYOUT_BESTAATNIET</layout>', ingame='instappen'),
    'vt_70_class_mismatch': dict(title='Klasse die niet bij het type past', problem='`vehicleClass` is `VC_MOTORCYCLE` bij een auto.',
        expect='M17', question='wat doet de game ermee', change='sub:vehicles:<vehicleClass>[^<]*</vehicleClass>:<vehicleClass>VC_MOTORCYCLE</vehicleClass>', ingame='GetVehicleClass; rijden'),
    'vt_73_meta_not_in_files': dict(title="Meta's niet in files {}", problem='Het manifest heeft geen `files {}`; de `data_file`-regels zijn gelijk aan vt_00.',
        expect='R15', question='laadt het voertuig', change='nofiles', ingame='bestaat het voertuig'),
    'vt_74_glob_case': dict(title='Hoofdletters in een glob', problem="De regel voor `vehicles.meta` is `data/**/Vehicles.meta` (hoofdletter V); het bestand heet `vehicles.meta`. De andere regels zijn gelijk aan vt_00.",
        expect='R16', question='Q-S3: is de glob hoofdlettergevoelig', change='globcase', ingame='bestaat het voertuig'),
    'vt_75_glob_star_folder': dict(title='* in een mapnaam', problem="De meta's staan in `data/x/`; `files { 'data/x/*.meta' }` klopt, maar de `data_file`-regels zijn `data/*/<type>.meta`.",
        expect='Q-S3', question='vindt een `*` in een mapnaam iets (broncode: nee)', change='starfolder', ingame='bestaat het voertuig'),
    'vt_76_stream_not_root': dict(title='stream/ niet in de root', problem='De modelbestanden staan in `assets/stream/` in plaats van `stream/`.',
        expect='F10', question='wordt het gestreamd (broncode: nee)', change='streamdeep', ingame='bestaat het model'),
    'vt_79_handling_missing': dict(title='handlingId die niet bestaat', problem='`handlingId` is `TLTYPES_BESTAATNIET`; `handling.meta` blijft gelijk.',
        expect='M6', question='welke handling krijgt het voertuig', change='sub:vehicles:<handlingId>[^<]*</handlingId>:<handlingId>TLTYPES_BESTAATNIET</handlingId>', ingame='spawnen; GetVehicleHandlingFloat; rijden'),
    'vt_80_clean_bike': dict(base=dict(unit='LORE', model='bati901'), title='Schone motor',
        problem='`bati901` uit de Lore-pack in de indeling van B24, zonder het eigen geluid (de geluidsmap ontbreekt in de bron, zie vt_14) en met het geluid van de vanilla Bati: de lege `<audioNameHash />` wordt `<audioNameHash>BATI</audioNameHash>`.',
        expect='geen', question='referentie motor (Q-M12, Q-S8)', change='sub:vehicles:<audioNameHash\\s*/>|<audioNameHash>[^<]*</audioNameHash>:<audioNameHash>BATI</audioNameHash>', what='geen eigen geluid; in `data/vehicles.meta` is `<audioNameHash />` nu `<audioNameHash>BATI</audioNameHash>`', ingame='spawnen; geluid; rijden'),
    'vt_81_clean_trailer': dict(base=dict(unit='ZACC', model='zaccflatlit'), title='Schone trailer',
        problem='`zaccflatlit` in de indeling van B24: een nieuw manifest met alleen de meta\'s die bestaan. Verder ongewijzigd.',
        expect='M16 (geen naam in de bron)', question='referentie trailer (Q-M12, Q-S8)', change='none', ingame='spawnen; koppelen'),
}

ALL = dict(WILD)
ALL.update(MADE)


# ------------------------------------------------------------------ plannen

def plan_layout(ctx, case_id, c):
    p = Plan(case_id, c)
    src = Src(ctx, c['unit'])
    files, info = collect_vehicle(src, c['model'])
    p.files.update(files)
    p.notes += info['notes']
    audio_lines = []
    if c.get('audio'):
        au = audio_for(src, c['audio'])
        p.files.update(au['files'])
        audio_lines = au['lines']
        if c.get('keep_missing_audio'):
            audio_lines = audio_lines + au['missing_lines']
            for m in au['missing']:
                p.notes.append('bewust gehouden, zoals in de bron: %s' % m)
        else:
            for m in au['missing']:
                p.notes.append('weggelaten uit het manifest van de bron: %s' % m)
    labels = []
    how = set()
    for m, g, _t in info['vehicles']:
        lab, via = src.label_for(m, g)
        if lab:
            labels.append((m, lab))
            how.add(via)
    info['label_via'] = ' en '.join(sorted(how))
    p.readme_info = info_lines(info, labels)
    if audio_lines:
        p.readme_info.append('- Geluid: %s' % ', '.join('`%s %s`' % x for x in audio_lines))
    p.info = info
    p.labels = labels
    p.audio_lines = audio_lines
    p.src = src
    c = dict(c)
    c['source_text'] = src.label()
    p.c = c
    p.manifest = manifest_text(p, c['title'], author=src.author, audio_lines=audio_lines, labels=labels)
    return p


def plan_wild(ctx, case_id, c):
    mode = c.get('mode', 'layout')
    if mode == 'layout':
        return plan_layout(ctx, case_id, c)
    if mode == 'nested':
        p = plan_layout(ctx, case_id, c)
        snd = Src(ctx, c['unit'], '[lorevehicles-sounds]/' + c['model'])
        for f in snd.files:
            p.files['[sounds]/%s/%s' % (c['model'], f)] = ('copy', snd, f)
        p.readme_info.append('- `[sounds]/%s/`: de geluids-resource uit `%s`, ongewijzigd' % (c['model'], snd.where()))
        return p
    if mode == 'unitcopy':
        p = Plan(case_id, c)
        src = Src(ctx, c['unit'], c['upath'])
        for f in src.files:
            p.files[f] = ('copy', src, f)
        c = dict(c)
        c['source_text'] = '`%s`, ongewijzigd (eigen manifest)' % src.where()
        p.c = c
        p.readme_info = ['- Alles uit `%s`, met het eigen manifest van de bron' % src.where()]
        return p
    if mode == 'asis':
        p = Plan(case_id, c)
        src = Src(ctx, c['unit'])
        for dp, dn, fn in os.walk(src.root):
            dn[:] = sorted(d for d in dn if not d.startswith('.'))
            for f in sorted(fn):
                rel = os.path.relpath(os.path.join(dp, f), src.root).replace(os.sep, '/')
                p.files[rel] = ('copy', src, rel)
        c = dict(c)
        c['source_text'] = '%s, ongewijzigd (eigen indeling en manifest)' % src.label()
        p.c = c
        p.readme_info = ['- Alles uit `%s` (behalve mappen die met een punt beginnen), met het eigen manifest' % src.where()]
        return p
    if mode == 'lore_style':
        p = plan_layout(ctx, case_id, c)
        src, info = p.src, p.info
        orig = {}
        for f in src.files:
            d = pp.dirname(f).lower()
            if pp.dirname(f) == info['data_dir'] or d in {x.lower() for x in info['stream_dirs']}:
                orig[f] = ('copy', src, f)
        au = audio_for(src, c.get('audio') or c['model'])
        for _k, spec in au['files'].items():
            orig[spec[2]] = spec
        for m in au['missing']:
            p.notes.append('weggelaten uit het manifest van de bron: %s' % m)
        p.files = orig
        mi = src.manifest_info
        data_lines = [(t, path) for t, path in mi.get('data_files') or [] if not t.startswith('AUDIO_')]
        audio_orig = au['lines_orig']
        fl = (mi.get('lists') or {}).get('files') or ['data/**/*.meta']
        games = None
        if mi.get('games'):
            games = 'games { %s }' % ', '.join(lua_str(g) for g in mi['games'])
        p.manifest = manifest_text(p, c['title'], author=src.author, files_list=fl, data_lines=data_lines,
                                   audio_lines=audio_orig, labels=p.labels, games=games)
        p.readme_info = ['- Bron: %s' % src.label(),
                         '- Mappen en namen zoals in de pack: %s' % ', '.join('`%s/`' % d for d in sorted({pp.dirname(k) for k in orig})),
                         '- Manifest: de `files`- en `data_file`-regels van de pack, alleen de geluidsregels van dit voertuig']
        return p
    raise SystemExit('onbekende modus %s' % mode)


def plan_made(ctx, case_id, c):
    base_spec = c.get('base')
    if base_spec:
        bc = dict(base_spec, title=c['title'], problem=c['problem'])
        base = plan_layout(ctx, case_id, bc)
    else:
        base = plan_layout(ctx, 'vt_00_baseline', WILD['vt_00_baseline'])
    p = Plan(case_id, c)
    p.files = dict(base.files)
    p.notes = list(base.notes)
    p.readme_info = list(base.readme_info)
    p.labels = base.labels
    src = base.src
    kind, _, arg = c['change'].partition(':')
    files_list = None
    data_lines = None
    extra = ()
    what = None
    if kind == 'none':
        pass
    elif kind == 'drop':
        key = 'data/%s.meta' % arg
        if key not in p.files:
            p.skip = 'het basisvoertuig heeft geen %s.meta; het basisvoertuig zelf is dit geval al' % arg
            return p
        del p.files[key]
        what = '`%s` weggelaten' % key
    elif kind == 'add':
        cand = [f for f, t in base.info['skipped'] if t == arg]
        if not cand:
            p.skip = 'de bron heeft geen %s.meta' % arg
            return p
        p.files['data/%s.meta' % arg] = ('copy', src, cand[0])
        extra = ["data_file 'DLCTEXT_FILE' 'data/%s.meta'" % arg]
        what = '`data/%s.meta` erbij (uit `%s`)' % (arg, cand[0])
        fixed = []
        for line in p.readme_info:
            if line.startswith('- Niet meegenomen'):
                line = re.sub(r',?\s*`%s` \(%s\)' % (re.escape(pp.basename(cand[0])), re.escape(arg)), '', line)
                if line.rstrip().endswith(':'):
                    continue
            fixed.append(line)
        p.readme_info = fixed
    elif kind in ('sub', 'bom'):
        which, _, rest = arg.partition(':')
        key = 'data/%s.meta' % which
        spec = p.files[key]
        raw = spec[1].raw(spec[2])
        if kind == 'bom':
            if raw.startswith(b'\xef\xbb\xbf'):
                p.skip = 'de bron heeft al een BOM'
                return p
            new = b'\xef\xbb\xbf' + raw
            what = 'BOM voor `%s`' % key
        else:
            pat, _, rep = rest.partition(':')
            txt = raw.decode('utf-8', errors='surrogateescape')
            out, n = re.subn(pat, rep, txt, count=1)
            if n != 1:
                p.skip = 'patroon niet gevonden: %s' % pat
                return p
            new = out.encode('utf-8', errors='surrogateescape')
            what = '`%s`: `%s` vervangen door `%s`' % (key, pat.replace('\\s*', ''), rep.replace('\\1', '…') or '(niets)')
        p.files[key] = ('bytes', new, spec[1], spec[2], what)
    elif kind == 'nofiles':
        files_list = []
        what = 'geen `files {}` in het manifest'
    elif kind == 'globcase':
        data_lines = [(t, 'data/**/Vehicles.meta' if t == 'VEHICLE_METADATA_FILE' else path)
                      for t, path in default_data_lines(p.files)]
        what = "`data_file 'VEHICLE_METADATA_FILE' 'data/**/Vehicles.meta'`"
    elif kind == 'starfolder':
        moved = {}
        for k, spec in p.files.items():
            moved['data/x/' + k[5:] if k.startswith('data/') else k] = spec
        p.files = moved
        files_list = ['data/x/*.meta']
        data_lines = [(dtype, 'data/*/%s.meta' % t) for t, dtype in DATA_FILE_TYPES if 'data/x/%s.meta' % t in p.files]
        what = "meta's in `data/x/`, `data_file`-regels als `data/*/<type>.meta`"
    elif kind == 'streamdeep':
        p.files = {('assets/' + k if k.startswith('stream/') else k): spec for k, spec in p.files.items()}
        what = '`stream/` verplaatst naar `assets/stream/`'
    else:
        raise SystemExit('onbekende wijziging %s' % c['change'])
    what = c.get('what') or what
    c = dict(c)
    c['source_text'] = ('gemaakt uit %s' % src.label()) if base_spec else 'gemaakt: `vt_00_baseline` (`tltypes` uit %s) met één wijziging' % src.label()
    p.c = c
    if what:
        p.readme_info = ['- **De wijziging:** %s' % what] + p.readme_info
    p.manifest = manifest_text(p, c['title'], author=src.author, files_list=files_list, data_lines=data_lines,
                               audio_lines=base.audio_lines, labels=p.labels, extra=extra)
    return p


def plan_case(ctx, case_id):
    if case_id in WILD:
        return plan_wild(ctx, case_id, WILD[case_id])
    return plan_made(ctx, case_id, MADE[case_id])


# ------------------------------------------------------------------ bouwen

def write_new(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'xb') as fh:
        fh.write(data)


def copy_new(src_path, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    h = hashlib.md5()
    n = 0
    with open(src_path, 'rb') as fi, open(path, 'xb') as fo:
        while True:
            b = fi.read(1 << 20)
            if not b:
                break
            h.update(b)
            fo.write(b)
            n += len(b)
    if os.path.getsize(path) != os.path.getsize(src_path):
        raise SystemExit('kopie niet compleet: %s' % path)
    return h.hexdigest(), n


def build(ctx, p):
    dest = os.path.join(ctx['out'], p.case_id)
    if os.path.exists(dest):
        return 'bestaat al, overgeslagen'
    if p.skip:
        return 'niet gebouwd: ' + p.skip
    os.makedirs(dest)
    record = []
    for rel in sorted(p.files):
        spec = p.files[rel]
        target = os.path.join(dest, *rel.split('/'))
        if spec[0] == 'copy':
            md5, n = copy_new(spec[1].abs(spec[2]), target)
            record.append(dict(path=rel, source=spec[1].where(spec[2]), bytes=n, md5=md5))
        else:
            write_new(target, spec[1])
            record.append(dict(path=rel, source=spec[2].where(spec[3]), bytes=len(spec[1]),
                               md5=hashlib.md5(spec[1]).hexdigest(), changed=spec[4]))
    meta = dict(case=p.case_id, built=TODAY, generator='build_testpack.py', files=record)
    taken = {k.lower() for k in p.files}
    rd = 'README.md' if 'readme.md' not in taken else 'README_testgeval.md'
    sj = 'sources.json' if 'sources.json' not in taken else 'sources_testgeval.json'
    write_new(os.path.join(dest, sj), json.dumps(meta, indent=1, ensure_ascii=False).encode('utf-8'))
    write_new(os.path.join(dest, rd), readme_text(p).encode('utf-8'))
    if p.manifest:  # als laatste: zonder manifest is een halve map geen resource
        write_new(os.path.join(dest, 'fxmanifest.lua'), p.manifest.encode('utf-8'))
    return 'gebouwd: %d bestanden, %.1f MB' % (len(record), sum(r['bytes'] for r in record) / 1e6)


def md5_file(path):
    h = hashlib.md5()
    with open(path, 'rb') as fh:
        for b in iter(lambda: fh.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def rewrite(ctx, p):
    """Schrijft de eigen bestanden van een gebouwd geval opnieuw (README, sources.json,
    manifest en gewijzigde meta's). Gekopieerde bestanden uit een download worden alleen
    vergeleken met de bron, nooit geschreven."""
    dest = os.path.join(ctx['out'], p.case_id)
    if not os.path.exists(dest):
        return 'bestaat niet; eerst build'
    if p.skip:
        return 'niet gebouwd: ' + p.skip
    record = []
    for rel in sorted(p.files):
        spec = p.files[rel]
        target = os.path.join(dest, *rel.split('/'))
        if spec[0] == 'copy':
            if not os.path.exists(target):
                return 'FOUT: %s ontbreekt (eerst de map wegzetten en opnieuw bouwen)' % rel
            m = md5_file(target)
            if m != md5_file(spec[1].abs(spec[2])):
                return 'FOUT: %s wijkt af van de bron' % rel
            record.append(dict(path=rel, source=spec[1].where(spec[2]), bytes=os.path.getsize(target), md5=m))
        else:
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with open(target, 'wb') as fh:
                fh.write(spec[1])
            record.append(dict(path=rel, source=spec[2].where(spec[3]), bytes=len(spec[1]),
                               md5=hashlib.md5(spec[1]).hexdigest(), changed=spec[4]))
    own = {'readme.md', 'readme_testgeval.md', 'sources.json', 'sources_testgeval.json', 'fxmanifest.lua'}
    extra = []
    for dp, dn, fn in os.walk(dest):
        for f in fn:
            rel = os.path.relpath(os.path.join(dp, f), dest).replace(os.sep, '/')
            if rel not in p.files and rel.lower() not in own:
                extra.append(rel)
    taken = {k.lower() for k in p.files}
    rd = 'README.md' if 'readme.md' not in taken else 'README_testgeval.md'
    sj = 'sources.json' if 'sources.json' not in taken else 'sources_testgeval.json'
    meta = dict(case=p.case_id, built=TODAY, generator='build_testpack.py', files=record)
    with open(os.path.join(dest, sj), 'wb') as fh:
        fh.write(json.dumps(meta, indent=1, ensure_ascii=False).encode('utf-8'))
    with open(os.path.join(dest, rd), 'wb') as fh:
        fh.write(readme_text(p).encode('utf-8'))
    if p.manifest:
        with open(os.path.join(dest, 'fxmanifest.lua'), 'wb') as fh:
            fh.write(p.manifest.encode('utf-8'))
    return 'opnieuw geschreven' + (('; bestanden die niet meer in het plan staan: %s' % ', '.join(extra)) if extra else '')


def index(ctx):
    rows = ['# Testpakket `[vehicletests]`', '',
            'Elk geval is een eigen resource. Start er één tegelijk (`ensure vt_00_baseline`), behalve de paren (vt_30, vt_31, vt_32) en vt_01 met vt_01b. '
            'Niet tegelijk met de downloads in `[Vehicles]`: die bevatten dezelfde voertuigen. Deze map staat niet in `server.cfg`.', '',
            'De gemaakte gevallen (vt_60 en hoger) gebruiken dezelfde model- en bestandsnamen als het voertuig waaruit ze gemaakt zijn; ook daarvan draait er steeds één.', '',
            'Uitleg per geval: de `README.md` in de map. Beschrijving en uitkomsten: `doc/test_pack.md` in de repo FivemVehicleTool. '
            'De voertuigbestanden zijn van hun makers: alleen voor tests op deze dev-server, niet in git en niet delen.', '',
            '| Geval | Wat | Verwacht | Vraag | Gebouwd |', '|-------|-----|----------|-------|---------|']
    for cid, c in ALL.items():
        built = 'ja' if os.path.exists(os.path.join(ctx['out'], cid, 'fxmanifest.lua')) or os.path.exists(os.path.join(ctx['out'], cid, '__resource.lua')) else 'nee'
        rows.append('| `%s` | %s | %s | %s | %s |' % (cid, c['title'], c.get('expect', '–'), c.get('question', '–'), built))
    rows += ['', 'Gemaakt met `build_testpack.py` op %s.' % TODAY, '']
    path = os.path.join(ctx['out'], 'README.md')
    data = '\n'.join(rows).encode('utf-8')
    if os.path.exists(path):
        # overschrijven mag hier: dit bestand maken we zelf, het is geen voertuigbestand
        with open(path, 'wb') as fh:
            fh.write(data)
    else:
        write_new(path, data)
    return path


def select(ids):
    out = []
    for i in ids:
        if i == 'all':
            out += list(ALL)
        elif i == 'wild':
            out += list(WILD)
        elif i == 'made':
            out += list(MADE)
        elif i in ALL:
            out.append(i)
        else:
            m = [k for k in ALL if k.startswith(i)]
            if not m:
                raise SystemExit('onbekend geval: %s' % i)
            out += m
    seen = set()
    return [x for x in out if not (x in seen or seen.add(x))]


def main(argv):
    if len(argv) < 4:
        print(__doc__)
        return 2
    ctx = dict(res=argv[1], scan=argv[2], out=os.path.join(argv[1], OUT_CATEGORY))
    cmd = argv[3]
    if cmd == 'index':
        print(index(ctx))
        return 0
    ids = select(argv[4:])
    if cmd == 'build':
        os.makedirs(ctx['out'], exist_ok=True)
    for cid in ids:
        try:
            p = plan_case(ctx, cid)
            if cmd == 'plan':
                print('== %s  (%s)  %d bestanden, %.1f MB%s' % (cid, ALL[cid].get('mode', 'gemaakt' if cid in MADE else 'layout'),
                      len(p.files), p.size() / 1e6, ('  OVERSLAAN: ' + p.skip) if p.skip else ''))
                for line in p.readme_info:
                    print('   ' + line)
                for n in p.notes:
                    print('   ! ' + n)
                if '-v' in os.environ.get('TESTPACK_FLAGS', ''):
                    print(p.manifest)
            elif cmd == 'rewrite':
                print('%-30s %s' % (cid, rewrite(ctx, p)), flush=True)
            else:
                print('%-30s %s' % (cid, build(ctx, p)), flush=True)
        except SystemExit as exc:
            print('%-30s FOUT: %s' % (cid, exc), flush=True)
        except Exception as exc:  # noqa: één geval mag de rest niet tegenhouden
            print('%-30s FOUT: %r' % (cid, exc), flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
