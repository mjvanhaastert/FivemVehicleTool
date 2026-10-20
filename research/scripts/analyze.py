#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Analyse van de scan-JSON's van scan_vehicles.py: bevindingen per soort.

Gebruik:
  python3 -I analyze.py <map met units_*.json en fivem_view.json> <findings.json> [vehicles.json]

<vehicles.json> is de vanilla-lijst uit de kennisbasis (mjvanhaastert/Fivem, data/vehicles.json).
Zonder die lijst worden de vanilla-controles (override, vanilla-handling, labels) overgeslagen.
"""
import json
import glob
import os
import re
import sys
from collections import defaultdict, Counter

DATA = sys.argv[1] if len(sys.argv) > 1 else 'data'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'findings.json'
VANILLA = sys.argv[3] if len(sys.argv) > 3 else None

MiB = 1024 * 1024
VALID_CLASSES = set('''VC_COMPACT VC_SEDAN VC_SUV VC_COUPE VC_MUSCLE VC_SPORT_CLASSIC VC_SPORT VC_SUPER
VC_MOTORCYCLE VC_OFF_ROAD VC_INDUSTRIAL VC_UTILITY VC_VAN VC_CYCLE VC_BOAT VC_HELICOPTER VC_PLANE
VC_SERVICE VC_EMERGENCY VC_MILITARY VC_COMMERCIAL VC_RAIL VC_OPEN_WHEEL'''.split())
OFFICIAL_TYPES = set("""ACTION_TABLE_DEFINITIONS ALTERNATE_VARIATIONS_FILE AMB_PROCEDURAL_BLOOD_FILE
AMBIENT_PED_MODEL_SET_FILE AMBIENT_PROP_MODEL_SET_FILE AMBIENT_VEHICLE_MODEL_SET_FILE
AUDIO_CURVEDATA AUDIO_DYNAMIXDATA AUDIO_GAMEDATA AUDIO_SOUNDDATA AUDIO_SPEECHDATA
AUDIO_SYNTHDATA AUDIO_WAVEPACK CARCOLS_FILE CLIP_SETS_FILE
COMBAT_BEHAVIOUR_OVERRIDE_FILE CONDITIONAL_ANIMS_FILE CONTENT_UNLOCKING_META_FILE
DLC_ITYP_REQUEST DLC_POP_GROUPS DLC_SCRIPT_METAFILE DLC_WEAPON_PICKUPS
DRIVER_RULES_STD_FILE EVENTS_OVERRIDE_FILE EXPLOSION_INFO_FILE EXPLOSIONFX_FILE
EXPRESSION_SETS_FILE EXTRA_FOLDER_MOUNT_DATA EXTRA_TITLE_UPDATE_DATA
FACIAL_CLIPSET_GROUPS_FILE GTXD_PARENTING_DATA HANDLING_FILE
INTERIOR_PROXY_ORDER_FILE LEVEL_STREAMING_FILE LOADOUTS_FILE MOVE_NETWORK_DEFS
MP_STATS_DISPLAY_LIST_FILE MP_STATS_UI_LIST_FILE NM_TUNING_FILE OVERLAY_INFO_FILE
PED_BOUNDS_FILE PED_BRAWLING_STYLE_FILE PED_COMPONENT_SETS_FILE
PED_DAMAGE_APPEND_FILE PED_DAMAGE_OVERRIDE_FILE PED_FIRST_PERSON_ALTERNATE_DATA
PED_FIRST_PERSON_ASSET_DATA PED_METADATA_FILE PED_OVERLAY_FILE
PED_PERCEPTION_FILE PED_PERSONALITY_FILE PED_TASK_DATA_FILE PEDSTREAM_FILE
POPSCHED_FILE PTFXASSETINFO_FILE SCALEFORM_DLC_FILE SCALEFORM_PREALLOC_FILE
SCENARIO_INFO_FILE SCENARIO_POINTS_FILE SCENARIO_POINTS_OVERRIDE_FILE
SCENARIO_POINTS_PSO_FILE SCENARIO_POINTS_OVERRIDE_PSO_FILE SCRIPT_BRAIN_FILE
SCRIPTFX_FILE SHOP_PED_APPAREL_META_FILE SP_STATS_DISPLAY_LIST_FILE
SP_STATS_UI_LIST_FILE STREAMING_REQUEST_LISTS_FILE TATTOO_SHOP_DLC_FILE
TEXTFILE_METAFILE TIMECYCLEMOD_FILE TRAINCONFIGS_FILE TRAINTRACK_FILE
VEHICLE_LAYOUTS_FILE VEHICLE_METADATA_FILE VEHICLE_SHOP_DLC_FILE
VEHICLE_VARIATION_FILE VEHICLEEXTRAS_FILE VFXVEHICLEINFO_FILE
WEAPON_ANIMATIONS_FILE WEAPON_METADATA_FILE WEAPON_SHOP_INFO_METADATA_FILE
WEAPONCOMPONENTSINFO_FILE WEAPONINFO_FILE_PATCH WEAPONINFO_FILE ZONEBIND_FILE""".split())

# root-element dat bij elk data_file-type hoort
TYPE_ROOT = {
    'HANDLING_FILE': 'CHandlingDataMgr',
    'VEHICLE_METADATA_FILE': 'CVehicleModelInfo__InitDataList',
    'CARCOLS_FILE': 'CVehicleModelInfoVarGlobal',
    'VEHICLE_VARIATION_FILE': 'CVehicleModelInfoVariation',
    'VEHICLE_LAYOUTS_FILE': 'CVehicleMetadataMgr',
    'VEHICLE_SHOP_DLC_FILE': 'ShopVehicleDataArray',
    'CONTENT_UNLOCKING_META_FILE': 'SContentUnlocks',
    'DLCTEXT_FILE': 'CExtraTextMetaFile',
    'PTFXASSETINFO_FILE': 'CPtfxAssetInfoMgr',
}



def joaat(s):
    h = 0
    for ch in s.lower().encode('utf-8'):
        h = (h + ch) & 0xFFFFFFFF
        h = (h + (h << 10)) & 0xFFFFFFFF
        h ^= (h >> 6)
    h = (h + (h << 3)) & 0xFFFFFFFF
    h ^= (h >> 11)
    h = (h + (h << 15)) & 0xFFFFFFFF
    return h


def load():
    packs = {}
    for f in sorted(glob.glob(os.path.join(DATA, 'units_*.json'))):
        d = json.load(open(f, encoding='utf-8'))
        # naam van het pack = laatste deel van het gescande pad
        packs[os.path.basename(os.path.normpath(d['scan_root']))] = d
    view_path = os.path.join(DATA, 'fivem_view.json')
    view = json.load(open(view_path, encoding='utf-8')) if os.path.exists(view_path) else {'resources': [], 'warnings': []}
    vanilla = json.load(open(VANILLA, encoding='utf-8'))['items'] if VANILLA else []
    return packs, view, vanilla


def main():
    packs, view, vanilla = load()
    vanilla_models = {v['model'].lower() for v in vanilla}
    vanilla_names = {(v.get('name') or '').lower() for v in vanilla}
    loaded = {r['path'] for r in view['resources'] if r['manifest']}

    F = defaultdict(list)          # categorie -> lijst bevindingen
    S = {}                         # samenvattingen
    all_units = []
    for pack, d in packs.items():
        for u in d['units']:
            uid = pack + ('/' + u['path'] if u['path'] else '')
            all_units.append((pack, uid, u))
        for f, info in d['loose'].items():
            b = info.get('bin') or {}
            if b.get('k') == 'rpf7':
                F['rpf'].append({'unit': pack, 'file': f, 'size': info['size'], 'enc': b.get('enc')})

    # ------------------------------------------------ laden door FiveM
    for pack, uid, u in all_units:
        # pad zoals de FiveM-scan het ziet, relatief aan resources/
        root = view.get('root')
        base = os.path.relpath(packs[pack]['scan_root'], root).replace('\\', '/') if root else pack
        rel = base + ('/' + u['path'] if u['path'] else '')
        u['_loads'] = rel in loaded
        if not u['_loads']:
            F['not_loaded'].append({'unit': uid})
        if u['manifest'] == '__resource.lua':
            F['outdated_manifest'].append({'unit': uid})
        if u.get('both_manifests'):
            F['both_manifests'].append({'unit': uid})
    for w in view['warnings']:
        if w['type'] == 'no_manifest' and any(
                w['path'] == os.path.relpath(d['scan_root'], view.get('root') or '').replace('\\', '/') for d in packs.values()):
            F['no_manifest'].append(w)

    # ------------------------------------------------ manifest
    vanilla_audio = vanilla_models
    custom_audio = defaultdict(set)   # naam -> units
    for pack, uid, u in all_units:
        mi = u['manifest_info']
        if mi.get('games'):
            if 'rdr3' in mi['games']:
                F['games_rdr3'].append({'unit': uid, 'games': mi['games']})
        file_patterns = mi.get('lists', {}).get('files', []) + mi.get('lists', {}).get('file', [])
        files_covered = set()
        for pat, matches in u['files_matches'].items():
            files_covered.update(matches)
        per_file_types = defaultdict(set)
        for m in u['data_file_matches']:
            t = m['type']
            if t not in OFFICIAL_TYPES:
                F['unknown_data_file_type'].append({'unit': uid, 'type': t, 'pattern': m['pattern'], 'matches': len(m['matches'])})
            if not m['matches']:
                rel_suffix = {'AUDIO_GAMEDATA': '151.rel', 'AUDIO_SOUNDDATA': '54.rel', 'AUDIO_SYNTHDATA': '10.rel'}.get(t)
                if rel_suffix:
                    if (m['pattern'] + rel_suffix) not in u['files']:
                        F['audio_rel_missing'].append({'unit': uid, 'type': t, 'pattern': m['pattern'],
                                                       'expected': m['pattern'] + rel_suffix})
                elif t == 'AUDIO_WAVEPACK':
                    pass  # map; zie wavepack_missing
                elif '*' in m['pattern']:
                    F['data_file_glob_empty'].append({'unit': uid, 'type': t, 'pattern': m['pattern']})
                else:
                    F['data_file_missing'].append({'unit': uid, 'type': t, 'pattern': m['pattern'],
                                                   'icase_only': m['icase_only'][:5]})
            elif m['icase_only']:
                F['data_file_case'].append({'unit': uid, 'type': t, 'pattern': m['pattern'], 'icase_only': m['icase_only'][:5]})
            for f in m['matches']:
                per_file_types[f].add(t)
                if not f.startswith('stream/') and f not in files_covered and not t.startswith('AUDIO_WAVEPACK'):
                    F['data_file_not_in_files'].append({'unit': uid, 'type': t, 'file': f})
            if t.startswith('AUDIO_GAMEDATA'):
                for f in m['matches']:
                    pass
        multi = {f: sorted(ts) for f, ts in per_file_types.items() if len(ts) > 1}
        if multi:
            F['file_multi_types'].append({'unit': uid, 'files': len(multi), 'example': next(iter(multi.items()))})
        # wavepacks: data_file AUDIO_WAVEPACK wijst naar map
        for dt, pat in mi.get('data_files', []):
            if dt == 'AUDIO_WAVEPACK':
                prefix = pat.rstrip('/') + '/'
                if not any(f.startswith(prefix) for f in u['files']):
                    F['wavepack_missing'].append({'unit': uid, 'pattern': pat})
                else:
                    name = pat.rstrip('/').split('/')[-1]
                    if name.lower().startswith('dlc_'):
                        custom_audio[name[4:].lower()].add(uid)
            if dt in ('AUDIO_GAMEDATA',):
                base = pat.split('/')[-1]
                custom_audio[re.sub(r'_game\.dat$', '', base.lower())].add(uid)
        for nt, names in u['nametables'].items():
            for n in names:
                custom_audio[n.lower()].add(uid)
        for pat, matches in u['script_matches'].items():
            if not matches:
                F['missing_script'].append({'unit': uid, 'script': pat})
        for f, info in u['lua'].items():
            if info.get('http'):
                F['lua_http'].append({'unit': uid, 'file': f})

    # ------------------------------------------------ meta's
    vehicles = []      # (uid, meta, veh)
    handling = defaultdict(list)   # name.lower -> [(uid, meta)]
    variations = []
    kits = []
    lights = []
    sirens = []
    meta_roots = Counter()
    text_entries = defaultdict(set)
    for pack, uid, u in all_units:
        types_for_file = defaultdict(set)
        for m in u['data_file_matches']:
            for f in m['matches']:
                types_for_file[f].add(m['type'])
        for f, info in u['lua'].items():
            for k, lab in info.get('text_entries', []):
                k = (k or '').lower().strip('`')
                if k.startswith('0x'):
                    try:
                        k = '0x%08x' % (int(k, 16) & 0xFFFFFFFF)
                    except ValueError:
                        pass
                text_entries[uid].add(k)
        for f, m in u['metas'].items():
            if m.get('error'):
                F['meta_parse_error'].append({'unit': uid, 'file': f, 'error': m['error'][:160],
                                              'recovered': m.get('root') is not None, 'notes': m.get('notes')})
            elif m.get('notes'):
                F['meta_notes'].append({'unit': uid, 'file': f, 'notes': m['notes']})
            root = m.get('root')
            meta_roots[root] += 1
            for t in types_for_file.get(f, ()):
                exp = TYPE_ROOT.get(t)
                if exp and root and exp not in root.split('+'):
                    F['meta_root_mismatch'].append({'unit': uid, 'file': f, 'type': t, 'root': root})
            if not types_for_file.get(f) and f.lower().endswith('.meta'):
                F['meta_not_loaded'].append({'unit': uid, 'file': f, 'root': root})
            for v in m.get('vehicles', []):
                vehicles.append((uid, f, v))
            for h in m.get('handling', []):
                handling[(h.get('handlingName') or '').lower()].append((uid, f, h))
            for v in m.get('variations', []):
                variations.append((uid, f, v))
            cc = m.get('carcols')
            if cc:
                for k in cc['kits']:
                    kits.append((uid, f, k))
                for l in cc['lights']:
                    lights.append((uid, f, l))
                for s in cc['sirens']:
                    sirens.append((uid, f, s))

    # ------------------------------------------------ koppelingen per unit
    by_unit_stream = {}
    for pack, uid, u in all_units:
        names = Counter(os.path.basename(f).lower() for f in u['stream'])
        by_unit_stream[uid] = names
        dupes = [n for n, c in names.items() if c > 1]
        if dupes:
            F['stream_dupe_in_unit'].append({'unit': uid, 'count': len(dupes), 'examples': dupes[:6]})
    unit_handling = defaultdict(set)
    for name, lst in handling.items():
        for uid, f, h in lst:
            unit_handling[uid].add(name)
    unit_vars = defaultdict(set)
    for uid, f, v in variations:
        unit_vars[uid].add((v.get('modelName') or '').lower())
    unit_kits = defaultdict(set)
    for uid, f, k in kits:
        unit_kits[uid].add((k.get('kitName') or '').lower())
    unit_vehicles = defaultdict(set)
    for uid, f, v in vehicles:
        unit_vehicles[uid].add((v.get('modelName') or '').lower())

    model_units = defaultdict(set)
    for uid, f, v in vehicles:
        model = (v.get('modelName') or '').lower()
        model_units[model].add(uid)
        s = by_unit_stream.get(uid, Counter())
        if model + '.yft' not in s:
            F['model_without_yft'].append({'unit': uid, 'model': model, 'meta': f})
        txd = (v.get('txdName') or '').lower()
        if txd and txd + '.ytd' not in s:
            F['txd_without_ytd'].append({'unit': uid, 'model': model, 'txd': txd})
        hid = (v.get('handlingId') or '').lower()
        if hid and hid not in unit_handling[uid]:
            if hid in vanilla_models:
                F['handling_vanilla'].append({'unit': uid, 'model': model, 'handlingId': hid})
            else:
                F['handling_missing'].append({'unit': uid, 'model': model, 'handlingId': hid})
        if model not in unit_vars[uid]:
            F['no_carvariation'].append({'unit': uid, 'model': model})
        if model in vanilla_models:
            F['vanilla_model_override'].append({'unit': uid, 'model': model})
        gn = (v.get('gameName') or '').lower()
        te = text_entries.get(uid, set())
        if gn and gn not in te and ('0x%08x' % joaat(gn)) not in te and gn not in vanilla_names:
            F['gamename_without_text'].append({'unit': uid, 'model': model, 'gameName': gn})
        vc = v.get('vehicleClass') or ''
        if vc and vc not in VALID_CLASSES:
            F['vehicleclass_invalid'].append({'unit': uid, 'model': model, 'vehicleClass': vc})
        audio = (v.get('audioNameHash') or '').lower()
        if audio and audio not in vanilla_audio and audio not in custom_audio:
            F['audio_unknown'].append({'unit': uid, 'model': model, 'audioNameHash': audio})
    per_unit_models = Counter((uid, (v.get('modelName') or '').lower()) for uid, f, v in vehicles)
    for (uid, model), c in per_unit_models.items():
        if c > 1:
            F['model_dupe_in_unit'].append({'unit': uid, 'model': model, 'count': c,
                                            'metas': sorted({f for u2, f, v in vehicles if u2 == uid and (v.get('modelName') or '').lower() == model})})
    for model, us in model_units.items():
        if len(us) > 1:
            F['model_in_multiple_units'].append({'model': model, 'units': sorted(us)})
    for uid, f, v in variations:
        model = (v.get('modelName') or '').lower()
        if model not in unit_vehicles[uid]:
            F['variation_without_vehicle'].append({'unit': uid, 'model': model})
        for kn in v.get('kits', []):
            if kn.lower() not in unit_kits[uid] and kn.lower() not in ('0_default_modkit',):
                F['kit_not_defined'].append({'unit': uid, 'model': model, 'kit': kn})
    # handling dubbel tussen units
    for name, lst in handling.items():
        us = {uid for uid, f, h in lst}
        if len(us) > 1:
            F['handling_in_multiple_units'].append({'handlingName': name, 'units': sorted(us)})
        per_unit = Counter(uid for uid, f, h in lst)
        for uid, c in per_unit.items():
            if c > 1:
                F['handling_dupe_in_unit'].append({'unit': uid, 'handlingName': name, 'count': c})
    # kit-id's
    kit_ids = defaultdict(set)
    for uid, f, k in kits:
        kit_ids[k.get('id')].add((uid, k.get('kitName')))
    for kid, owners in kit_ids.items():
        us = {o[0] for o in owners}
        if len(owners) > 1:
            F['kit_id_collision'].append({'id': kid, 'owners': sorted(owners)[:8], 'n': len(owners), 'cross_unit': len(us) > 1})
    S['kit_ids'] = sorted([k for k in kit_ids if k is not None], key=lambda x: int(x) if str(x).lstrip('-').isdigit() else 0)
    for name, items_ in (('light_id_collision', lights), ('siren_id_collision', sirens)):
        ids = defaultdict(set)
        for uid, f, l in items_:
            key = l[0] if isinstance(l, list) else l
            ids[key].add(uid)
        for key, us in ids.items():
            if len([1 for uid, f, l in items_ if (l[0] if isinstance(l, list) else l) == key]) > 1:
                F[name].append({'id': key, 'units': sorted(us), 'n': len([1 for uid, f, l in items_ if (l[0] if isinstance(l, list) else l) == key])})

    # stream-naam botsingen tussen units
    stream_owner = defaultdict(set)
    for uid, names in by_unit_stream.items():
        for n in names:
            stream_owner[n].add(uid)
    cross = {n: sorted(us) for n, us in stream_owner.items() if len(us) > 1}
    S['stream_cross_collisions'] = len(cross)
    pairs = Counter()
    for n, us in cross.items():
        pairs[' + '.join(us)] += 1
    S['stream_cross_pairs'] = pairs.most_common(20)
    S['stream_cross_examples'] = list(cross.items())[:30]
    # vanilla-namen in stream (.yft/.ytd die vanilla vervangen)
    for uid, names in by_unit_stream.items():
        rep = sorted(n for n in names if os.path.splitext(n)[0].replace('_hi', '').replace('+hi', '') in vanilla_models)
        if rep:
            F['stream_replaces_vanilla'].append({'unit': uid, 'count': len(rep), 'examples': rep[:8]})

    # ------------------------------------------------ binaire bestanden
    thresholds = [16, 32, 48, 64]
    size_rows = []
    for pack, uid, u in all_units:
        for f, b in u['bin'].items():
            k = b.get('k')
            if k == 'fxap':
                F['escrow'].append({'unit': uid, 'file': f})
            elif k == 'rpf7':
                F['rpf'].append({'unit': uid, 'file': f, 'enc': b.get('enc')})
            elif k in ('rsc7', 'rsc8'):
                size_rows.append((uid, f, b['v'], b['vm'], b['pm'], u['sizes'].get(f, -1)))
            elif k in ('other', 'err', 'xml'):
                if f.lower().endswith('.ymf') and b.get('m') == '5053494e':
                    continue  # PSO-bestand (PSIN), geen RSC; normaal voor _manifest.ymf
                F['bin_not_rsc'].append({'unit': uid, 'file': f, 'kind': k, 'magic': b.get('m')})
        # rare tekens in paden
        for f in u['files']:
            base = os.path.basename(f)
            if re.search(r"[^\x20-\x7e]", f):
                F['path_non_ascii'].append({'unit': uid, 'file': f})
            if f.startswith('stream/') and (base != base.lower()):
                F['stream_uppercase'].append({'unit': uid, 'file': f})
            if f.startswith('stream/') and len(base) >= 64:
                F['stream_long_name'].append({'unit': uid, 'file': f, 'len': len(base)})
        odd_dirs = sorted({os.path.dirname(f) for f in u['files'] if re.search(r"[ '&()!,]", os.path.dirname(f))})
        if odd_dirs:
            F['path_odd_chars'].append({'unit': uid, 'dirs': len(odd_dirs), 'examples': odd_dirs[:4]})
        exts = Counter(os.path.splitext(f)[1].lower() for f in u['files'])
        exe = {e: c for e, c in exts.items() if e in ('.dll', '.exe', '.bat', '.cmd', '.ps1', '.zip', '.rar', '.7z', '.oiv', '.asi')}
        if exe:
            F['odd_file_types'].append({'unit': uid, 'types': exe})
        ystream_outside = [f for f in u['files'] if os.path.splitext(f)[1].lower() in ('.yft', '.ytd', '.ydr', '.ydd') and not f.startswith('stream/')]
        if ystream_outside:
            F['asset_outside_stream'].append({'unit': uid, 'count': len(ystream_outside), 'examples': ystream_outside[:4]})

    over = {t: [r for r in size_rows if max(r[3], r[4]) > t * MiB] for t in thresholds}
    S['rsc_total'] = len(size_rows)
    S['over'] = {t: len(v) for t, v in over.items()}
    per_unit_over = defaultdict(lambda: Counter())
    for t in thresholds:
        for r in over[t]:
            per_unit_over[r[0]][t] += 1
    S['over_per_unit'] = {u: dict(c) for u, c in per_unit_over.items()}
    by_ext_over = defaultdict(Counter)
    for t in thresholds:
        for r in over[t]:
            by_ext_over[os.path.splitext(r[1])[1].lower()][t] += 1
    S['over_by_ext'] = {e: dict(c) for e, c in by_ext_over.items()}
    phys_or_virt = Counter()
    for r in over[16]:
        if r[4] > 16 * MiB and r[3] > 16 * MiB:
            phys_or_virt['both'] += 1
        elif r[4] > 16 * MiB:
            phys_or_virt['physical'] += 1
        else:
            phys_or_virt['virtual'] += 1
    S['over16_kind'] = dict(phys_or_virt)
    top = sorted(size_rows, key=lambda r: -max(r[3], r[4]))[:25]
    S['top_assets'] = [{'unit': r[0], 'file': r[1], 'virt_mib': round(r[3] / MiB, 1), 'phys_mib': round(r[4] / MiB, 1), 'disk_mb': round(r[5] / 1e6, 1)} for r in top]
    # verhouding geheugen/schijf voor ytd
    ratios = []
    for r in size_rows:
        if r[1].lower().endswith('.ytd') and r[5] > 0:
            ratios.append((r[4] / max(r[5], 1), r))
    ratios.sort(key=lambda x: -x[0])
    S['ytd_ratio_top'] = [{'unit': r[0], 'file': r[1], 'ratio': round(x, 1), 'phys_mib': round(r[4] / MiB, 1), 'disk_mb': round(r[5] / 1e6, 2)} for x, r in ratios[:10]]

    # ------------------------------------------------ liveries
    liv = Counter()
    liv_examples = defaultdict(list)
    for uid, f, v in variations:
        if v.get('liveries'):
            liv['carvariations_liveries'] += 1
            liv_examples['carvariations_liveries'].append((uid, v.get('modelName'), v['liveries']))
    for uid, f, k in kits:
        n = k.get('modTypes', {}).get('VMT_LIVERY_MOD', 0)
        if n:
            liv['modkit_livery'] += 1
            liv_examples['modkit_livery'].append((uid, k.get('kitName'), n))
    S['liveries'] = dict(liv)
    S['liveries_examples'] = {k: v[:8] for k, v in liv_examples.items()}
    # livery-varianten als losse modellen: modelnamen die op een cijfer eindigen met dezelfde stam
    stems = defaultdict(list)
    for uid, f, v in vehicles:
        m = (v.get('modelName') or '').lower()
        st = re.sub(r'\d+$', '', m)
        if st != m:
            stems[(uid, st)].append(m)
    S['numbered_model_groups'] = [(k[0], k[1], sorted(v)) for k, v in stems.items() if len(v) > 1][:20]

    # ------------------------------------------------ samenvatting per pack
    pack_rows = []
    for pack, d in packs.items():
        units = [x for x in all_units if x[0] == pack]
        n_veh = sum(1 for uid, f, v in vehicles if uid.split('/')[0] == pack or uid == pack)
        size = sum(sum(max(s, 0) for s in u['sizes'].values()) for _, _, u in units)
        size += sum(max(i.get('size', 0), 0) for i in d['loose'].values())
        pack_rows.append({'pack': pack, 'units': len(units), 'loads': [uid for _, uid, u in units if u.get('_loads')],
                          'vehicles': n_veh, 'files': d['n_files'], 'size_gb': round(size / 1e9, 2),
                          'stream': sum(len(u['stream']) for _, _, u in units)})
    S['packs'] = pack_rows
    S['meta_roots'] = meta_roots.most_common()
    S['vehicle_types'] = Counter(v.get('type') for _, _, v in vehicles).most_common()
    S['vehicle_classes'] = Counter(v.get('vehicleClass') for _, _, v in vehicles).most_common()
    S['n_vehicles'] = len(vehicles)

    # handling-waarden (voor later: wat is "normaal" bij add-ons)
    hv = defaultdict(list)
    for name, lst in handling.items():
        for uid, f, h in lst:
            for k in ('fMass', 'fInitialDriveForce', 'fInitialDriveMaxFlatVel', 'nInitialDriveGears', 'fBrakeForce',
                      'fTractionCurveMax', 'fTractionCurveMin', 'fSuspensionForce', 'fSteeringLock', 'fDriveInertia'):
                x = h['f'].get(k)
                try:
                    hv[k].append(float(x))
                except (TypeError, ValueError):
                    pass
    def pct(a, p):
        a = sorted(a)
        if not a:
            return None
        i = min(len(a) - 1, max(0, int(round(p / 100 * (len(a) - 1)))))
        return a[i]
    S['handling_stats'] = {k: {'n': len(v), 'min': min(v), 'p5': pct(v, 5), 'p50': pct(v, 50), 'p95': pct(v, 95), 'max': max(v)} for k, v in hv.items() if v}

    res = {'summary': S, 'findings': {k: v for k, v in F.items()}}
    with open(OUT, 'w', encoding='utf-8') as fh:
        json.dump(res, fh, ensure_ascii=False, indent=1, default=list)
    # korte tekst
    print('vehicles', S['n_vehicles'])
    for r in pack_rows:
        print('PACK', r)
    print('over', S['over'], 'of', S['rsc_total'], 'kind16', S['over16_kind'])
    print('over_by_ext', S['over_by_ext'])
    print('stream cross collisions', S['stream_cross_collisions'])
    for k in sorted(F):
        print(f'{k:28s} {len(F[k]):5d}  e.g. {json.dumps(F[k][0], ensure_ascii=False)[:230]}')


if __name__ == '__main__':
    main()
