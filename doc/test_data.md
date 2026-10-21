# Testdata: welke voertuigen we hebben en wat ze laten zien

De voertuigen en packs in `TestVehicleFolder/`, `research/`, `VehicleTool/pack/` en `VehicleOptimizer/output/` (sinds 21 okt 2026 in `archive/` van de projectmap), en de downloads die Mark in `[Vehicles]` van de dev-server zette. Per item: wat het is, en welk probleem of welke vorm je ermee kunt testen. Een voorstel voor een vaste set testvoertuigen staat in [test_pack.md](test_pack.md).

De geheugengroottes komen uit de RSC7-header van elk bestand (`tested`, gelezen op 20 okt 2026 met de flag-formule uit CodeWalker; zie [textures.md](textures.md)). "phys" is het grafische deel (textures), "virt" het systeemdeel (model, physics).

---

## TestVehicleFolder (363 MB, nu `archive/TestVehicleFolder/`)

Alle vier staan sinds 20 okt ook in `[Vehicles]` van de dev-server.

| Map | Type | Vorm | Wat het laat zien |
|-----|------|------|-------------------|
| `cle53amg/` | auto, **nog niet omgezet** | alleen `dlc.rpf` (307 MB = 293 MiB, RPF7, niet versleuteld) | Intake vanaf een GTA-mod: uitpakken en omzetten (zie [tool_functions.md](tool_functions.md), functie F-E1) |
| `kriegerty2/` | auto (`VC_SUPER`) | uitvoer van convert.cfx.rs: `common/` + `stream/`, 7 meta's | **Referentie "goed"** qua vorm. Kit `64378_kriegerty2_modkit`; `txdRelationships` naar vanilla `vehicles_fmj_interior`; een livery-onderdeel met een andere naam (`kriety2_liv1.yft`). Grootste bestand 4,4 MiB virt. Let op: `carcols` heeft een eigen licht-id 941, maar `carvariations` verwijst naar `lightSettings` 140 (testgeval voor M10) |
| `strman/` | auto (`VC_SPORT`), **escrow** | `data/` + `stream/`, `.fxap`, `dependency '/assetpacks'`, map `[Template]` met een livery-sjabloon | **Bekend probleemgeval "oversized".** `strman.ytd` is 1,9 MB op schijf maar **76 MiB phys**. `strman.yft` en `strman_hi.yft` zijn versleuteld (header `FXAP`); de `.ytd` niet. Ook een animatie (`va_str.ycd`). Het manifest noemt `data/carcols.meta`, maar **dat bestand ontbreekt** (testgeval voor R3/R4) |
| `zaccflatlit/` | trailer (`VC_UTILITY`) | `__resource.lua`, meta's in de root | Oud manifest, geen `common/`. `zaccflatlit.ytd` 32 MiB phys, `.yft` 14,2 MiB virt. Het manifest noemt `carcols.meta` en `vehiclelayouts.meta`, maar **die ontbreken** (testgeval voor R3/R4) |

## research/ (699 MB, nu `archive/research/`)

Volgens `research/README.md` alleen als kennisbron, niet voor productie. Afspraak uit dat bestand: per onderzoek een map met `README.md`, `source/`, `notes/` en `experiments/`, en in elke notitie minimaal de herkomst, het doel, wat bruikbaar is voor productie, en de risico's. De packs hier hebben (behalve DriveV) nog geen eigen README.

