# Testpakket

**Gebouwd op 21 okt 2026** (B25): `resources/[vehicletests]/` op de dev-server, 55 gevallen, samen ongeveer 670 MB (640 MiB). Gemaakt met [`research/scripts/build_testpack.py`](../research/scripts/README.md) uit de downloads in `[Vehicles]`. `ensure [Vehicles]` staat sinds 21 okt uit in `server.cfg` (back-up: `server.cfg.bak-2026-10-21-vehicletests`), en de vijf packs zijn gestopt.

Dit document zegt **wat we nodig hebben** voor alles wat de tool moet kunnen, **welke gevallen** dat zijn, **wat we in de game zagen**, en hoe het pakket is opgebouwd. De voertuigen komen uit de scan van de downloads ([test_data.md](test_data.md#downloads-in-vehicles-21-okt-2026)).

---

## Wat we nodig hebben

Per onderdeel van de tool, in Marks volgorde (B12): wat we willen testen, en welk geval daarvoor is.

- ✓ = in het pakket (het geval, en waar het voertuig vandaan komt)
- **archief** = hebben we, in `archive/` van de projectmap; nog niet in het pakket
- **later** = gemaakt geval dat nog gebouwd moet worden
- **zoeken** = hebben we nog niet

### 0. Schone voertuigen, één per type

Nodig voor de templates per type (Q-M12, Q-S8) en als "goed"-referentie.

| Type | Waarom | Geval |
|------|--------|-------|
| Auto | basis voor bijna alle gemaakte gevallen | ✓ `vt_00` (`tltypes`, PLOKS) |
| Motor | eigen handling-klasse (`CBikeHandlingData`) en layout | ✓ `vt_80` (`bati901`, Lore, schoon gemaakt: geluid van de vanilla Bati) |
| Trailer | geen motor, andere velden | ✓ `vt_81` (`zaccflatlit`, schoon gemaakt: nieuw manifest) |
| Heli | `CFlyingHandlingData`, andere meta-velden | **archief**: `sheriffmav` (`11john11_sapo_pack`) |
| Vliegtuig | idem | **zoeken** |
| Boot | `CBoatHandlingData` | **zoeken** |
| Hulpdienst | sirene en lichten met eigen id's | **archief**: `umkscout` (`alamo`), eigen sirene 232 |

### 1. Structuur, templates en meta's

| Wat we willen testen | Geval |
|----------------------|-------|
| De gekozen indeling (B24) | ✓ `vt_00` (auto), ✓ `vt_13` (onderdelen en liveries in submappen van `stream/`) |
| Minimale set per type (Q-S8) | ✓ `vt_60`, `vt_61`, `vt_62` (zonder `carvariations`, `carcols`, `vehiclelayouts`). `dlctext` en `shop_vehicle` horen niet in de indeling van B24, dus `vt_00` is al "zonder"; `vt_63` test juist "met `dlctext`" |
| Ontbrekende velden (Q-M14) | ✓ `vt_65` (`audioNameHash`); een lege `<audioNameHash />` zit in `vt_14`; `layout` **later** |
| Kapotte XML (Q-M16) | ✓ `vt_02` (`--` in commentaar), `vt_03` (tag die niet dichtgaat), `vt_04` (NUL-bytes), `vt_05` (spaties voor `<?xml`), `vt_66` (BOM), `vt_67` (losse `&`). `taycan` (verkeerde sluit-tag) niet opgenomen: lijkt op `vt_03` |
| Koppelingen (M4–M10) | model zonder `.yft` ✓ `vt_06` · `txdName` zonder `.ytd` ✓ `vt_68` · `handlingId` die niet bestaat ✓ `vt_79` · `handlingId` van vanilla ✓ `vt_11`, `vt_07` · kit die nergens staat ✓ `vt_12` · licht-id die niet bestaat ✓ `vt_20` (licht 140) |
| Ongeldige waarden | `vehicleClass` die niet bestaat ✓ `vt_08` · type en klasse die niet passen ✓ `vt_70` · layout die niet bestaat ✓ `vt_69` |
| Naam (Q-M18, B26) | geen tekst ✓ `vt_09` · naam uit het manifest ✓ elk geval met `vehicle_label` (zo krijgen ook de Lore-voertuigen hun naam, die de pack met `AddTextEntryByHash` zette) · naam via `AddTextEntryByHash` in een script: **later** (`vt_71`) |
| Liveries | soort 1 (in de `.ytd`) **zoeken** · soort 2 (mod-onderdeel) ✓ `vt_13` · soort 3 (livery2) **zoeken** · soort 4 (apart model) **archief** (`lsfd`) |
| Geluid | eigen geluid in de resource ✓ `vt_32b` (`vorstand`) · geluid uit een andere resource ✓ `vt_01` + `vt_01b` · geluids-resource in een resource ✓ `vt_01` · ontbrekende geluidsmap ✓ `vt_14` |
| Pack splitsen (B2) | **archief** (`USSS`, gedeelde handling) en de packs in `[Vehicles]`; hoort bij de intake (later) |

### 2. Manifest

| Wat we willen testen | Geval |
|----------------------|-------|
| Onbekende `data_file`-types (Q-M15) | ✓ `vt_20` (`kriegerty2`), `vt_63` |
| Elke meta onder elk type (Q-S13) | ✓ `vt_21` (`buffaloh`, met het manifest van de Lore-pack) |
| Oud manifest en ontbrekende bestanden (Q-S9) | ✓ `vt_22` (`zaccflatlit`) |
| Escrow (Q-T7) | ✓ `vt_45` (`strman`) |
| Meta niet in `files {}` (R15) · hoofdletters in een glob (R16) · `*` in een mapnaam · `stream/` niet in de root (F10) | ✓ `vt_73`, `vt_74`, `vt_75`, `vt_76` |
| Resource in een resource (R13) | ✓ `vt_01` |

### 3. Botsingen (twee resources tegelijk)

| Wat we willen testen | Geval |
|----------------------|-------|
| Zelfde kit-id | ✓ `vt_30a` (`rcf`, PLOKS) + `vt_30b` (`dubstag`, lds): allebei 689 |
| Zelfde stream-naam, andere inhoud | ✓ `vt_31a` (`f430s`) + `vt_31b` (`gs350`), PLOKS |
| Zelfde voertuig twee keer | ✓ `vt_32a` (`vorstand`, lds) + `vt_32b` (`vorstand`, Lore) |
| Vervangt een vanilla-voertuig | ✓ `vt_33` (`futo2`, Lore) |
| Kit met een vanilla-naam | ✓ `vt_34` (`wildtrak`, PLOKS) |
| Kit-id gelijk aan dat van een vanilla-kit | nieuw (21 okt): zie [Uitkomsten](#uitkomsten), `vt_13` en `vt_13b` |
| Zelfde bestandsnaam in twee submappen van één resource (X7) | **later** (`vt_77`) |

### 4. Textures

| Wat we willen testen | Geval |
|----------------------|-------|
| Elke grens van de melding: 16, 32, 48 en 64 MiB | ✓ `vt_40` (`cutlass.ytd`, 26 MiB), `vt_41` (`rhinetaxi.ytd`, 40), `vt_42` (`nissantitan17.ytd`, 52), `vt_43` (`i8.ytd`, 128) |
| Textures in het model (`.yft`) | ✓ `vt_44` (`ingotc_interiormod.yft`, 128 MiB) |
| Een `.ytd` om te verkleinen (Q-T4) | ✓ `vt_43`: `i8.ytd` is 1,5 MB op schijf en 128 MiB in het geheugen |
| `txdRelationships` | ✓ `vt_00` (`vehicles_schaf_interior` → `tltypes`), `vt_20` |
| `.rpf` in `stream/` (Q-S14) | ✓ `vt_46` (`rculi`) |

### 5. Handling-editor

| Wat we willen testen | Geval |
|----------------------|-------|
| "Normaal" per klasse (Q-H4) | vanilla-voertuigen: geen add-on nodig, spawnen en uitlezen |
| Uitschieters | ✓ `vt_50` (`720s`, 10 versnellingen), `vt_51` (`ruiner6str`) en `vt_33` (`futo2`), allebei kracht 4,79; `teslax` (1 versnelling) **later** |
| Niet-auto's | ✓ `vt_80` (motor); heli, boot en vliegtuig uit 0 |
| Gedeelde handling | **archief** (`USSS`, zes modellen op één `handlingId`) |

### 6. Intake (later)

| Wat we willen testen | Bron |
|----------------------|------|
| `dlc.rpf` uitpakken en omzetten (Q-A3) | `cle53amg` (in `[Vehicles]`) |

### Nog te zoeken

- een **vliegtuig** en een **boot**: echte add-ons met een model;
- een voertuig met **liveries in de `.ytd`** (soort 1, met `<liveries>` in `carvariations`), vaak politie of brandweer;
- een voertuig met **livery2** (dak-livery, soort 3).

---

## De gevallen

Een geval uit de downloads krijgt de gekozen indeling (B24), behalve als het juist over de vorm gaat (`vt_20`, `vt_21`, `vt_22`, `vt_45`, en de geneste geluids-resource in `vt_01`). De bestanden zelf zijn byte voor byte gelijk aan de download. MB = miljoen bytes.

Een voertuig neemt de modellen mee die in dezelfde `vehicles.meta` staan: `vt_04` bevat ook `imperialpas` en `imperialev`, `vt_06` ook `accolade2`, en `vt_10` ook `nsandstorm` en `nsandstorm2`.

Bijvangst die niet bij elk geval staat: de meeste voertuigen uit `lds-lorevehicles` hebben geen tekst voor `gameName` (M16).

### Structuur, templates en meta's

| Geval | Voertuig (bron) | MB | Probleem | Vraag / controle |
|-------|-----------------|---:|----------|------------------|
| `vt_00_baseline` | `tltypes` (PLOKS) | 7,8 | geen: de scan vindt niets, niets boven 16 MiB | referentie; basis voor de gemaakte gevallen |
| `vt_01_nested_resource` | `zionks` (lds), met zijn geluids-resource in `[sounds]/zionks/` | 10,1 | een resource in een resource laadt niet; dan ontbreekt het eigen geluid | R13 |
| `vt_01b_zionks_sounds` | de geluids-resource van `zionks` (lds), los | 3,3 | geen: start na `vt_01`, dan hoort het geluid er te zijn | R13 |
| `vt_02_xml_comment` | `bolide` (PLOKS) | 13,4 | `<!------…---->` in `vehicles.meta` | Q-M16, M1 |
| `vt_03_xml_wrong_close` | `84rx7k` (PLOKS) | 18,5 | `carcols.meta`: `<Kits>` gaat nooit dicht, en de kit staat binnen `<Lights>` | Q-M16, M1 |
| `vt_04_xml_nul_bytes` | `imperial` (lds) | 25,9 | twee NUL-bytes aan het eind van `carvariations.meta` | Q-M16, M1 |
| `vt_05_xml_space_before_decl` | `gstghell1` (lds) | 6,0 | drie spaties voor `<?xml` in `carcols.meta` (bijvangst: het eigen geluid zit in een geneste resource van lds) | Q-M16, M1 |
| `vt_06_model_without_yft` | `accolade` (lds) | 4,8 | `vehicles.meta` noemt ook `accolade2`, maar daar is geen `.yft` voor | M4 |
| `vt_07_no_carvariations` | `sandero` (PLOKS) | 8,6 | alleen `vehicles.meta`: geen `carvariations`, `carcols` of `handling` (handling van de vanilla `Baller`) | Q-M9 |
| `vt_08_invalid_class` | `stingray` (PLOKS) | 31,1 | `vehicleClass` `VC_SPORTS` bestaat niet; `gameName` met een spatie (`Corvette C8`) | Q-M17, M27 |
| `vt_09_no_label` | `blistacr` (lds) | 2,3 | geen tekst voor `gameName` | Q-M18, M16 |
| `vt_10_unknown_audio` | `hellenstorm` (lds) | 43,9 | `audioNameHash` `hellenstorm` staat niet in de downloads en is geen vanilla-voertuignaam | M12 |
| `vt_11_vanilla_handling` | `surano3` (lds) | 5,3 | `handlingId` `SURANO` (vanilla): mag, verwacht geen fout | M28 |
| `vt_12_kit_not_defined` | `yosemiteswb` (lds) | 2,8 | `carvariations` noemt `0_suv_modkit`; er is geen eigen `carcols.meta` (of de kit in vanilla bestaat: Q-M19) | M8 |
| `vt_13_livery_mods` | `atlas` (lds) | 6,2 | geen echt probleem: 16 liveries als mod-onderdeel (soort 2), in `stream/liveries/` | M22, Q-S4 |
| `vt_14_missing_wavepack` | `bati901` (Lore) | 11,1 | het manifest noemt `audio/sfx/dlc_bati901`, maar die map bestaat niet; lege `<audioNameHash />` | R4, M12 |

### Manifest

| Geval | Voertuig (bron) | MB | Probleem | Vraag / controle |
|-------|-----------------|---:|----------|------------------|
| `vt_20_unknown_types` | `kriegerty2`, ongewijzigd | 6,7 | `DLCTEXT_FILE` en `VEHICLE_SHOP_FILE` staan niet in de officiële lijst | Q-M15, R14 |
| `vt_21_all_types_glob` | `buffaloh` (Lore), met de mappen en het manifest van de Lore-pack | 5,6 | elke meta onder tien types, waarvan twee onofficieel | Q-S13, R6 |
| `vt_22_old_manifest` | `zaccflatlit`, ongewijzigd | 18,3 | `__resource.lua`, en twee meta's uit het manifest ontbreken | Q-S9, R2, R4 |

### Botsingen (paren: twee resources tegelijk)

| Geval | Voertuig (bron) | MB | Probleem | Vraag / controle |
|-------|-----------------|---:|----------|------------------|
| `vt_30a_kit_id_rcf` + `vt_30b_kit_id_dubstag` | `rcf` (PLOKS) + `dubstag` (lds) | 19,5 + 4,6 | allebei kit-id 689 | Q-S6, X4 |
| `vt_31a_stream_name_f430s` + `vt_31b_stream_name_gs350` | `f430s` + `gs350` (PLOKS) | 17,9 + 14,5 | allebei `spoiler_2.yft` en `spoiler_3.yft`, met andere inhoud | Q-S6, X1 |
| `vt_32a_vorstand_lds` + `vt_32b_vorstand_lore` | `vorstand` uit lds en uit Lore | 11,1 + 14,1 | zelfde model, stream-namen en kit-id 701 | X1, X2, X4 |
| `vt_33_vanilla_vehicle` | `futo2` (Lore) | 6,6 | vervangt de vanilla Futo GTX (bijvangst: `fInitialDriveForce` 4,79) | X5, Q-T6 |
| `vt_34_vanilla_kit` | `wildtrak` (PLOKS) | 26,2 | definieert kits met de naam van vanilla-voertuigen: `268_hermes_modkit` en `269_revolter_modkit` | Q-M19, M21 |

### Textures

| Geval | Voertuig (bron) | MB | Probleem | Vraag / controle |
|-------|-----------------|---:|----------|------------------|
| `vt_40_over_16` | `cutlass` (PLOKS) | 7,7 | `cutlass.ytd`: 26 MiB, blauwe melding | Q-T1, T1 |
| `vt_41_over_32` | `rhinetaxi` (lds) | 6,8 | `rhinetaxi.ytd`: 40 MiB, gele melding (bijvangst: `gameName` `taxi`) | Q-T1, T1 |
| `vt_42_over_48` | `nissantitan17` (PLOKS) | 20,8 | `nissantitan17.ytd`: 52 MiB, gele melding met "WILL lead to streaming issues" | Q-T1, Q-T2, T1 |
| `vt_43_over_64_ytd` | `i8` (PLOKS) | 16,8 | `i8.ytd`: 128 MiB uit 1,5 MB op schijf | Q-T1, Q-T2, Q-T4 |
| `vt_44_yft_with_textures` | `ingotc` (lds) | 5,4 | `ingotc_interiormod.yft`: 128 MiB phys, textures in het model | Q-T1, T1 |
| `vt_45_escrow` | `strman`, ongewijzigd | 47,7 | escrow; `strman.ytd` 76 MiB; `carcols.meta` uit het manifest ontbreekt | Q-T7, R9, T2 |
| `vt_46_rpf_in_stream` | `rculi` (PLOKS) | 37,9 | `rculi_mods.rpf` in `stream/` | Q-S14, F9 |

### Handling

| Geval | Voertuig (bron) | MB | Probleem | Vraag / controle |
|-------|-----------------|---:|----------|------------------|
| `vt_50_ten_gears` | `720s` (PLOKS) | 13,1 | `nInitialDriveGears` 10 | Q-H14 |
| `vt_51_extreme_force` | `ruiner6str` (Lore) | 7,5 | `fInitialDriveForce` 4,79 (90% van de downloads zit tussen 0,20 en 0,525) | Q-H4, Q-H5, M19 |

### Gemaakt: expres één fout erin

Een gemaakt geval is een kopie van een schoon voertuig (meestal `vt_00`, uit `tltypes`) waarin we **precies één** ding veranderen. Zo weten we zeker welke fout welk gevolg heeft; gevallen uit de downloads hebben vaak meer dan één probleem tegelijk. Mark vindt dat prima, en "zelfs verstandig" (21 okt).

De gemaakte gevallen van `vt_00` gebruiken dezelfde model- en bestandsnamen, en kit-id 948: er draait er steeds één tegelijk, en niet samen met `vt_00` of `vt_13b`. Elk is 7,7 tot 7,8 MB.

| Geval | De wijziging | Vraag / controle |
|-------|--------------|------------------|
| `vt_60_no_carvariations` | `data/carvariations.meta` weg | Q-S8, Q-M9 |
| `vt_61_no_carcols` | `data/carcols.meta` weg (de kit `948_tltypes_modkit` en licht 948 vallen weg) | Q-S8 |
| `vt_62_no_layouts` | `data/vehiclelayouts.meta` weg | Q-S8 |
| `vt_63_with_dlctext` | `dlctext.meta` uit de bron erbij, als `DLCTEXT_FILE` | Q-M2, Q-M15 |
| `vt_65_no_audioname` | `<audioNameHash>` weg uit `vehicles.meta` | Q-M14 |
| `vt_66_xml_bom` | een UTF-8-BOM voor `vehicles.meta` | Q-M16, M1 |
| `vt_67_xml_ampersand` | `vehicleMakeName` `Acura&Co` (een losse `&`) | Q-M16, M1 |
| `vt_68_txd_missing` | `txdName` `tltypes_bestaatniet` | M5 |
| `vt_69_bad_layout` | `layout` `LAYOUT_BESTAATNIET` | M11 |
| `vt_70_class_mismatch` | `vehicleClass` `VC_MOTORCYCLE` bij een auto | M17 |
| `vt_73_meta_not_in_files` | geen `files {}` in het manifest | R15 |
| `vt_74_glob_case` | `data_file 'VEHICLE_METADATA_FILE' 'data/**/Vehicles.meta'`; het bestand heet `vehicles.meta` | R16 |
| `vt_75_glob_star_folder` | meta's in `data/x/`, `files { 'data/x/*.meta' }`, maar `data_file` met `data/*/<type>.meta` | Q-S3 |
| `vt_76_stream_not_root` | `stream/` verplaatst naar `assets/stream/` | F10 |
| `vt_79_handling_missing` | `handlingId` `TLTYPES_BESTAATNIET` | M6 |
| `vt_80_clean_bike` | `bati901` (Lore) zonder het eigen geluid; de lege `<audioNameHash />` wordt `BATI` | referentie motor |
| `vt_81_clean_trailer` | `zaccflatlit` met een nieuw manifest: alleen de meta's die bestaan | referentie trailer |

Twee gemaakte varianten van `vt_13` (atlas uit lds, 6,2 MB), voor de kit-proef:

| Geval | De wijziging | Vraag / controle |
|-------|--------------|------------------|
| `vt_13b_atlas_kit_948` | kit-id 948 in plaats van 620 | waarom `vt_13` geen kit heeft |
| `vt_13c_atlas_kit_1500` | kit-id 1500 in plaats van 620 | Q-M4: werkt een kit-id boven 1023 |

**Nog te bouwen:**

| Geval | De wijziging | Vraag / controle |
|-------|--------------|------------------|
| `vt_71` | naam via `AddTextEntryByHash` in een script | Q-M18 |
| `vt_77` | twee bestanden met dezelfde naam in `stream/mods/` en `stream/liveries/` | X7 |
| `vt_78` | kit-id boven 65.535 | Q-M4 |
| `layout` weg | `<layout>` uit `vehicles.meta` | Q-M14 |

Vervallen: `vt_64` ("zonder `shop_vehicle`": `vt_00` heeft er geen) en `vt_72` ("naam uit het manifest": dat doet nu elk geval, B26).

---

## Uitkomsten

In de game op de dev-server, met Mark ingelogd, via dolu, op 21 okt 2026 tussen 03:50 en 04:20. Game-build 3889. Werkwijze: het geval starten, de serverlog lezen, het model laden en het voertuig spawnen, uitlezen, verwijderen, het geval stoppen. Spawnen gaat één voertuig tegelijk, met een `DoesEntityExist`-check en een `Wait` ertussen (tip van Mark, nadat een reeks van 60 voertuigen in één keer de bridge liet hangen).

**Belangrijk voor elke test met kits:** de client onthoudt per model de eerste koppeling aan een kit, ook nadat de resource gestopt is. Een latere resource met hetzelfde model verandert die koppeling niet; pas opnieuw verbinden maakt de client schoon (zie Q-S15). Test een kit dus altijd in een schone sessie, of met een model dat in die sessie nog niet geladen is. Hetzelfde geldt waarschijnlijk voor de editor straks: na een wijziging in `carcols` of `carvariations` opnieuw verbinden.

| Geval | Wat we zagen | Wat het betekent | Label |
|-------|--------------|------------------|-------|
| alle | Na `refresh` vond de server alle gevallen, zonder melding over `[vehicletests]`. `vt_01_nested_resource/[sounds]/zionks/` staat niet in de lijst van resources; `vt_01b_zionks_sounds` wel | R13 (serverkant) | `tested` |
| `vt_00_baseline` | Eerste sessie: start zonder melding, model laadt in 0,2 s, spawnt met textures. Klasse 1 (`VC_SEDAN`), 4 stoelen. Handling uit het bestand (`fMass` 1700, 6 versnellingen, `fInitialDriveForce` 0,31). De kit werkt: motor (4), remmen (3), versnellingsbak (3), claxon (46), vering (4), pantser (5). Naam: eerst "NULL", na `AddTextEntry` met de waarde uit `vehicle_label` "Acura TL Type-S". Na `stop` is het model weg | de indeling van B24 werkt; B26 (b) werkt | `tested` |
| `vt_13_livery_mods` | Atlas spawnt (klasse 12, Vans), maar zonder kit (`GetNumModKits` 0, `GetVehicleModKit` 65535) | id 620 is ook het id van de vanilla-kit `620_gt750_modkit` | `tested` |
| `vt_13b_atlas_kit_948` | Met id 948: wel een kit, 16 liveries (mod 48). Livery 5 is zichtbaar op de auto (strepen op de zijkant; zonder livery niet) | een kit-id dat vanilla gebruikt, werkt niet (M21); liveries uit `stream/liveries/` werken (Q-S4) | `tested` |
| `vt_13c_atlas_kit_1500` | In een schone sessie: kit en 16 liveries | een kit-id boven 1023 werkt (Q-M4) | `tested` |
| `vt_13` na `vt_13c` | Zelfde sessie, eerst `vt_13c` (1500), dan `vt_13` (620): atlas heeft nu wél een kit, met dezelfde index als bij `vt_13c` | de eerste koppeling blijft (Q-S15) | `tested` |
| `vt_00` na `vt_61` | Zelfde sessie, eerst `vt_61` (zonder `carcols`), dan `vt_00`: geen kit | idem | `tested` |
| `vt_11_vanilla_handling` | Kit met alle 11 onderdelen uit `stream/mods/` in het mod-menu (5 motorkappen, uitlaat, skirt, 1 voor- en 2 achterbumpers, grille); de nieuwe voorbumper is zichtbaar op de auto. `fMass` 1600 (handling van de vanilla Surano) | onderdelen uit `stream/mods/` werken (Q-S4) | `tested` |
| `vt_02_xml_comment` | `<!------…---->` in `vehicles.meta`: het voertuig bestaat (klasse 7), kit, kleuren en handling laden. Server: alleen de melding dat `bolide.ytd` 24 MiB gebruikt | de game slikt `--` in een commentaar (Q-M16) | `tested` |
| `vt_03_xml_wrong_close` | `<Kits>` gaat nooit dicht: het voertuig werkt (klasse 5) met de kit uit `carvariations` (`0_default_modkit`). De vanilla Hotring houdt zijn kit en 31 liveries, ook nadat het geval stopte | of de rest van die `carcols` laadt, weten we niet (die kit wordt niet gebruikt) | `tested` (wat we zagen) |
| `vt_04_xml_nul_bytes` | NUL-bytes aan het eind van `carvariations.meta`: alle drie de modellen hebben hun kit, liveries (19, 8 en 13) en kleuren | de game slikt het (Q-M16) | `tested` |
| `vt_05_xml_space_before_decl` | Spaties voor `<?xml` in `carcols.meta`: kit, 10 liveries en onderdelen laden | de game slikt het (Q-M16) | `tested` |
| `vt_66_xml_bom` | BOM voor `vehicles.meta`: het voertuig bestaat (klasse, merk, handling kloppen). De kit ontbrak; vermoedelijk omdat `vt_13b` in dezelfde sessie al een kit met id 948 had (Q-S15), want de kit komt niet uit `vehicles.meta`. Nog eens testen in een schone sessie | de game slikt een BOM (Q-M16) | `tested` (BOM); kit: `aanname` |
| `vt_67_xml_ampersand` | Losse `&` in `vehicleMakeName`: het voertuig laadt, maar het merk heet `Acura?o` in plaats van `Acura&Co` | de game slikt het, maar de tekst raakt beschadigd (M1) | `tested` |
| `vt_61_no_carcols` | Zonder `carcols.meta`: het voertuig werkt, met de kleuren uit `carvariations`, maar zonder kit (geen tuning) | Q-S8 | `tested` |
| `vt_73_meta_not_in_files` | Zonder `files {}`: het voertuig bestaat niet (`IsModelInCdimage` nee). De server meldt niets | R15 | `tested` |
| `vt_74_glob_case` | `data/**/Vehicles.meta` vindt `vehicles.meta` niet: geen voertuig, geen melding | R16: hoofdlettergevoelig, ook op Windows | `tested` |
| `vt_75_glob_star_folder` | `data/*/vehicles.meta` vindt niets: geen voertuig, geen melding | Q-S3: een `*` in een mapnaam werkt niet | `tested` |
| `vt_76_stream_not_root` | Met `assets/stream/`: de meta's laden (het model "bestaat", merk Acura), maar het model laadt nooit (na 6 s nog niet). Geen melding | F10 | `tested` |
| vanilla na het stoppen van de packs | Eerste sessie: na het stoppen van de vijf packs hadden `calico`, `tailgater2` en `futo2` geen kit meer. Na opnieuw verbinden wel weer (kit-index 431, 424, 421). Stoppen en starten van `vt_03` en `vt_13` (die een vanilla-id gebruiken) raakte de vanilla-kits niet. Alleen `futo2` stond in een pack (Lore); `calico` en `tailgater2` noemt geen enkele pack | oorzaak open (Q-S15) | `tested` (wat we zagen) |

Fout in mijn eigen test, niet in het pakket: `IsModelInCdimage` op de livery-onderdelen (`atlas_liv1` …) zegt niets, want onderdelen van een kit zijn geen losse modellen. En `GetVehicleModKit` geeft de plek van de kit in de lijst van de client (de index), niet het kit-id: de eerste kit van een add-on kreeg steeds 610.

Nog niet getest: `vt_01`/`vt_01b` en `vt_10`, `vt_14`, `vt_32b`, `vt_65`, `vt_80` (geluid: iemand moet luisteren), de paren `vt_30` t/m `vt_32`, `vt_06` t/m `vt_09`, `vt_12`, `vt_20` t/m `vt_22`, `vt_33`, `vt_34`, de textures (`vt_40` t/m `vt_46`), de handling (`vt_50`, `vt_51`, `vt_79`) en `vt_60`, `vt_62`, `vt_63`, `vt_68` t/m `vt_70`, `vt_81`.

---

## Opbouw

```text
resources/
  [vehicletests]/                 -- niet in server.cfg; elk geval los starten
    README.md                     -- overzicht van alle gevallen
    vt_00_baseline/               -- één geval = één resource, in de indeling van B24
      fxmanifest.lua              -- met vehicle_label (B26) als de bron een naam heeft
      README.md                   -- het geval: zie hieronder
      sources.json                -- per bestand: herkomst, grootte en md5
      data/ …
      stream/ …
    vt_02_xml_comment/
    …
```

De `README.md` van elk geval:

- **Probleem:** wat er mis is.
- **Bron:** pack en map, en de maker volgens het manifest (of: "gemaakt uit `vt_00`").
- **Verwacht van de tool:** welke controle afgaat (bijv. M1).
- **Vraag:** welke open vraag het beantwoordt (bijv. Q-M16).
- **In-game kijken:** wat je in de game controleert.
- **Uitkomst:** na de test, met datum en het label `tested`.
- **Wat er in deze map staat:** uit welke mappen van de bron, welke modellen, hoeveel bestanden in `stream/`, `mods/` en `liveries/`, wat niet is meegenomen, en waar de naam vandaan komt.

Opnieuw maken (op de computer met de server; `<scan-map>` bevat de `units_*.json` van `scan_vehicles.py`):

```text
python3 -I build_testpack.py <resources-map> <scan-map> plan  all      -- laat zien wat er gekopieerd wordt
python3 -I build_testpack.py <resources-map> <scan-map> build vt_0     -- bouwt alles wat met vt_0 begint
python3 -I build_testpack.py <resources-map> <scan-map> rewrite vt_08  -- alleen README, sources.json, manifest en gewijzigde meta's opnieuw
python3 -I build_testpack.py <resources-map> <scan-map> index          -- het overzicht opnieuw
```

Het script leest alleen uit `[Vehicles]` en schrijft alleen in `[vehicletests]`. Een geval waarvan de map al bestaat, slaat het over; het overschrijft geen voertuigbestanden en verwijdert niets.

Regels:

- **Nooit repareren** wat uit een download komt; daar gaat het om.
- **Eén geval tegelijk**, behalve de paren (`vt_30`, `vt_31`, `vt_32`) en `vt_01` met `vt_01b`.
- **Niet samen met de downloads.** `[Vehicles]` bevat dezelfde voertuigen.
- **De voertuigen niet in git.** Ze zijn van andere makers, en samen honderden MB's. In de repo staan alleen de beschrijvingen en het script; met de downloads maakt het script het pakket opnieuw.

## Nog open

1. De gevallen die nog niet getest zijn (lijst onder [Uitkomsten](#uitkomsten)), met de testregel voor kits: schone sessie per model.
2. Waarom `calico`, `tailgater2` en `futo2` hun kit kwijtraakten na het stoppen van de grote packs (Q-S15): een pack los starten en stoppen, en steeds de vanilla-kits bekijken.
3. De voertuigen uit "Nog te zoeken" vinden, en de gevallen uit het archief in het pakket zetten.
