# Audio van voertuigen

Eigen motorgeluid in een voertuig-resource: welke bestanden, hoe het manifest ze laadt, en wat de tool moet controleren.
De labels staan uitgelegd in [README.md](README.md#labels).

---

## Voorbeeld

Uit `research/Custom Engine Sounds` (een werkend geluidspakket), voor één motor:

```lua
files {
    'audioconfig/rb26dett_amp.dat10.rel',
    'audioconfig/rb26dett_game.dat151.rel',
    'audioconfig/rb26dett_sounds.dat54.rel',
    'sfx/dlc_rb26dett/rb26dett.awc',
    'sfx/dlc_rb26dett/rb26dett_npc.awc',
}

data_file 'AUDIO_SYNTHDATA' 'audioconfig/rb26dett_amp.dat'     -- = rb26dett_amp.dat10.rel
data_file 'AUDIO_GAMEDATA'  'audioconfig/rb26dett_game.dat'    -- = rb26dett_game.dat151.rel
data_file 'AUDIO_SOUNDDATA' 'audioconfig/rb26dett_sounds.dat'  -- = rb26dett_sounds.dat54.rel
data_file 'AUDIO_WAVEPACK'  'sfx/dlc_rb26dett'                 -- map met de .awc-bestanden
```

En in `vehicles.meta` van het voertuig dat dit geluid krijgt:

```xml
<audioNameHash>rb26dett</audioNameHash>
```

De bron-resource `batic` (een motor van Marks oude server) heeft dezelfde opbouw zonder `.dat10.rel`. De pack-versie van VehicleTool neemt die set over, maar dat manifest is ongeldige Lua (zie [inventory.md](inventory.md)).

---

## Wat de bestanden zijn

| Bestand | Rol | `data_file` | Status |
|---------|-----|-------------|--------|
| `<naam>_game.dat151.rel` | game-data: het geluidsobject van het voertuig | `AUDIO_GAMEDATA` (pad zonder `151.rel`) | `tested` (gelezen) |
| `<naam>_sounds.dat54.rel` | sound-data | `AUDIO_SOUNDDATA` (pad zonder `54.rel`) | `tested` (gelezen) |
| `<naam>_amp.dat10.rel` | synth/versterker (sommige geluidspakketten) | `AUDIO_SYNTHDATA` (pad zonder `10.rel`) | `tested` (gelezen in het manifest van Custom Engine Sounds) |
| `.nametable` naast een `.rel` | namenlijst voor tools | geen, wel in `files` | `tested` (gelezen) |
| `sfx/dlc_<naam>/<naam>.awc` en `<naam>_npc.awc` | de geluidsgolven (speler en NPC) | `AUDIO_WAVEPACK` (de map) | `tested` (gelezen) |

"Gelezen" betekent: zo staat het in werkende resources. Waarom FiveM de paden zonder `151.rel`, `54.rel` en `10.rel` wil, is niet nagezocht.

**Fout in de oude notities en in VehicleTool:** `docs/meta_reference_and_load_order.md` §10, `docs/vehicle_intake_procedure.md` §4 en `VehicleTool/checks.py` zetten `.dat10.rel` onder `AUDIO_GAMEDATA`. Het is `AUDIO_SYNTHDATA` (K39 in [duplicates_and_conflicts.md](duplicates_and_conflicts.md)).

---

## Regels voor de tool

Uit `docs/vehicle_intake_procedure.md` §4 en `docs/meta_reference_and_load_order.md` §10 (eerdere keuze: "manifest-first"):

- Het manifest is de bron van waarheid, niet de mapnaam.
- `sfx/` is nodig als `AUDIO_WAVEPACK` in het manifest staat.
- `audioconfig/` zonder de bijbehorende `sfx/`-map is onvolledig: melden als FAIL.
- `audioNameHash` moet wijzen naar een vanilla-voertuig of naar een geluidsobject dat de resource zelf meelevert (Q-M13: hoe controleren we dat de naam in een `.dat151.rel` staat?).

## Geluidspakket los van het voertuig

`research/Custom Engine Sounds` (Aquaphobic, v1.7) is een resource met alleen geluiden. Het manifest noemt **13** sets: brabus850, gt3flat6, k20a, lambov10, m158huayra, m297zonda, musv8, p60b40, predatorv8, rb26dett, rotary7, shonen en toysupmk4. De readme noemt er 11 (zonder `p60b40` en `shonen`). Alle 13 `sfx/dlc_*`-mappen staan op schijf (gecontroleerd op 20 okt 2026). Je gebruikt een geluid door `audioNameHash` in een `vehicles.meta` op die naam te zetten. Het pakket levert zowel `fxmanifest.lua` (`fx_version 'adamant'`) als `__resource.lua` ("use only one").

Gevolg voor de tool: een `audioNameHash` kan geldig zijn dankzij een **andere** resource. De controle moet dus over alle resources op de server kijken, niet alleen binnen het voertuig.

## In-game

Er bestaat een native om het motorgeluid van een voertuig te wisselen: `ForceUseAudioGameObject` (oude naam `_FORCE_VEHICLE_ENGINE_AUDIO`). `aanname`, te testen (Q-H10). Handig voor de in-game editor: geluiden uitproberen zonder de meta aan te passen.

## Beperkingen

- Niets hiervan is op de dev-server getest.
- `.rel`-bestanden zijn binair; de tool kan de namen erin alleen lezen met een parser (CodeWalker kan dat, Q-A5).
