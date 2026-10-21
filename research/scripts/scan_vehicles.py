#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Onderzoeksscan van voertuig-resources. Leest alleen, schrijft niets in de gescande map.

Gebruik:
  python3 -I scan_vehicles.py fivem-view <resources_root> <out.json>
      Doet na hoe de FiveM-server resources vindt (ServerResourceList.cpp):
      alleen mappen met [haken] worden doorzocht; elke andere map is een resource.

  python3 -I scan_vehicles.py units <scan_root> <out.json>
      Zoekt elke map met fxmanifest.lua of __resource.lua (ook diep genest),
      leest manifest, meta's, AddTextEntry in .lua, en de eerste 16 bytes van
      resource-bestanden (RSC7-header), en schrijft alles naar JSON.

Bronnen voor de regels: FiveM-broncode (citizenfx/fivem, master 20 okt 2026):
  ServerResourceList.cpp, ResourceStreamComponent.cpp, ResourceMetaDataComponent.cpp,
  ResourcesTest.cpp. Zie doc/sources.md.
"""
import json
import os
import re
import struct
import sys
import time
import xml.etree.ElementTree as ET

MANIFESTS = ('fxmanifest.lua', '__resource.lua')
# Bestanden waarvan we de 16-byte header lezen
RSC_EXT = {'.ytd', '.yft', '.ydr', '.ydd', '.ycd', '.ybn', '.ypt', '.ynv', '.ymap', '.ytyp', '.ynd', '.ymf', '.ymt'}
TEXT_EXT = {'.meta', '.xml', '.lua', '.json', '.md', '.txt', '.ini', '.cfg', '.sql'}


def size_from_flags(flags):
    # Zelfde formule als ConvertRSC7Size in ResourceStreamComponent.cpp
    s = (((flags >> 27) & 0x1) << 0) + (((flags >> 26) & 0x1) << 1) \
        + (((flags >> 25) & 0x1) << 2) + (((flags >> 24) & 0x1) << 3) \
        + (((flags >> 17) & 0x7F) << 4) + (((flags >> 11) & 0x3F) << 5) \
        + (((flags >> 7) & 0xF) << 6) + (((flags >> 5) & 0x3) << 7) \
        + (((flags >> 4) & 0x1) << 8)
    return ((0x200 << (flags & 0xF)) * s) & 0xFFFFFFFF


def read_head(path, n=16):
    try:
        with open(path, 'rb') as fh:
            return fh.read(n)
    except OSError as exc:
        return exc


def classify_binary(path):
    head = read_head(path)
    if isinstance(head, Exception):
        return {'k': 'err', 'e': str(head)[:120]}
    magic = head[:4]
    if magic == b'RSC7' and len(head) == 16:
        ver, sys_f, gfx_f = struct.unpack('<III', head[4:16])
        return {'k': 'rsc7', 'v': ver, 'vm': size_from_flags(sys_f), 'pm': size_from_flags(gfx_f)}
    if magic == b'RSC8' and len(head) == 16:
        ver, sys_f, gfx_f = struct.unpack('<III', head[4:16])
        return {'k': 'rsc8', 'v': ver, 'vm': size_from_flags(sys_f), 'pm': size_from_flags(gfx_f)}
    if magic == b'FXAP':
        return {'k': 'fxap'}
    if magic == b'7FPR':
        enc = head[12:16]
        return {'k': 'rpf7', 'enc': enc.decode('latin-1') if enc == b'OPEN' else enc.hex()}
    if head[:5] == b'<?xml' or head[:1] == b'<' or head[:3] == b'\xef\xbb\xbf':
        return {'k': 'xml'}
    return {'k': 'other', 'm': magic.hex()}


# ---------------------------------------------------------------- FiveM-scan

def fivem_view(resources_root):
    """Doet de BFS van ServerResourceList::ScanResources na."""
    resources = []
    categories = []
    warnings = []
    seen = {}
    queue = [resources_root]
    while queue:
        this = queue.pop(0)
        try:
            names = sorted(os.listdir(this), key=lambda s: s.lower())
        except OSError as exc:
            warnings.append({'type': 'list_failed', 'path': this, 'error': str(exc)})
            continue
        for name in names:
            if name in ('.', '..', '.git'):
                continue
            full = os.path.join(this, name)
            if not os.path.isdir(full):
                continue
            rel = os.path.relpath(full, resources_root).replace('\\', '/')
            if name.startswith('[') and name.endswith(']'):
                queue.append(full)
                has_manifest = any(os.path.isfile(os.path.join(full, m)) for m in MANIFESTS)
                categories.append({'path': rel, 'has_manifest': has_manifest})
                if has_manifest:
                    warnings.append({'type': 'category_manifest', 'path': rel})
                continue
            if name.startswith('.') or name.lower() == 'txadmin':
                continue
            if name in seen:
                warnings.append({'type': 'duplicate_resource', 'name': name, 'used': seen[name], 'duplicate': rel})
                continue
            seen[name] = rel
            manifest = next((m for m in MANIFESTS if os.path.isfile(os.path.join(full, m))), None)
            resources.append({'name': name, 'path': rel, 'manifest': manifest})
            if manifest is None:
                warnings.append({'type': 'no_manifest', 'name': name, 'path': rel})
    return {'root': resources_root, 'resources': resources, 'categories': categories, 'warnings': warnings}


# ---------------------------------------------------------------- manifest

def strip_lua_comments(text):
    text = re.sub(r'--\[(=*)\[.*?\]\1\]', '', text, flags=re.S)
    out = []
    for line in text.splitlines():
        # simpel: '--' buiten een string; goed genoeg voor manifests
        idx = None
        in_s = None
        i = 0
        while i < len(line):
            c = line[i]
            if in_s:
                if c == '\\':
                    i += 2
                    continue
                if c == in_s:
                    in_s = None
            elif c in ('"', "'"):
                in_s = c
            elif line.startswith('--', i):
                idx = i
                break
            i += 1
        out.append(line if idx is None else line[:idx])
    return '\n'.join(out)


STR_RE = r'''(?:'([^'\n]*)'|"([^"\n]*)"|\[\[(.*?)\]\])'''


def _strings(blob):
    return [a or b or c for a, b, c in re.findall(STR_RE, blob, flags=re.S)]


def parse_manifest(path):
    raw = open(path, 'rb').read()
    text = raw.decode('utf-8', errors='replace')
    info = {'bom': raw.startswith(b'\xef\xbb\xbf')}
    code = strip_lua_comments(text)
    info['lines'] = text.count('\n') + 1

    def single(key):
        m = re.search(r'\b' + key + r'\s*\(?\s*' + STR_RE, code, flags=re.S)
        if m:
            return m.group(1) or m.group(2) or m.group(3)
        return None

    info['fx_version'] = single('fx_version')
    info['resource_manifest_version'] = single('resource_manifest_version')
    info['game'] = single('game')
    m = re.search(r'\bgames\s*\(?\s*\{(.*?)\}', code, flags=re.S)
    info['games'] = _strings(m.group(1)) if m else []
    info['lua54'] = single('lua54')
    info['this_is_a_map'] = single('this_is_a_map')
    info['author'] = single('author')
    info['version'] = single('version')

    data_files = []
    for mm in re.finditer(r'\bdata_file\s*\(?\s*' + STR_RE + r'\s*\)?\s*\(?\s*' + STR_RE, code, flags=re.S):
        g = mm.groups()
        dtype = g[0] or g[1] or g[2]
        pat = g[3] or g[4] or g[5]
        data_files.append([dtype, pat])
    info['data_files'] = data_files

    lists = {}
    for key in ('file', 'files', 'client_script', 'client_scripts', 'server_script', 'server_scripts',
                'shared_script', 'shared_scripts', 'ui_page', 'dependency', 'dependencies', 'escrow_ignore'):
        vals = []
        for mm in re.finditer(r'(?<![\w.])' + key + r'\s*\(?\s*(\{.*?\}|' + STR_RE + r')', code, flags=re.S):
            vals.extend(_strings(mm.group(1)))
        if vals:
            lists[key] = vals
    info['lists'] = lists
    return info


def _fivem_name_regex(part, ignore_case):
    # Zelfde omzetting als de Match-struct in ResourceMetaDataComponent.cpp:
    # alles escapen, dan '?' -> '.' en '*' -> '.*'
    rx = ''.join('.*' if ch == '*' else '.' if ch == '?' else re.escape(ch) for ch in part)
    return re.compile('^' + rx + '$', re.I if ignore_case else 0)


def _norm(path):
    path = path.replace('\\', '/')
    out = []
    for seg in path.split('/'):
        if seg in ('', '.'):
            continue
        out.append(seg)
    return '/'.join(out)


class _Tree:
    """Mappenboom van een resource, opgebouwd uit de lijst met relatieve bestandspaden."""

    def __init__(self, rel_files):
        self.entries = {'': {}}
        for f in rel_files:
            parts = f.split('/')
            for i in range(len(parts)):
                parent = '/'.join(parts[:i])
                name = parts[i]
                is_dir = i < len(parts) - 1
                self.entries.setdefault(parent, {})
                if name not in self.entries[parent] or is_dir:
                    self.entries[parent][name] = is_dir
                if is_dir:
                    self.entries.setdefault('/'.join(parts[:i + 1]), {})

    def match(self, pattern, ignore_case):
        # Match(device, pattern): map = alles tot de laatste '/', naam = de rest
        slash = pattern.rfind('/')
        root = pattern[:slash] if slash != -1 else ''
        after = pattern[slash + 1:] if slash != -1 else pattern
        rx = _fivem_name_regex(after, ignore_case)
        for name, is_dir in sorted(self.entries.get(_norm(root), {}).items(), key=lambda kv: kv[0].lower()):
            if rx.match(name):
                yield name, is_dir


def _get_directory(path):
    i = path.rfind('/')
    return path[:i] if i != -1 else '.'


def _match_files(tree, pattern, out, ignore_case, depth=0):
    """Port van MatchFiles (ResourceMetaDataComponent.cpp, master 20 okt 2026), inclusief
    het afwijkende gedrag: een enkele '*' in een mapnaam vindt niets, omdat de code het
    teken vóór de '/' weglaat; '?' werkt alleen in de bestandsnaam; '**' werkt."""
    if depth > 64:
        return
    pn = pattern
    star = pn.find('*')
    before = _get_directory(pn[:star] if star != -1 else pn)
    slash = pn.find('/', star) if star != -1 else -1
    after = pn[slash + 1:] if slash != -1 else ''
    recurse = star != -1 and pn[star + 1:star + 2] == '*' and (star == 0 or pn[star - 1] == '/')
    if recurse:
        for off in (1, 2):
            sub = pn[:star] + pn[star + off:]
            _match_files(tree, sub.replace('//', '/'), out, ignore_case, depth + 1)
        for name, is_dir in tree.match(pn[:star + 1], ignore_case):
            if is_dir:
                _match_files(tree, before + '/' + name + '/' + pn[star:], out, ignore_case, depth + 1)
    else:
        find_pattern = pn[:slash - 1] if slash != -1 else pn
        for name, is_dir in tree.match(find_pattern, ignore_case):
            if not (slash != -1 and not is_dir):
                match_path = (before + '/' + name) if before not in ('.', '') else name
                if after:
                    _match_files(tree, match_path + '/' + after, out, ignore_case, depth + 1)
                elif not is_dir:
                    out.add(match_path)


def glob_match(pattern, rel_files, ignore_case=False, _cache={}):
    """Welke bestanden FiveM bij dit patroon vindt (paden relatief aan de resource)."""
    key = id(rel_files)
    tree = _cache.get(key)
    if tree is None or tree[0] is not rel_files:
        tree = (rel_files, _Tree(rel_files))
        _cache.clear()
        _cache[key] = tree
    pat = pattern.replace('\\', '/')
    while pat.startswith('./'):
        pat = pat[2:]
    out = set()
    _match_files(tree[1], pat, out, ignore_case)
    return sorted(out)


# ---------------------------------------------------------------- meta (XML)

def load_xml(path):
    raw = open(path, 'rb').read()
    notes = []
    if raw.startswith(b'\xef\xbb\xbf'):
        notes.append('bom_utf8')
    if raw.startswith(b'\xff\xfe') or raw.startswith(b'\xfe\xff'):
        notes.append('utf16')
        raw = raw.decode('utf-16').encode('utf-8')
        raw = re.sub(rb'encoding="[^"]*"', b'encoding="utf-8"', raw, count=1)
    try:
        return ET.fromstring(raw), None, notes
    except ET.ParseError as exc:
        err = str(exc)
    # mild herstel om toch gegevens te lezen; de fout blijft gemeld
    text = raw.decode('utf-8', errors='replace').lstrip('﻿').lstrip()
    text = re.sub(r'^<\?xml[^>]*\?>', '', text).strip()
    text = re.sub(r'&(?!(?:amp|lt|gt|quot|apos|#\d+|#x[0-9a-fA-F]+);)', '&amp;', text)
    try:
        root = ET.fromstring(text.encode('utf-8'))
        notes.append('lenient')
        return root, err, notes
    except ET.ParseError as exc2:
        # meerdere roots? wikkel ze in
        try:
            root = ET.fromstring(('<__wrap__>' + text + '</__wrap__>').encode('utf-8'))
            notes.append('multi_root')
            return root, err, notes
        except ET.ParseError:
            return None, err + ' | ' + str(exc2), notes


def txt(el, tag):
    c = el.find(tag)
    if c is None:
        return None
    if c.text is not None and c.text.strip():
        return c.text.strip()
    return c.get('value')


def val(el, tag):
    c = el.find(tag)
    if c is None:
        return None
    v = c.get('value')
    if v is None and c.text:
        v = c.text.strip()
    return v


def items(el, path):
    c = el.find(path)
    return list(c.findall('Item')) if c is not None else []


def extract_meta(root):
    tag = root.tag
    out = {'root': tag}
    roots = [root]
    if tag == '__wrap__':
        roots = list(root)
        out['root'] = '+'.join(r.tag for r in roots)
    for r in roots:
        t = r.tag
        if t == 'CVehicleModelInfo__InitDataList':
            vehs = out.setdefault('vehicles', [])
            for it in items(r, 'InitDatas'):
                vehs.append({
                    'modelName': txt(it, 'modelName'), 'txdName': txt(it, 'txdName'),
                    'handlingId': txt(it, 'handlingId'), 'gameName': txt(it, 'gameName'),
                    'vehicleMakeName': txt(it, 'vehicleMakeName'), 'type': txt(it, 'type'),
                    'vehicleClass': txt(it, 'vehicleClass'), 'audioNameHash': txt(it, 'audioNameHash'),
                    'layout': txt(it, 'layout'), 'expressionDictName': txt(it, 'expressionDictName'),
                    'ptfxAssetName': txt(it, 'ptfxAssetName'), 'plateType': txt(it, 'plateType'),
                    'flags': (txt(it, 'flags') or ''),
                })
            out.setdefault('txdRelationships', []).extend(
                [[txt(i, 'parent'), txt(i, 'child')] for i in items(r, 'txdRelationships')])
            res = txt(r, 'residentTxd')
            if res:
                out['residentTxd'] = res
        elif t == 'CHandlingDataMgr':
            hs = out.setdefault('handling', [])
            for it in items(r, 'HandlingData'):
                fields = {}
                for ch in it:
                    if ch.tag in ('handlingName', 'SubHandlingData'):
                        continue
                    if ch.get('value') is not None:
                        fields[ch.tag] = ch.get('value')
                    elif ch.get('x') is not None:
                        fields[ch.tag] = [ch.get('x'), ch.get('y'), ch.get('z')]
                    elif ch.text and ch.text.strip():
                        fields[ch.tag] = ch.text.strip()
                subs = [s.get('type') for s in items(it, 'SubHandlingData') if s.get('type')]
                hs.append({'handlingName': txt(it, 'handlingName'), 'type': it.get('type'),
                           'sub': subs, 'f': fields})
        elif t == 'CVehicleModelInfoVariation':
            vs = out.setdefault('variations', [])
            for it in items(r, 'variationData'):
                kits = [k.text.strip() for k in items(it, 'kits') if k.text and k.text.strip()]
                vs.append({'modelName': txt(it, 'modelName'), 'kits': kits,
                           'colors': len(items(it, 'colors')),
                           'liveries': len(items(it, 'liveries')),
                           'lightSettings': val(it, 'lightSettings'),
                           'sirenSettings': val(it, 'sirenSettings')})
        elif t == 'CVehicleModelInfoVarGlobal':
            cc = out.setdefault('carcols', {'kits': [], 'lights': [], 'sirens': [], 'wheels': 0})
            for it in items(r, 'Kits'):
                mods = items(it, 'visibleMods')
                types = {}
                models = []
                for m in mods:
                    mt = txt(m, 'type') or '?'
                    types[mt] = types.get(mt, 0) + 1
                    mn = txt(m, 'modelName')
                    if mn:
                        models.append(mn)
                cc['kits'].append({'kitName': txt(it, 'kitName'), 'id': val(it, 'id'),
                                   'kitType': txt(it, 'kitType'), 'mods': len(mods),
                                   'modTypes': types, 'modModels': models,
                                   'statMods': len(items(it, 'statMods'))})
            cc['lights'].extend([val(i, 'id') for i in items(r, 'Lights')])
            cc['sirens'].extend([[val(i, 'id'), txt(i, 'name')] for i in items(r, 'Sirens')])
            w = r.find('Wheels')
            if w is not None:
                cc['wheels'] += len(list(w.iter('Item')))
        elif t == 'CVehicleMetadataMgr':
            out['layouts'] = {ch.tag: len(list(ch)) for ch in r}
        elif t == 'CExtraTextMetaFile':
            out['dlctext'] = True
        elif t == 'ShopVehicleDataArray':
            out['shop'] = len(list(r.iter('Item')))
        elif t == 'SContentUnlocks':
            out['unlocks'] = len(list(r.iter('Item')))
        elif t == 'CPtfxAssetInfoMgr':
            out['ptfx'] = True
    return out


# ---------------------------------------------------------------- lua

TEXT_ENTRY_RE = re.compile(r'''AddTextEntry(?:ByHash)?\s*\(\s*(?:'([^']*)'|"([^"]*)"|(`[^`]*`|0x[0-9A-Fa-f]+|[\w.]+))\s*,\s*(?:'([^']*)'|"([^"]*)")''')


def lua_info(path):
    try:
        text = open(path, 'rb').read().decode('utf-8', errors='replace')
    except OSError:
        return {}
    entries = []
    for m in TEXT_ENTRY_RE.finditer(text):
        key = m.group(1) or m.group(2) or m.group(3)
        label = m.group(4) if m.group(4) is not None else m.group(5)
        entries.append([key, label])
    http = bool(re.search(r'PerformHttpRequest|http[s]?://', text))
    return {'text_entries': entries, 'http': http, 'lines': text.count('\n') + 1}


def nametable_names(path):
    try:
        raw = open(path, 'rb').read()
    except OSError:
        return []
    return [p.decode('latin-1') for p in raw.split(b'\x00') if p]


# ---------------------------------------------------------------- units

def walk_files(root):
    files = []
    dirs = []
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d != '.git']
        rel_dp = os.path.relpath(dp, root).replace('\\', '/')
        rel_dp = '' if rel_dp == '.' else rel_dp
        dirs.append(rel_dp)
        for f in fn:
            files.append((rel_dp + '/' + f) if rel_dp else f)
    return files, dirs


def scan_units(scan_root, out_path):
    t0 = time.time()
    files, dirs = walk_files(scan_root)
    t_walk = time.time() - t0
    fileset = set(files)
    unit_dirs = sorted({os.path.dirname(f) for f in files if os.path.basename(f) in MANIFESTS},
                       key=lambda d: (d.count('/'), d))

    def owner(rel):
        best = None
        for u in unit_dirs:
            if u == '' or rel == u or rel.startswith(u + '/'):
                if best is None or len(u) > len(best):
                    best = u
        return best

    units = {u: {'path': u, 'files': []} for u in unit_dirs}
    loose = []
    for f in files:
        o = owner(f)
        if o is None:
            loose.append(f)
        else:
            units[o]['files'].append(f[len(o) + 1:] if o else f)

    big = []
    for u in unit_dirs:
        unit = units[u]
        ufiles = unit['files']
        base = os.path.join(scan_root, u) if u else scan_root
        manifest_name = 'fxmanifest.lua' if 'fxmanifest.lua' in ufiles else '__resource.lua'
        unit['manifest'] = manifest_name
        unit['both_manifests'] = 'fxmanifest.lua' in ufiles and '__resource.lua' in ufiles
        try:
            unit['manifest_info'] = parse_manifest(os.path.join(base, manifest_name))
        except Exception as exc:  # noqa
            unit['manifest_info'] = {'error': str(exc)}
        mi = unit['manifest_info']

        # bestanden per soort
        sizes = {}
        by_ext = {}
        rsc = {}
        stream = []
        for f in ufiles:
            full = os.path.join(base, f)
            try:
                st = os.stat(full)
                size = st.st_size
            except OSError:
                size = -1
            sizes[f] = size
            ext = os.path.splitext(f)[1].lower()
            by_ext.setdefault(ext, [0, 0])
            by_ext[ext][0] += 1
            by_ext[ext][1] += max(size, 0)
            if ext in RSC_EXT or ext == '.rpf' or os.path.basename(f) == '.fxap':
                rsc[f] = classify_binary(full)
            if f.startswith('stream/'):
                stream.append(f)
        unit['sizes'] = sizes
        unit['by_ext'] = by_ext
        unit['bin'] = rsc
        unit['stream'] = stream

        # data_file-matches (FiveM: hoofdlettergevoelig; ook zonder hoofdletters voor de melding)
        dmatches = []
        for dtype, pat in mi.get('data_files', []):
            exact = glob_match(pat, ufiles)
            icase = glob_match(pat, ufiles, ignore_case=True)
            dmatches.append({'type': dtype, 'pattern': pat, 'matches': exact,
                             'icase_only': sorted(set(icase) - set(exact))})
        unit['data_file_matches'] = dmatches
        fmatches = {}
        for key in ('file', 'files'):
            for pat in mi.get('lists', {}).get(key, []):
                fmatches[pat] = glob_match(pat, ufiles)
        unit['files_matches'] = fmatches
        scripts = {}
        for key in ('client_script', 'client_scripts', 'server_script', 'server_scripts',
                    'shared_script', 'shared_scripts'):
            for pat in mi.get('lists', {}).get(key, []):
                if pat.startswith('@'):
                    scripts[pat] = ['@external']
                else:
                    scripts[pat] = glob_match(pat, ufiles)
        unit['script_matches'] = scripts

        # meta's en xml
        metas = {}
        for f in ufiles:
            ext = os.path.splitext(f)[1].lower()
            if ext in ('.meta', '.xml') and not f.startswith('stream/'):
                try:
                    root, err, notes = load_xml(os.path.join(base, f))
                except OSError as exc:
                    metas[f] = {'error': str(exc)}
                    continue
                entry = {'error': err, 'notes': notes}
                if root is not None:
                    try:
                        entry.update(extract_meta(root))
                    except Exception as exc:  # noqa
                        entry['extract_error'] = str(exc)
                metas[f] = entry
        unit['metas'] = metas

        # lua
        luas = {}
        for f in ufiles:
            if f.lower().endswith('.lua') and os.path.basename(f) not in MANIFESTS:
                luas[f] = lua_info(os.path.join(base, f))
        unit['lua'] = luas

        # audio nametables
        names = {}
        for f in ufiles:
            if f.lower().endswith('.nametable'):
                names[f] = nametable_names(os.path.join(base, f))
        unit['nametables'] = names

        for f, info in rsc.items():
            if info.get('k') in ('rsc7', 'rsc8') and max(info['vm'], info['pm']) > 16 * 1024 * 1024:
                big.append([u, f, info['vm'], info['pm']])

    loose_info = {}
    for f in loose:
        full = os.path.join(scan_root, f)
        try:
            size = os.stat(full).st_size
        except OSError:
            size = -1
        ext = os.path.splitext(f)[1].lower()
        entry = {'size': size}
        if ext in RSC_EXT or ext == '.rpf':
            entry['bin'] = classify_binary(full)
        loose_info[f] = entry

    out = {'scan_root': scan_root, 'scanned_at': time.strftime('%Y-%m-%d %H:%M:%S'),
           'seconds_walk': round(t_walk, 1), 'seconds_total': round(time.time() - t0, 1),
           'n_files': len(files), 'n_dirs': len(dirs), 'dirs': dirs,
           'units': [units[u] for u in unit_dirs], 'loose': loose_info, 'over16': big}
    with open(out_path, 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, separators=(',', ':'))
    print('ok', scan_root, 'files', len(files), 'units', len(unit_dirs), 'loose', len(loose),
          'walk', round(t_walk, 1), 's total', round(time.time() - t0, 1), 's')


def main(argv):
    if len(argv) != 4 or argv[1] not in ('fivem-view', 'units'):
        print(__doc__)
        return 2
    if argv[1] == 'fivem-view':
        res = fivem_view(argv[2])
        with open(argv[3], 'w', encoding='utf-8') as fh:
            json.dump(res, fh, ensure_ascii=False, indent=1)
        print('ok fivem-view', len(res['resources']), 'resources', len(res['warnings']), 'warnings')
        return 0
    scan_units(argv[2], argv[3])
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
