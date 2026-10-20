# Mapstructuur van voertuig-resources

Hoe een voertuig-resource op schijf staat, welke varianten we tegenkwamen, en hoe FiveM resources en `stream/` vindt.
De labels staan uitgelegd in [README.md](README.md#labels).

**Gekozen (Mark, 21 okt 2026): één resource per voertuig** (B1 in [decisions.md](decisions.md)). Liveries gaan mee in die resource, met een duidelijke indeling. Packs worden gesplitst (B2). Nog open: de indeling binnen de resource en de naam (B24, voorstel in §3), en waar livery soort 4 heen gaat (B23, §2).

---

## 1. Wat we tegenkwamen

Vijftien manieren in onze eigen map, de repo, de testdata en de downloads. Allemaal `tested` in de zin van: zo staan ze echt op schijf (gelezen op 20 en 21 okt 2026). Of ze in FiveM allemaal werken, is niet overal getest.

| # | Variant | Waar gezien | Meta | Stream | Manifest |
|---|---------|-------------|------|--------|----------|
| A | **Converter-uitvoer** (convert.cfx.rs) | `TestVehicleFolder/kriegerty2`, alle packs in `research/` behalve DriveV en Custom Engine Sounds | `common/*.meta` | `stream/` | `fxmanifest.lua`, `games { 'gta5' }`, `files { ... 'common/*.meta' }`, één `data_file` per bestand |
| B | **Betaald / escrow** | `TestVehicleFolder/strman` | `data/*.meta` | `stream/` (deels versleuteld) | `.fxap` en `dependency '/assetpacks'` |
| C | **Oud, alles in de root** | `TestVehicleFolder/zaccflatlit` | in de root | `stream/` | `__resource.lua` |
| D | **Pack, map per voertuig** (VehicleTool-doel) | `VehicleTool/pack` | `data/<HANDLINGID>/*.meta` | één gedeelde `stream/`, recursief | globs: `data_file 'HANDLING_FILE' 'data/**/handling.meta'` |
| E | **Pack, map per DLC** | `research/DriveV` | `meta/*.meta` en `meta/<dlc>/*.meta` | geen eigen modellen | globs: `meta/**/*.meta` |
| F | **Per categorie** (FivemVehicleTool-repo) | GitHub `FivemVehicleTool` | `Vehicles/<categorie>/meta/<resource>_<bestand>.meta` | `Vehicles/<categorie>/stream/`: **wordt niet gestreamd**, want `stream/` moet in de root van de resource staan (§5) | één centrale `fxmanifest.lua`, `data_file` als tabel (Q-S12) |
| G | **VehicleOptimizer** | `VehicleOptimizer/` | uitvoer: `<klasse>/<naam>/data/*.meta`; de (ongebruikte) manifest-template gaat uit van `meta/` en `audio/` | `<klasse>/<naam>/<naam>.yft` en `.ytd`, zonder `stream/` | geen; template met wildcards zoals `meta/vehicles*.meta` |
| H | **Plan van maart 2026** | `docs/plan.md` §5 (en "1 model per folder/resource" in `docs/meta_reference_and_load_order.md` §4.3) | `common/` | `stream/` | gelijk aan A |
| I | **Intake-doel "VehiclePack"** | `docs/vehicle_intake_procedure.md` §5 | `data/<handlingId>/` | gedeeld `stream/`, plus `audio/` en `sfx/` | gelijk aan D |
| J | **Split-beleid** | `VehicleTool/docs/META_SPLIT_POLICY.md` | per model één map, `carcols` gedeeld in `data/common/` of per model ingekort | `stream/<modelName>/` | handmatig |
| K | **Engine-geluiden** | `research/Custom Engine Sounds` | geen | `audioconfig/` + `sfx/dlc_<naam>/` | `fx_version 'adamant'`, plus een `__resource.lua` ernaast ("use only one") |
| L | **Eigen converter** | `trp_rpf_to_fivem_converter` | `data/` (plat, ook `content.xml` en `setup2.xml` van de DLC) | `stream/` (plat; dubbele namen worden hernoemd) | geen |
| M | **Pack per merk** | downloads: `PLOKS_CARS` (189 auto's) | `data/[MERK]/<model>/*.meta` | `stream/[MERK]/<model>/` | per type één glob: `data_file 'HANDLING_FILE' 'data/**/handling*.meta'` |
| N | **Pack per merk, met volledige namen** | downloads: `Lore_Friendly_Car_Pack` (72 voertuigen) | `data/[MERK]/<Merk Model Custom>/*.meta`, met spaties en `'` in de mapnaam | `stream/[MERK]/<zelfde naam>/`, plus `audio/` | élke meta onder élk type: `data_file 'HANDLING_FILE' 'data/**/*.meta'` enz. (Q-S13) |
| O | **Pack met losse geluids-resources erin** | downloads: `lds-lorevehicles` (98 voertuigen) | `data/<model>/*.meta` | `stream/vehicles/<model>/` en `stream/vehmods/<model>/` | globs; de 29 geluids-resources staan in `[lorevehicles-sounds]/` **binnen** de resource en laden daardoor nooit (§5) |

Wat opvalt:

- **De mapnaam van de meta's verschilt** (`common/`, `data/`, `meta/`, de root). Voor FiveM telt alleen het pad in `data_file` (§5). Of de game zelf iets met de map doet: `aanname`, te testen (Q-S1 in [open_questions.md](open_questions.md)).
- **De bestandsnaam van een meta mag vrij zijn.** Packs gebruiken `vehiclelayouts_bcat.meta`, `vehicleweapon_shermav.meta` en `weaponminigun.meta`; de repo zet de voertuignaam ervoor (`ferrari_f40_handling.meta`). Het `data_file`-type bepaalt wat het is. `community`, te testen (Q-S2).
- **Globs in `data_file`** (`data/**/handling.meta`) gebruiken DriveV, onze pack en alle drie de downloads. Dat FiveM ze leest, ook `**`, en hoofdlettergevoelig, staat in de broncode (`official`, §5); in-game nog bevestigen (Q-S3). Let op: Python (`PurePosixPath.match`, gebruikt door VehicleTool) leest `**` anders dan FiveM.
- **De converter zet zowel elke meta los als `'common/*.meta'` in `files`.** Dubbel, maar onschuldig. `tested` (gelezen).
- **`stream/` met submappen** komt veel voor (VehicleTool, de drie downloads). FiveM streamt submappen mee en kijkt alleen naar de bestandsnaam (`official`, §5).

---

## 2. Liveries: vier manieren, en wat dat voor de mappen betekent

Mark vroeg (21 okt): "liveries horen bij 1 voertuig toch?" **Ja, voor soort 1, 2 en 3**: dat zijn uiterlijken van hetzelfde model, en ze gaan mee in de resource van dat voertuig. **Soort 4 niet**: dat is voor de game een apart voertuig met een eigen `modelName`, dat alleen lijkt op een livery. Waar die heen gaat, is B23 (voorstel: in de resource van het basisvoertuig).

| Soort | Hoe | Voorbeeld | Bestanden | Hoort bij |
|-------|-----|-----------|-----------|-----------|
| 1. **Livery in de texture** | Livery-textures in de `.ytd` van het voertuig; aan/uit per slot in `carvariations.meta` `<liveries>`; namen via `liveryNames` in `carcols` | `strman/[Template]/strman_sign_1.dds` (een sjabloon voor zo'n livery). In de downloads gebruikt geen enkel voertuig `<liveries>` | `<model>.ytd` | hetzelfde model |
| 2. **Livery als mod-onderdeel** | Elke livery is een eigen `.yft`, als `VMT_LIVERY_MOD` in een modkit in `carcols.meta` | `batic_livery1.yft` … `batic_livery18.yft`, `kriety2_liv1.yft`; in de downloads 95 kits met `VMT_LIVERY_MOD`, tot 31 per kit | `<model>_livery<n>.yft` + kit in `carcols` | hetzelfde model |
| 3. **Tweede livery-laag** | `livery2` / dak-livery | (niet in testdata; `livery2Names` komt wel voor in `carcols` van de downloads) | nog uitzoeken (Q-M7) | hetzelfde model |
| 4. **Apart model per uiterlijk** | Elke variant een eigen `modelName`, vaak dezelfde handling | `lsfd` … `lsfd5`, `halfback` + `halfback2` (USSS) | eigen `.yft`/`.ytd` en eigen entry in `vehicles.meta` | apart voertuig (B23) |

Bronnen: GTAMods en Dawnstar (`community`, zie [sources.md](sources.md)), samengevat in [meta_files.md](meta_files.md).

Een extra `.ytd` naast het model (zoals `bell505a.ytd`) is meestal geen tweede voertuig maar een texture-laag via `txdRelationships` (zie [textures.md](textures.md#txdrelationships)).

In rapporten gebruikten we de notatie `livery_group = <modelName>`. Bronbestanden of werkbestanden van liveries (zoals het sjabloon in `strman/[Template]/`) zijn niet nodig voor het spel en horen niet in `stream/` (`docs/meta_reference_and_load_order.md` §4.4); in het voorstel hieronder gaan ze naar `source/`.

---

## 3. Eén resource per voertuig: de indeling (voorstel, B24)

### Wat B1 betekent

- Een voertuig is los aan en uit te zetten; een fout raakt alleen dat voertuig.
- Dezelfde vorm als de converter (variant A), dus nieuwe voertuigen passen er meteen in.
- Een server krijgt honderden resources. Wat dat kost (starttijd, joinen, geheugen), is Q-S10 (prio hoog, B2).
- Gedeelde dingen (sirenes, lichten, wielen) staan per voertuig in de eigen `carcols.meta`. Hun id's moeten over de hele server uniek zijn (X4 in [validation_rules.md](validation_rules.md)).
- Een pack (zoals M, N en O hierboven) splitst de tool bij de intake naar losse resources (B2, functie F-D2 in [tool_functions.md](tool_functions.md)).

### Voorstel

```text
resources/
  [vehicles]/                        -- categorie: FiveM zoekt alleen in mappen met haken
    [emergency]/                     -- mag: een categorie in een categorie (§5)
    veh_kriegerty2/                  -- één voertuig; naam: zie hieronder
      fxmanifest.lua
      data/
        vehicles.meta
        handling.meta
        carvariations.meta
        carcols.meta                 -- alleen bij eigen kits, lichten of sirenes
        vehiclelayouts.meta          -- alleen bij een eigen layout
      stream/                        -- moet direct in de root staan (§5)
        kriegerty2.yft
        kriegerty2_hi.yft
        kriegerty2.ytd               -- livery soort 1 zit hierin
        kriegerty2+hi.ytd
        mods/                        -- onderdelen uit de kit: kriegerty2_<deel>.yft
        liveries/                    -- livery soort 2 (en 3): kriegerty2_livery<n>.yft
      audio/                         -- alleen bij eigen motorgeluid
        audioconfig/<naam>_game.dat151.rel, <naam>_sounds.dat54.rel
        sfx/dlc_<naam>/<naam>.awc, <naam>_npc.awc
      source/                        -- niet voor de game: livery-sjablonen, readme, licentie van de maker
```

Keuzes die Mark nog maakt (B24):

| Keuze | Voorstel | Alternatief | Waarom |
|-------|----------|-------------|--------|
| Naam van de resource | `veh_<modelName>` | `<modelName>`, of `<maker>_<modelName>` | Met `veh_` staan ze bij elkaar en botsen ze nooit met een script; de `modelName` zelf blijft zoals hij is |
| Map voor de meta's | `data/` | `common/` (zoals de converter) | De drie downloads en `strman` gebruiken `data/`; voor FiveM maakt het niet uit (Q-S1) |
| Eén bestand per type | ja, zonder voertuignaam ervoor | `kriegerty2_handling.meta` | De resource zegt al welk voertuig het is |
| Submappen in `stream/` | `mods/` en `liveries/` | alles plat in `stream/` | Overzicht; voor FiveM maakt het niet uit (§5). De bestandsnamen moeten hoe dan ook uniek zijn op de hele server |
| Livery soort 4 (B23) | in dezelfde resource: een `Item` per model in dezelfde meta's, de bestanden van elk model in dezelfde `stream/` | elk model een eigen resource | Ze delen meestal handling en textures |
| Categorieën | `[vehicles]`, eventueel met submappen per klasse of herkomst | alles plat in `[vehicles]` | Honderden resources blijven zo overzichtelijk |

Zo'n resource heeft een kort manifest; de tool maakt het uit wat er echt staat (prioriteit 2, B12):

```lua
fx_version 'cerulean'
game 'gta5'

files {
    'data/*.meta',
}

data_file 'HANDLING_FILE'          'data/handling.meta'
data_file 'VEHICLE_METADATA_FILE'  'data/vehicles.meta'
data_file 'CARCOLS_FILE'           'data/carcols.meta'
data_file 'VEHICLE_VARIATION_FILE' 'data/carvariations.meta'
```

### Wat we eerder overwogen

Op 20 okt stonden vier opties naast elkaar, omdat de bronnen elkaar tegenspraken. Het voorlopige advies van toen (optie 2: één pack met een map per voertuig) vervalt door B1.

| Bron | Zei |
|------|-----|
| `docs/meta_reference_and_load_order.md` §4.3 | "1 model per folder/resource"; meerdere voertuigen = `PACK_MODE`, liefst splitsen naar losse resources met elk een eigen `fxmanifest.lua` |
| `docs/vehicle_intake_procedure.md` §5 | Eén `VehiclePack`-resource met `data/<handlingId>/` en één gedeelde `stream/` |
| `VehicleTool/docs/META_SPLIT_POLICY.md` | Per bestand één voertuig; `carcols` óf gedeeld óf per model ingekort |
| FivemVehicleTool-repo | Eén resource, per categorie, meta's met voertuignaam ervoor |
| `docs/plan.md` §5 | Per voertuig een resource met `common/` + `stream/` |

- **Optie 2, één pack met een map per voertuig:** één manifest, maar een kapotte meta kan het hele pack raken (Q-S5), en alles moet samen aan of uit.
- **Optie 3, één bestand per type voor het hele pack:** één XML-fout raakt alle voertuigen; dit wilden we eerder al niet (`META_SPLIT_POLICY.md`).
- **Optie 4, per categorie:** de categorie komt uit `vehicleClass`, en die herkenning faalde (K24 in [duplicates_and_conflicts.md](duplicates_and_conflicts.md)).

---

## 4. Namen in `stream/`

Wat we in de testdata zien (`tested`, gelezen 20 okt 2026). Of de engine dit afdwingt, staat erbij.

| Bestand | Betekenis | Status |
|---------|-----------|--------|
| `<model>.yft` | het model; naam = `modelName` | `community` |
| `<model>_hi.yft` | model in hoge kwaliteit, voor dichtbij | `community` |
| `<txd>.ytd` | textures; naam = `txdName` | `community` |
| `<txd>+hi.ytd` | textures in hoge kwaliteit (afstand: `HDTextureDist`) | `community` |
| `<model>_<onderdeel>.yft` | mod-onderdeel uit een kit (`batic_exh1.yft`, `polstan_pbar.yft`) | `community` |
| `<andere>.ytd` | texture-laag via `txdRelationships` (`bell505a.ytd`) | `community` |
| `vehicles_<x>_interior.ytd` | **vanilla-naam**: vervangt de gedeelde texture van de game voor iedereen | `aanname`, gezien in `11john11_sapo_pack` (Q-T6) |
| `.ydr`, `.ycd` | wielen (`extramuscle`, `vanillawheels`), animaties (`va_str.ycd`) | `tested` (gelezen) |

### Bestandstypen die in `stream/` horen

Deze lijst stond drie keer in de oude notities (`docs/meta_reference_and_load_order.md` §12, `docs/vehicle_intake_procedure.md` §8 en het canvas), en twee keer in de VehicleTool-code (`checks.py` en `ui.py`). VehicleTool gebruikt hem voor de botsingscontrole en voor een waarschuwing als zo'n bestand in de root staat. De extensies zelf: `community`. Bij vier stond in de oude lijst waarschijnlijk een **verkeerde betekenis**; de juiste is een `aanname` (na te kijken in CodeWalker, dat per type een eigen bestandsklasse heeft).

| Extensie | Betekenis | Oude lijst zei |
|----------|-----------|----------------|
| `.yft` | fragment (voertuigmodel, ook mod-onderdelen) | |
| `.ytd` | texture dictionary | |
| `.ydr` | drawable (3D-model, bijv. wielen) | |
| `.ydd` | drawable dictionary | |
| `.ybn` | collision (bounds) | |
| `.ycd` | clip dictionary (animaties) | |
| `.yfd` | frame filter dictionary (animatie) | fragment dictionary |
| `.yed` | expression dictionary | |
| `.yld` | cloth dictionary (kleding/stof) | lights |
| `.ypt` | particle effects | |
| `.ypdb` | pose matcher database (animatie) | particle database |
| `.ywr` | waypoint recording | water |
| `.ytyp` | type definitions (map) | |
| `.ymap` | map placement (map) | |
| `.ynv` | navigation mesh (map) | |
| `.ynd` | path nodes (map) | |
| `.ymf` | manifest (`_manifest.ymf`) | |
| `.ymt` | binaire meta (niet hetzelfde als de XML `*.meta`) | |
| `.yvr` | vehicle records | |

Voor een voertuig horen vooral `.yft`, `.ytd`, `.ydr` (wielen) en soms `.ycd`. De map-typen (`.ymap`, `.ytyp`, `.ynv`, `.ynd`) horen er niet in.

**`stream/` hoeft niet in `files {}`.** FiveM streamt de map `stream/` vanzelf. Zet je `.y*`-bestanden uit `stream/` toch in `files {}`, dan haalt de server ze daar weer uit, behalve `.ytyp` (`official`, `ResourceFilesComponent.cpp`). `files {}` is voor bestanden die de client moet downloaden, zoals de meta's achter `data_file`. VehicleTool meldde elk stream-bestand als "niet in het manifest": 164 van de 210 waarschuwingen in de laatste runs, allemaal vals alarm.

**`_manifest.ymf`** staat in sommige resources in `stream/` (gezien in de bron van `pigeonp`). In een gedeelde pack-`stream/` botst hij met die van een ander voertuig: de Lore-pack uit de downloads heeft er zeven (Q-S11). Bij één resource per voertuig speelt dat niet.

### Unieke namen

Een bestandsnaam in `stream/` moet uniek zijn over alle resources op de server. FiveM kijkt alleen naar de bestandsnaam, niet naar de map (`official`, §5). Twee bestanden met dezelfde naam botsen dus ook binnen één resource. Welke dan wint, weten we niet (Q-S6).

In de downloads komt dat echt voor: in `PLOKS_CARS` heten de spoilers van drie verschillende auto's `spoiler_2.yft` (andere inhoud), en tussen de Lore-pack en `lds-lorevehicles` botsen 1.474 namen, omdat ze voor een deel dezelfde voertuigen bevatten ([test_data.md](test_data.md#downloads-in-vehicles-21-okt-2026)). VehicleTool controleerde daarom al op botsende namen (X1 en X7 in [validation_rules.md](validation_rules.md)).

In `11john11_sapo_pack` zitten ook map-bestanden (`sc1_19_*.ytd/.ydr`) tussen de voertuigen. Een voertuig-pack hoort zulke bestanden niet te hebben: de tool moet ze melden.

---

## 5. Hoe FiveM resources en `stream/` vindt (broncode)

`official`: gelezen in de FiveM-broncode, master van 20 okt 2026. Nog niet in-game getest, maar het verklaart wat we in de downloads zien.

**Resources vinden** (`code/components/citizen-server-impl/src/ServerResourceList.cpp`, `ServerResourceMounter.cpp`):

- De server doorzoekt `resources/`. Een map met haken (`[vehicles]`) is een **categorie**: daar kijkt hij in, ook in categorieën binnen categorieën.
- **Elke andere map is een resource**, met de mapnaam als naam. Heeft die map geen `fxmanifest.lua` of `__resource.lua`, dan meldt de server "*naam* does not have a resource manifest (fxmanifest.lua)" en laadt hij niets. **In die map kijkt hij niet verder.**
- Gevolg 1: een gedownload pack dat je in zijn geheel neerzet (`[Vehicles]/FiveM-Civ-Car-Pack/PLOKS_CARS/`), laadt niet. De map `FiveM-Civ-Car-Pack` geldt als resource zonder manifest.
- Gevolg 2: een resource **in** een andere resource laadt nooit, ook niet in een map met haken (`lds-lorevehicles/[lorevehicles-sounds]/zr250/`).
- Dezelfde resourcenaam twee keer: de server gebruikt de eerste die hij vindt en meldt "exists in more than one place".
- Een categorie (met haken) mét een manifest: de server meldt dat en behandelt hem als categorie.
- Mappen die met `.` beginnen, `.git` en `txAdmin` slaat hij over.

**`stream/`** (`ResourceStreamComponent.cpp`):

- Alleen `<resource>/stream/` telt, direct in de root van de resource.
- De server loopt die map **recursief** door; submappen die met `.` beginnen slaat hij over.
- De naam in de game is **alleen de bestandsnaam**, zonder map. Hij wordt opgeslagen in 128 tekens; een langere naam wordt afgekapt.
- Een bestand `<naam>.stream_raw` naast een bestand telt niet als eigen bestand.
- Elk bestand met een RSC-header krijgt een geheugencontrole: zie [textures.md](textures.md#de-melding-van-fivem).

---

## Links

- Converter: https://convert.cfx.rs/en
- Meta-splitter (community): https://github.com/zfbx/fivem-meta-splitter
- Liveries: GTAMods [Carvariations.ymt](https://gtamods.com/wiki/Carvariations.ymt), [Carcols.ymt](https://gtamods.com/wiki/Carcols.ymt)
- FiveM-broncode: https://github.com/citizenfx/fivem (bestanden in §5)

## Beperkingen

- Of FiveM varianten A t/m O allemaal accepteert, is niet getest. §5 komt uit de broncode; de tests staan in [open_questions.md](open_questions.md).
- Hoe FiveM omgaat met twee resources die dezelfde `modelName` of `handlingName` registreren, weten we niet (Q-S6).