| Pack | Inhoud | Wat het laat zien |
|------|--------|-------------------|
| `0x63E74A4A/` | 10 vuilniswagen-varianten (`brickade*`) | Eigen layout (`vehiclelayouts_brickade_box.meta`, `LAYOUT_BRICKADE_BOX`); **zwaarste textures van alles**: `brickadeb.ytd` 4,9 MB op schijf, **224 MiB phys**; twaalf bestanden boven 16 MiB. Geen `carcols` in het manifest |
| `11john11_sapo_pack/` | 16 politievoertuigen (15 auto's, 1 heli) | Voertuigwapens (`WEAPONINFO_FILE`), twee eigen layouts, mod-onderdelen (`polstan_pbar.yft`), kits `1101`–`1105`; **vanilla-namen** in `stream/` (`vehicles_stanier_interior.ytd`); **map-bestanden** in een voertuig-pack (`sc1_19_*`) |
| `USSS/` | 19 auto's (Secret Service) | **Livery als apart model** (`halfback` + `halfback2`, enz.); **gedeelde handling**: zes modellen gebruiken `handlingId` `USSS`; wapens (minigun, rook) |
| `alamo/` | 1 auto (`umkscout`) | Eén auto met een **eigen sirene** (id 232 in `carcols`, gebruikt in `carvariations`). De kit `3995_scout_modkit` staat in `carcols`, maar `carvariations` verwijst naar `0_default_modkit`: een kit die niemand gebruikt |
| `lsfd/` | 8 brandweervoertuigen | Varianten als apart model (`lsfd` … `lsfd5`, `lsfdtruck` … `lsfdtruck3`); `lsfd3.ytd` 64 MiB phys |
| `extramuscle/` | 326 wielen (`.ydr`) | Wielen-pack: alleen `carcols.meta` met 163 `<Wheels>`-items |
| `vanillawheels/` | 337 wielen (`.ydr`) | Wielen-pack: 308 wielen in `carcols.meta` onder `<Wheels>`; de `contentunlocks.meta` is leeg |
| `DriveV/` | handling-overhaul, geen modellen | `meta/handling.meta` met **790** handlings en `meta/vehicles.meta` met 298 voertuigen, plus per DLC een map. Globs in het manifest; AI- en verkeersbestanden. **Let op: aangepaste waarden, niet vanilla.** Uit `research/DriveV/README.md`: realistischer rijgedrag per model, rijhoogte en overhellen echter, downforce alleen waar logisch, schade zwaarder. Niet overnemen: ENB, InversePower, trainer-eisen, de verkeers-overhaul en de pack-vorm met veel modellen per meta |
| `Custom Engine Sounds/` | 13 motorgeluiden (het manifest; de readme noemt er 11) | Audio-resource zonder voertuig, ook met `AUDIO_SYNTHDATA` (zie [audio.md](audio.md)) |

## VehicleTool/pack (gegenereerd, nu `archive/VehicleTool/pack/`)

Een pack dat VehicleTool maakte, met vier voertuigen uit `[vehicles_pack]` van Marks oude server (zie de tabel daaronder). VehicleTool zelf stond toen in `resources\[standalone]\VehicleEditor\`.

| Map in `data/` | Model | Type | Wat het laat zien |
|----------------|-------|------|-------------------|
| `BATIC` | `batic` | motor | 137 stream-bestanden: 18 liveries als `.yft`, ruim 100 mod-onderdelen; eigen audio (`batic_game.dat151.rel`, `batic.awc`) |
| `BELL505` | `bell505` | heli | Tweede texture-laag `bell505a.ytd`. In de bron hangt die via `txdRelationships` (keten `bell505` → `bell505a` → `vehicles_jet_interior`); **in de pack-versie is `txdRelationships` leeg**: de template nam hem niet over |
| `BUFFALOSX` | `lssdbuffalosx` | auto | `lssdbuffalosx.ytd` 28 MiB phys; **map heet naar de handling, het model heet anders** |
| `SCOUT2020` | `dnscoutun` | auto | `dnscoutun.ytd` 13 MiB phys; zelfde naamverschil |

Alle vier hebben kit-id `10000` (uit de template), dezelfde auto-handling (ook de motor en de heli), en een `dlctext.meta`/`shop_vehicle.meta` met een verkeerd root-element. Het manifest is ongeldige Lua. Zie [inventory.md](inventory.md). Niet gebruiken als voorbeeld van een goede resource; de `stream/`-bestanden (147) zijn wel bruikbaar.

## Elders: de resources uit de rapporten van maart

VehicleTool controleerde in maart 2026 tien resources die niet in deze map staan (van acht is er een rapport van de laatste versie; van `dc_mdbuffalo` en de Lore Friendly-pack alleen van een oudere). Ze stonden op de oude server, in `C:\server\txData\Qbox_ADC0AC.base\resources\[vehicles_pack]\`. Als die map er nog is, is dat goede testdata:

| Resource | Wat | Bijzonder |
|----------|-----|-----------|
| `2020umk` | `dnscoutun`, auto, Emergency | `__resource.lua`, meta's in de root, geen `dlctext`/`shop_vehicle` |
| `barybuffalosx` | `lssdbuffalosx`, auto, Emergency | geen `shop_vehicle` |
| `bell505` | heli | geen `carcols`; tweede `.ytd` via `txdRelationships` |
| `batic` | motor | meta's in `data/`; `vehicle_names.lua` met de namen; complete eigen audio |
| `pigeonp` | twee voertuigen (`lcpdpigeon`, `pigeonp`), auto, Emergency | `vehicles_pigeon_interior.ytd`, `_manifest.ymf` in `stream/` |
| `bike` | `pdbf400rb`, politiemotor (motor + Emergency) | `__resource.lua`; meta's in de root |
| `bow` | auto, Super | geen `carcols` |
| `dc_mdheli` | heli | meta's in `data/`; geen `carcols`, `dlctext`, `shop_vehicle` |
| `dc_mdbuffalo` | auto | alleen een rapport van een oudere versie |
| `Lore_Friendly_Car_Pack` | ±83 voertuigen | 83 audio-mappen (`dlc_*`, elk `<naam>.awc` + `<naam>_npc.awc`); `client.lua` en `server.lua` in de root; `paradox` en `paradox2` hebben kits 700 en 701 en een byte-gelijke `carcols.meta` (`CARCOLS_CARVARIATIONS_REFERENCE.md`; testgeval voor M14) |

## VehicleOptimizer/output (nu `archive/VehicleOptimizer/output/`)

- `onbekend/socharger/`: `socharger.ytd` 52 MiB phys, `socharger.yft` 23,6 MiB virt. "onbekend" is de categorie die de optimizer gaf.

## Downloads in `[Vehicles]` (21 okt 2026)

Mark zette op 20 okt downloads in `resources/[Vehicles]` van de dev-server. Gescand op 21 okt met `research/scripts/scan_vehicles.py` uit de repo: alleen lezen (manifest, meta's, `.lua`, en de eerste 16 bytes van elk resource-bestand). Alles hieronder is `tested` in de zin van "gelezen"; niets is in-game getest. De server was tijdens de scan nog aan het opstarten.

| Map | Wat | Voertuigen | Grootte | Laadt FiveM het? |
|-----|-----|-----------:|--------:|------------------|
| `FiveM-Civ-Car-Pack/` | Pack van PLOKMJNB (GitHub): `PLOKS_CARS`, één resource met echte merken, plus `VehicleSpawner` (C#-menu met drie `.dll`'s) en voorbeeldbestanden voor vMenu en een framework | 191 | 5,3 GB | **nee** |
| `FiveM-Lore-Friendly-Pack/` | Pack van SpiritsCreations (GitHub): `Lore_Friendly_Car_Pack` v1.2 met 41 motorgeluiden, en zes wielen-packs | 72 | 2,9 GB | **nee** |
| `lds-lorevehicles/` | Lore-friendly pack: één resource, met 29 geluids-resources in `[lorevehicles-sounds]/` | 98 | 1,7 GB | ja, maar de 29 geluids-resources niet |
| `kriegerty2/`, `strman/`, `zaccflatlit/` | kopieën uit `TestVehicleFolder` | 3 | 73 MB | ja |
| `cle53amg/` | kopie uit `TestVehicleFolder`: alleen `dlc.rpf` | – | 307 MB | nee |

Samen: 364 voertuigen, 16.431 bestanden, ruim 10 GB, 13.856 bestanden met een RSC7-header. Van twee voertuigen (`bolide` en `2020ss` in `PLOKS_CARS`) is de `vehicles.meta` kapot; de andere 362 konden we lezen: 356 auto's, 4 motoren, 1 amfibie-auto en 1 trailer. Ook acht `carcols.meta` waren niet te lezen, dus de aantallen voor voertuigen en kits hieronder zijn minimums.

**Waarom twee packs en `cle53amg` niet laden:** FiveM kijkt alleen in mappen met haken. `FiveM-Civ-Car-Pack` heeft geen haken en geen manifest, dus de server ziet hem als één resource zonder manifest en kijkt er niet in. Hetzelfde geldt voor de geluids-resources in `lds-lorevehicles`: een resource in een resource laadt nooit (`official`, broncode; zie [folder_structure.md](folder_structure.md) §5). `ensure [Vehicles]` start dus alleen `kriegerty2`, `lds-lorevehicles`, `strman` en `zaccflatlit`.

### Wat de scan vond

De ID's in de laatste kolom verwijzen naar [validation_rules.md](validation_rules.md) en [open_questions.md](open_questions.md). Of de game de meeste van deze dingen slikt, weten we niet: dat is precies wat het testpakket moet uitzoeken.

| Soort | Aantal | Voorbeeld | Regel / vraag |
|-------|-------:|-----------|---------------|
| **Laden en structuur** | | | |
| Pack-map zonder haken en zonder manifest | 2 (+ `cle53amg`) | `FiveM-Civ-Car-Pack/PLOKS_CARS` | R13 |
| Resource in een andere resource | 29 | `lds-lorevehicles/[lorevehicles-sounds]/zr250` | R13 |
| `__resource.lua` | 1 | `zaccflatlit` | R2, Q-S9 |
| Escrow | 1 | `strman` (`.fxap`, twee versleutelde `.yft`'s) | R9, T2 |
| `.rpf` | 2 | `cle53amg/dlc.rpf`; `PLOKS_CARS/stream/[ROLLSROYCE]/rculi/rculi_mods.rpf` (in `stream/`) | F9, Q-S14 |
| **Manifest** | | | |
| `data_file`-type niet in de officiële lijst | 5 types | `DLCTEXT_FILE`, `VEHICLE_SHOP_FILE` (`kriegerty2`), `CARCONTENTUNLOCKS_FILE` (lds), `VEHICLE_SETTINGS_FILE`, `CAR_ADDON_CONTENT_UNLOCKS` (Lore) | R14, Q-M15 |
| Elke meta onder negen types (`data_file 'HANDLING_FILE' 'data/**/*.meta'` enz.) | Lore-pack: 319 bestanden × 9 types; ook de zes wielen-packs | `Lore_Friendly_Car_Pack` | R6, Q-S13 |
| Bestand of script uit het manifest ontbreekt | 3 meta's, 1 script, 1 geluidsmap | `strman`, `zaccflatlit`; `versioncheck.lua` en `audio/sfx/dlc_bati901` (Lore) | R3, R4, A2 |
| Scripts met HTTP-versiecheck en `SetConvarServerInfo('tags', …)` | 2 | `server.lua` van `PLOKS_CARS` en `Lore_Friendly_Car_Pack` | R8, B6 |
| Mapnamen met spaties en `'` | 128 mappen | `data/[6STR]/6STR Benefactor Schwartzer 'Aggressor' Custom` | info: globs werken, losse paden in een Lua-string breken |
| **Meta-inhoud** | | | |
| XML die een strikte parser weigert | 13 bestanden | `--` in commentaar (`[BUGATTI]/bolide/vehicles.meta`); `<visibleMods>` dicht met `</linkMods>` (`[PORSCHE]/taycan/carcols.meta`); NUL-bytes aan het eind (lds `imperial/carvariations.meta`); drie spaties vóór `<?xml` (lds `gstghell1/carcols.meta`) | M1, Q-M16 |
| Voertuig in `vehicles.meta` zonder `.yft` | 11 | `aventador` in `[FORD]/raptor2017/vehicles.meta` | M4 |
| `handlingId` die nergens staat | 3 | `dodgesrt2`, `tofu` (PLOKS), `sultanrsv82` (Lore) | M6 |
| `handlingId` van een vanilla-voertuig | 14 | lds `surano3` (`SURANO`), PLOKS `sandero` (`BALLER`) | M28 (geen fout) |
| Voertuig zonder `carvariations` | 13 | PLOKS `sandero`; lds `imperial` (door de NUL-bytes) | Q-M9 |
| `vehicleClass` die niet bestaat | 4 | `VC_SPORTS` (PLOKS `stingray`), `VC_COMPACTS` (lds `castella`, `weevilup`) | M27, Q-M17 |
| Geen tekst voor `gameName` | 152 van de 362 gelezen | lds: 85 van 98; PLOKS `bmci` (`gameName` `m5`, en geen tekst voor `m5`) | M16, Q-M18 |
| `audioNameHash` die niet in de downloads staat en geen vanilla-voertuignaam is | 4 | lds `hellenstorm`, `zodiacr` | M12, Q-M13 |
| Kit-naam niet in de eigen `carcols` | 12 | `0_suv_modkit` (lds `yosemiteswb`), `0_default_no_lower` (Lore) | M8 |
| Zelfde `handlingName` of `modelName` twee keer in één pack | 4 + 2 | `180sx` 3× (PLOKS); `hachurac` (Lore) | X2, X3 |
| **Botsingen** | | | |
| Kit-id dubbel | minstens 44 id's, 29 tussen packs | `964`: `bmci` (PLOKS) en `callista` (Lore én lds); `926`: `q820` en `veneno` (beide PLOKS) | X4, B9, Q-S6 |
| Add-on definieert kits met een vanilla-naam | 2 kits + 5× `0_default_modkit` | `PLOKS_CARS/[FORD]/wildtrak/carcols.meta`: `268_hermes_modkit`, `269_revolter_modkit` | M21, Q-M19 |
| Licht-id of sirene-id dubbel | 29 + 2 | licht `998` 13× in PLOKS | X4 |
| Zelfde stream-naam in één pack, andere inhoud | 7 (PLOKS), 5 (Lore) | `spoiler_2.yft` van `bmci`, `f430s` en `gs350` | X7, Q-S6 |
| Zelfde stream-naam tussen packs | 1.474 (1.395 met dezelfde grootte) | bijna alles tussen Lore en lds | X1 |
| Zelfde voertuig in twee packs | 20 modellen | `ariant`, `zr250`, `mf1` (Lore én lds) | X2 |
| Vervangt een vanilla-voertuig | 2 | lds `euros`, Lore `futo2` | X5, Q-T6 |
| Meerdere `_manifest.ymf` in één resource | 6 (Lore) | | X7, Q-S11 |
| **Grootte** (per bestand, de grenzen van FiveM) | | | |
| Boven 16 MiB | 1.352 van 13.856 | 1.197 `.yft` (textures in het model), 151 `.ytd`, 4 `.ydr`; 1.184 door phys, 168 door virt | T1 |
| Boven 32 MiB | 97 | | T1 |
| Boven 48 MiB ("WILL lead to streaming issues") | 65 | | T1 |
| Boven 64 MiB | 26 | `ns350.ytd` 240 MiB (12 MB op schijf); `i8.ytd` 128 MiB uit 1,5 MB op schijf; lds `ingotc_interiormod.yft` 128 MiB uit 1,7 MB | T1 |

Per pack boven 16 MiB: `PLOKS_CARS` 481 (24 boven 64 MiB), `lds-lorevehicles` 469 (1 boven 64), `Lore_Friendly_Car_Pack` 400 (geen boven 64), `strman` 1 (76 MiB), `zaccflatlit` 1.

**Liveries:** minstens 95 kits met `VMT_LIVERY_MOD` (soort 2), tot 71 per kit (`rh4_modkit` in de Lore-pack). Geen enkel voertuig gebruikt `<liveries>` in `carvariations` (soort 1).

**Handling** (356 handlings, voor Q-H4): `fMass` 230–4.750 (90% tussen 900 en 2.700), `fInitialDriveForce` 0–4,79 (90% tussen 0,20 en 0,525), `fInitialDriveMaxFlatVel` 98–380 (130–257), `nInitialDriveGears` 1–10 (4–7), `fBrakeForce` 0,2–14,7 (0,315–1,5), `fTractionCurveMax` 0,8–7,65 (1,7–2,88). De uitschieters zijn goede testgevallen voor de grenzen in de editor ([handling.md](handling.md)).

---

## Welke test bij welk voorbeeld

| Vraag | Beste voorbeeld |
|-------|-----------------|
| Wanneer meldt FiveM "oversized" (Q-T1) | `strman` (76 MiB), `0x63E74A4A` (tot 224 MiB), `kriegerty2` (geen) als controle |
| Wat gebeurt er in-game met een te grote texture (Q-T2) | `0x63E74A4A` |
| Minimale meta-set (Q-S8) | `alamo` (één auto) |
| Bestanden die het manifest noemt maar die ontbreken (R3/R4) | `strman`, `zaccflatlit` |
| Verwijzing naar een licht- of sirene-id (M10) | `kriegerty2` (licht 140 staat niet in de eigen `carcols`), `alamo` (sirene 232 klopt) |
| Kit die niemand gebruikt | `alamo` |
| Pack splitsen, gedeelde handling (B2) | `USSS` |
| Liveries soort 1, 2 en 4 ([folder_structure.md](folder_structure.md#2-liveries-vier-manieren-en-wat-dat-voor-de-mappen-betekent)) | `strman`, `BATIC`, `lsfd` |
| Escrow herkennen (Q-T7) | `strman` |
| Intake vanaf `.rpf` (Q-A3) | `cle53amg` |
| Oud manifest omzetten | `zaccflatlit` |
| Vanilla-namen in `stream/` (Q-T6) | `11john11_sapo_pack`; lds `euros`, Lore `futo2` (hele voertuigen) |
| Resource die FiveM niet vindt (R13) | `FiveM-Civ-Car-Pack` zoals gedownload; de geluids-resources in `lds-lorevehicles` |
| XML die een strikte parser weigert (Q-M16) | `[BUGATTI]/bolide`, `[PORSCHE]/taycan` (PLOKS); `imperial`, `gstghell1` (lds) |
| Kit-id-botsingen en kits met een vanilla-naam (Q-S6, Q-M19) | `bmci` + `callista`; `wildtrak` (PLOKS) |
| Alle grenzen van de oversized-melding (Q-T1) | `cutlass` (26 MiB), `rhinetaxi` (40), `nissantitan17` (52), `i8` (128) |

## Checklist in-game (uit `PACK_VALIDATION.md` en `TEST_PLAN.md`)

Voor elk voertuig dat we testen op de dev-server:

- [ ] De resource start zonder fouten in de console; spawn elk voertuig op `modelName`.
- [ ] Liveries: verschijnen ze allemaal in het mod-menu (bij veel kits, zoals BATIC)? Zo niet: `carcols` en `carvariations` nalopen.
- [ ] Een tweede `.ytd` (zoals `bell505a.ytd`): is het een texture-laag via `txdRelationships`, of zitten er livery-varianten in? (`PACK_VALIDATION.md` vermoedde het laatste.)
- [ ] Geen tweede resource die dezelfde stream-namen laadt.

## Wat ontbreekt

- Een **boot** en een **vliegtuig** als echte resource (het vliegtuig in VehicleOptimizer is alleen een template).
- Een voertuig met **livery2** (dak-livery).
- Een **vanilla** `handling.meta` als ijkpunt voor "normale" waarden (DriveV is aangepast). Zie Q-H4.

Mark kan zulke voertuigen op de dev-server zetten; zie de takenlijst in [open_questions.md](open_questions.md).
