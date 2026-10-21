# Controles: wat de tool moet nakijken

Alle controles uit de oude notities en de code bij elkaar, in één lijst met vaste ID's. Per controle: wat, hoe erg, of de tool het zelf mag oplossen, waar het vandaan komt, en of het al gebouwd is.
De labels staan uitgelegd in [README.md](README.md#labels).

**Ernst:** `FAIL` = blokkeert de volgende stap · `WARN` = nakijken · `INFO` = ter kennis · `SECURITY` = nooit automatisch oplossen, altijd een mens.
**Fix:** `auto` = de tool mag het zelf (met dry-run en back-up, B8) · `voorstel` = de tool stelt iets voor · `nee` = alleen melden.
**Gebouwd in VehicleTool** (Python, maart 2026): de foutcode uit `checks.py` of het script. "nee" = niet gebouwd. VehicleTool lost zelf nooit iets op in de bron; alleen de pack-sync schrijft (zie [inventory.md](inventory.md)).

Volgorde (eerdere keuze B5): R → F → M → X → A → T. Alleen-lezen controles mogen altijd draaien; fixes pas als de stap ervoor groen is.

---

## R. Resource en manifest

| ID | Controle | Ernst | Fix | Bron | Gebouwd in VehicleTool |
|----|----------|-------|-----|------|------------------------|
| R1 | `fxmanifest.lua` aanwezig | FAIL | auto: maken uit template | plan §7 stap 1 | `FXMANIFEST_MISSING` |
| R2 | `__resource.lua` in plaats van `fxmanifest.lua` | WARN (FAIL in het plan) | auto: omzetten (Q-S9) | plan §7 | `LEGACY_RESOURCE_MANIFEST` |
| R3 | Elk bestand in `files {}` bestaat. De server meldt dit zelf bij het starten ("could not find file …"), ook voor `client_script`, `server_script` en `shared_script`, maar niet altijd: een glob in een bestaande map die niets vindt (`data/*.meta`), meldt hij niet. Een `**`-glob die niets vindt, meldt hij wel (`tested`: `data/**/*.dat` in `PLOKS_CARS`) | WARN | auto: regel weg | plan §7; `official`, broncode (`ServerResources.cpp`) | nee |
| R4 | Elk pad in `data_file` bestaat. Hier meldt de server **niets**: hij controleert `data_file` niet, en de client geeft een ontbrekend pad zonder `*` gewoon door aan de game ([meta_files.md](meta_files.md) §10) | WARN | auto: regel weg | plan §7; `official`, broncode | alleen voor audio (`AUDIO_CONFIG_MISSING`, `AUDIO_WAVEPACK_*`) |
| R5 | Een meta staat in de resource maar niet in het manifest | WARN | auto: toevoegen | plan §7 | via R7 |
| R6 | `data_file`-type past bij het bestand (op root-element, niet op bestandsnaam). Ook: één bestand onder meerdere types (de Lore-pack laadt elke meta onder negen types, met `data_file 'HANDLING_FILE' 'data/**/*.meta'` enz.) | WARN | auto: corrigeren | plan §7; root-element: nieuw; meerdere types: downloads 21 okt (Q-S13) | nee |
| R7 | Bestand in de resource dat het manifest nergens noemt (`UNDECLARED_FILE_IN_RESOURCE`). **Uitzondering: alles in `stream/`** (FiveM streamt dat vanzelf) | WARN | nee | intake §3, meta_ref §11 | `UNDECLARED_FILE_IN_RESOURCE`, **zonder** de uitzondering: 164 vals alarmen in de laatste runs |
| R8 | `.lua`-bestanden in een voertuig-resource, behalve de manifests. Extra melden: netwerkverkeer (`PerformHttpRequest`) en server-instellingen (`SetConvarServerInfo`), zoals de versiechecks in twee packs uit de downloads; en `.dll`'s | SECURITY | nee, nooit verwijderen (B6) | plan §7; downloads 21 okt | `LUA_FILE_FOUND` (telt ten onrechte ook `__resource.lua`) |
| R9 | Escrow: `.fxap` of `dependency '/assetpacks'`. Zonder recht op het asset start de resource niet (`tested`: "You lack the required entitlement to use strman") | INFO | nee: resource alleen lezen | nieuw (zie [textures.md](textures.md)) | nee |
| R10 | Manifest lezen: `data_file 'X' 'y'` én `data_file('X')('y')`, `files {}` en `files({...})`, alle script-blokken | – | – | VT `AUDIT.md` | ja, maar `server_scripts {}` en `shared_scripts {}` worden niet gelezen |
| R11 | Volgorde van `data_file` volgens de afgesproken volgorde | INFO | voorstel | meta_ref §1, §7 | nee (Q-S7) |
| R12 | Het manifest is geldige Lua | FAIL | nee | nieuw: de eigen pack-manifest van VehicleTool was het niet (komma's ontbraken) | nee |
| R13 | De resource staat waar FiveM hem vindt: direct in `resources/` of in een map met haken (`[vehicles]`). Een map zonder haken is zelf een resource; FiveM kijkt er niet in. Dus: een pack-map zonder manifest laadt niets, en een resource ín een andere resource laadt nooit | FAIL | voorstel: verplaatsen | `official`, FiveM-broncode (`ServerResourceList.cpp`); `tested` in de serverlog op 21 okt ("does not have a resource manifest"); downloads: twee packs, zes wielen-packs en 29 geluids-resources laadden daardoor niet | nee |
| R14 | `data_file`-type staat in de officiële lijst ([meta_files.md](meta_files.md) §10) | WARN | voorstel | `official` (docs.fivem.net); in de downloads: `DLCTEXT_FILE`, `VEHICLE_SHOP_FILE`, `CARCONTENTUNLOCKS_FILE`, `CAR_ADDON_CONTENT_UNLOCKS`, `VEHICLE_SETTINGS_FILE` (Q-M15) | nee |
| R15 | Elk bestand achter een `data_file` staat ook in `files {}`. De client zoekt de `data_file`-globs alleen tussen de bestanden die hij gedownload heeft | WARN | auto: toevoegen | `aanname`, afgeleid uit de broncode (`ResourcesTest.cpp`); testen (Q-S3) | nee |
| R16 | Globs in `data_file` en `files` zijn hoofdlettergevoelig: `data/**/vehicles*.meta` vindt `Vehicles.meta` niet | WARN | voorstel | `official`, broncode (`ResourceMetaDataComponent.cpp`, `std::regex` zonder `icase`); in-game testen | nee |

## F. Mapstructuur

B1 is gekozen (één resource per voertuig); de indeling binnen de resource is nog open (B24, voorstel in [folder_structure.md](folder_structure.md) §3). Hieronder de controles uit het plan; ze gaan uit van `common/` + `stream/`. F10 geldt hoe de keuze ook uitvalt.

| ID | Controle | Ernst | Fix | Bron | Gebouwd in VehicleTool |
|----|----------|-------|-----|------|------------------------|
| F1 | Map voor meta's aanwezig (`common/`) | FAIL in plan, WARN in VT als `data/` er wel is | auto: maken | plan §7 stap 2 | `COMMON_MISSING`, `COMMON_MISSING_USING_DATA` |
| F2 | `stream/` aanwezig | FAIL | auto: maken, waarschuwen | plan §7 | `STREAM_MISSING` |
| F3 | Meta buiten de meta-map (`META_WRONG_LOCATION`) | WARN | auto: verplaatsen + manifest | plan §7, intake §2 | `META_WRONG_LOCATION` (ook voor `data/`) |
| F4 | `.meta` of asset-bestand in de root | WARN | auto: verplaatsen | plan §7 | `ROOT_FILE_SHOULD_BE_MOVED` |
| F5 | Ander onverwacht bestand in de root (toegestaan: de manifests en een readme) | WARN | nee | VT | `UNEXPECTED_ROOT_FILE` |
| F6 | Onverwachte map in de root (`x64/`, …): niet-omgezette GTA-structuur | WARN | nee | plan §7 | `UNEXPECTED_ROOT_DIR` (toegestaan: `common`, `data`, `stream`, `audio`, `audioconfig`, `sfx`; vergelijkt hoofdlettergevoelig) |
| F7 | Meerdere voertuigen in één `vehicles.meta` (`PACK_MODE`) | INFO | voorstel: splitsen | meta_ref §4.3, §7 | `check_resource_meta.py` (alleen onder `data/`), `split_multi_vehicle.py` |
| F8 | Map-bestanden in een voertuig-resource (`.ymap`, `.ytyp`, gebouw-`.ydr`) | WARN | nee | nieuw (`11john11_sapo_pack`) | nee |
| F9 | `.rpf` in de resource: moet eerst omgezet. Ook in `stream/` (gezien: `PLOKS_CARS/stream/[ROLLSROYCE]/rculi/rculi_mods.rpf`, Q-S14) | FAIL | voorstel: intake | canvas; downloads 21 okt | nee |
| F10 | `stream/` staat direct in de root van de resource. Een `stream/` dieper in de resource (zoals `Vehicles/<categorie>/stream/` in de oude repo) wordt niet automatisch gestreamd (alleen een script kan met `REGISTER_RESOURCE_ASSET` nog een los bestand aanmelden) | FAIL | voorstel: verplaatsen | `official`, broncode (`ResourceStreamComponent.cpp`: alleen `<resource>/stream/`) | nee |

## M. Meta-inhoud en koppelingen

| ID | Controle | Ernst | Fix | Bron | Gebouwd in VehicleTool |
|----|----------|-------|-----|------|------------------------|
| M1 | XML is geldig en het root-element hoort bij het type. In de downloads: 13 bestanden die een strikte parser weigert (`--` in commentaar, verkeerde sluit-tags, NUL-bytes aan het eind, spaties vóór `<?xml`). Of de game ze slikt, bepaalt de ernst (Q-M16) | FAIL | nee | nieuw; downloads 21 okt | `VEHICLES_META_XML_INVALID`, `CARVARS_ROOT_*`, `CARCOLS_ROOT_*`, `HANDLING_XML_INVALID`; niet voor de andere meta's |
| M2 | Verplichte meta's per type aanwezig | FAIL / INFO | auto: uit template | plan §7 stap 3 | `META_MISSING`: zes bestanden voor **elk** type (ook `dlctext`, `shop_vehicle`); `vehiclelayouts` optioneel. Omstreden: B13, Q-S8 |
| M3 | Kernvelden gevuld: `modelName`, `txdName`, `handlingId`, `gameName`, `type` | FAIL | nee | VT | `VEHICLES_META_FIELD_MISSING` (alleen het eerste voertuig) |
| M4 | `modelName` heeft een `.yft` in `stream/` | FAIL | nee | plan §7, `vehicles_meta_fields.md` | in de UI (WARN) en in de split |
| M5 | `txdName` heeft een `.ytd`; `txdName` = `modelName` | FAIL / WARN | nee | plan §7 | alleen in de split (`<modelName>.ytd`) |
| M6 | `handlingId` bestaat als `handlingName` | FAIL | nee | plan §7 | alleen met een gekozen profiel (`HANDLING_LINE_NOT_FOUND`); de split vergelijkt hoofdlettergevoelig, `checks.py` niet (Q-M8) |
| M7 | `modelName` in `carvariations` = `modelName` in `vehicles.meta` | FAIL | nee | CARCOLS_REF §1 | alleen in de split |
| M8 | Elke `kitName` uit `carvariations` bestaat in `carcols` | FAIL | nee | CARCOLS_REF §3 | alleen in de split |
| M9 | Elke `visibleMods/modelName` uit een kit heeft een `.yft` | WARN | nee | META_SPLIT_POLICY regel 5 | in de split, maar **werkt niet** (bug: geeft altijd een lege lijst) |
| M10 | `sirenSettings` / `lightSettings` wijzen naar een bestaand id | WARN | nee | CARCOLS_REF §1 | nee (de split gooit `Lights` en `Sirens` zelfs weg) |
| M11 | `layout` bestaat (vanilla-lijst of eigen `vehiclelayouts.meta`) | WARN | nee | nieuw | nee |
| M12 | `audioNameHash` bestaat (vanilla of eigen audio, ook in een andere resource) | WARN | nee | [audio.md](audio.md) | deels: de UI zoekt audio-bestanden met die naam (Q-M13) |
| M13 | `txdRelationships`: parent bestaat; relaties met een vreemde `child` melden | WARN | nee | nieuw (`strman`) | nee |
| M14 | Twee identieke `carcols.meta` (zelfde SHA256) | WARN | voorstel: één gedeelde | META_SPLIT_POLICY | `check_resource_meta.py` |
| M15 | Meerdere modellen in één `carvariations.meta`, meerdere handlings in één `handling.meta` | INFO | voorstel: splitsen | META_SPLIT_POLICY | `check_resource_meta.py` |
| M16 | Waar de naam vandaan komt: `AddTextEntry` in een `.lua` (ook `AddTextEntryByHash` met de hash van `gameName`), of nergens (`TEXT_SOURCE`). In de downloads heeft 152 van de 362 voertuigen die we konden lezen geen tekst (Q-M18) | WARN als nergens | nee | meta_ref §5; downloads 21 okt | nee |
| M17 | Type en klasse passen bij elkaar | WARN | voorstel | VT, meta_ref §8 | `TYPE_CLASS_MISMATCH`, maar de tabel is **te streng** (zie onder) |
| M18 | `wheelType` past bij type en klasse (bijv. motor met `VWT_BIKE`) | WARN | nee | meta_ref §8 (backlog) | nee |
| M19 | Handling binnen de bereiken van het profiel (klasse) | WARN | voorstel | handling_template §8 | `HANDLING_RANGE_OUTSIDE`, alleen met een UI-profiel; ging in geen enkel rapport af |
| M20 | Naamregels: lengte, tekens, kleine letters | WARN | voorstel | `vehicles_meta_fields.md` | alleen in de UI: `gameName` > 11 en `handlingId` > 14 tekens (Q-M6) |
| M21 | Kit-id in een vanilla-bereik (83–91, 96–453, 999) of buiten het geldige bereik | WARN | voorstel: vrij id | CARCOLS_REF §4 | `MODKIT_ID_VANILLA_RANGE` (geen check boven 1023, Q-M4) |
| M22 | Liveries kloppen: de `<liveries>`-schakelaars in `carvariations` passen bij wat er in de `.ytd` en de kits zit | WARN | nee | meta_ref §7 (TODO) | nee |
| M23 | Een kit in `carcols` die geen enkel voertuig gebruikt (bijv. `alamo`) | INFO | nee | nieuw | nee |
| M24 | Hoge downforce (`fDownforceModifier`) buiten de klasse Super | WARN | nee | `research/DriveV/README.md` | nee |
| M25 | Offroad-voertuig met de grip van een straatauto | WARN | nee | `research/DriveV/README.md` | nee |
| M26 | Varianten (bijv. taxi en politie van hetzelfde model) met exact dezelfde handling | INFO | nee | `research/DriveV/README.md` | nee |
| M27 | `vehicleClass` is een bestaande `VC_*`-naam (gezien: `VC_SPORTS`, `VC_COMPACTS`) | FAIL | voorstel: dichtstbijzijnde naam | downloads 21 okt (Q-M17) | nee |
| M28 | `handlingId` van een vanilla-voertuig (`BALLER`, `SURANO`): geen fout, wel melden, want de handling is dan niet van de resource zelf | INFO | nee | downloads 21 okt (14 voertuigen) | nee |

**Type en klasse.** VehicleTool keurt bijvoorbeeld `VEHICLE_TYPE_BIKE` met `VC_EMERGENCY` af. Vanilla heeft die combinatie wel: `policeb` en `policeb2` (motor, Emergency). Andere vanilla-combinaties die de tabel van VehicleTool afkeurt: heli met Military (`thruster`), blimp met Planes, trailer met Military, amfibie-auto met Military. Bron: `data/vehicles.json` in de kennisbasis (`tested`, build 3889). En in onze eigen testdata: `sheriffmav` in `11john11_sapo_pack` is een heli met `VC_EMERGENCY`. De controle moet dus uit echte data komen, niet uit een eigen tabel.

## X. Botsingen over de hele server

Deze controles kijken naar **alle** resources, niet één. VehicleTool deed het alleen binnen zijn eigen pack, met een register (`registry/vehicles_index.json`).

| ID | Controle | Ernst | Fix | Bron | Gebouwd in VehicleTool |
|----|----------|-------|-----|------|------------------------|
| X1 | Zelfde bestandsnaam in `stream/` van twee resources (alle extensies uit [folder_structure.md](folder_structure.md) §4) | FAIL | nee: eerst oplossen | meta_ref §9, intake §7 | binnen de pack, bij het toevoegen (blokkeert) |
| X2 | Zelfde `modelName` twee keer | FAIL | nee | nieuw | nee |
| X3 | Zelfde `handlingName` twee keer (met andere waarden) | WARN | nee | nieuw | nee |
| X4 | Zelfde kit-id twee keer | FAIL | voorstel: vrij id (B9) | CARCOLS_REF §4 | binnen de pack: `verify_modkit_ids.py` en een blokkade bij het toevoegen; die blokkade kijkt naar de **bron**-`carcols`, terwijl de pack de template krijgt (zo kregen alle vier id 10000) |
| X5 | Vanilla-naam in `stream/` (vervangt een game-bestand voor iedereen) | WARN | nee | nieuw (Q-T6) | nee |
| X6 | Identieke `.ytd` onder twee namen (bijv. `brickadeb.ytd` = `brickadebr.ytd`) | INFO | voorstel: delen via `txdRelationships` | nieuw (gevonden met md5) | nee |
| X7 | Zelfde bestandsnaam twee keer in `stream/` van **één** resource (in submappen). FiveM gebruikt alleen de bestandsnaam, dus ze botsen ook dan. Gezien: `spoiler_2.yft` bij drie auto's in `PLOKS_CARS`, met verschillende inhoud; zes `_manifest.ymf` in de Lore-pack | FAIL (andere inhoud) / INFO (zelfde inhoud) | nee | `official`, broncode (`ResourceStreamComponent.cpp`): de naam telt, en binnen één resource houdt de server stil het eerst gevonden bestand; tussen resources open (Q-S6) | nee |

## A. Audio

| ID | Controle | Ernst | Fix | Bron | Gebouwd in VehicleTool |
|----|----------|-------|-----|------|------------------------|
| A1 | Elk `AUDIO_*`-pad uit het manifest bestaat (`x.dat` → `x.dat151.rel` voor `AUDIO_GAMEDATA`, `x.dat54.rel` voor `AUDIO_SOUNDDATA`, `x.dat10.rel` voor `AUDIO_SYNTHDATA`) | FAIL | nee | intake §4 | `AUDIO_CONFIG_MISSING` (accepteert `.dat10.rel` ten onrechte als `AUDIO_GAMEDATA`, K39) |
| A2 | `AUDIO_WAVEPACK` is een map met minstens één `.awc` | FAIL | nee | intake §4 | `AUDIO_WAVEPACK_MISSING`, `_EMPTY` |
| A3 | `audioconfig/` zonder `sfx/` = onvolledig | FAIL | nee | meta_ref §10 | via A1 en A2 |

## T. Textures en assets

| ID | Controle | Ernst | Fix | Bron | Gebouwd in VehicleTool |
|----|----------|-------|-----|------|------------------------|
| T1 | Geheugen per bestand uit de RSC7-header, phys en virt apart. FiveM meldt boven 16 MiB (blauw), 32 MiB (geel) en 64 MiB (rood); boven 48 MiB staat erbij dat het streamingproblemen geeft | WARN boven 16 MiB, FAIL boven 48 MiB (voorstel) | voorstel (Q-T4) | `official`, broncode (`ResourceStreamComponent.cpp`), en `tested` in de serverlog (Q-T1); zie [textures.md](textures.md) | nee (script getest op 20 okt) |
| T2 | Versleuteld bestand (`FXAP`) | INFO | nee | nieuw | nee |
| T3 | Per texture: resolutie, formaat, mips, aantal (pas als we een `.ytd` kunnen lezen) | INFO | voorstel | plan §7 stap 4 | nee; `trp_dds_inspector` doet het op met OpenIV geëxporteerde `.dds` |
| T4 | `+hi.ytd` identiek aan of groter dan de gewone `.ytd` | INFO | nee | nieuw (Q-T5) | nee |

---

## Rapport

Uit VehicleTool en het plan:

- Uitkomst per controle als PASS / WARN / FAIL, en een totaal (FAIL zodra er één FAIL is). CLI: exitcode 0 bij PASS of WARN, 1 bij FAIL.
- Tekst én JSON (`--json`), opgeslagen per voertuig (`report/<handlingId>/<handlingId>_<datum>_report.txt`).
- Een dry-run die laat zien wat een fix zou doen, en een back-up vóór het schrijven.
- Per voertuig een spoor bewaren van wat er gecontroleerd en veranderd is (`docs/vehicle_intake_procedure.md` §10: "per voertuig audittrail bewaren").

**Lessen uit de rapporten van maart 2026** (40 runs over 10 resources):

- Elke keer dat het padveld de focus verloor, kwam er een volledig nieuw rapport, ook als er niets veranderde (13 identieke van `scout2020`). Liever: alleen een nieuw rapport als de uitkomst anders is.
- De rapportmap volgt de `handlingId`, en anders de mapnaam. Daardoor kwam één resource onder twee namen terecht (`bike/` en `pdbf400rb/`). Liever: één vaste sleutel per resource.
- Alleen het eerste voertuig in een `vehicles.meta` werd gecontroleerd. Een pack met twee voertuigen (`pigeonp`) werd dus maar half nagekeken.
- 164 van de 210 waarschuwingen waren vals alarm (R7, stream-bestanden). Te veel ruis zorgt dat je de echte meldingen mist.

## Intake-checklist (uit `docs/vehicle_intake_procedure.md` §11)

- [ ] Manifest aanwezig en leesbaar
- [ ] Verplichte meta's gevonden
- [ ] Waarschuwingen over de plek van meta's bekeken
- [ ] Bestanden die het manifest niet noemt bekeken (`.lua`, `.txt`, restanten)
- [ ] Audio in het manifest gecontroleerd (`audioconfig` + `sfx`)
- [ ] Geen botsende namen in `stream/`
- [ ] Velden nagekeken en waar nodig aangepast
- [ ] Pas daarna kopiëren naar de pack
