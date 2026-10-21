# Testpakket

**Besloten (B25, Mark, 21 okt 2026):** we maken een eigen testpakket, ook met gevallen waarin we expres een fout zetten. Het komt in plaats van de downloads: `ensure [Vehicles]` gaat uit `server.cfg` zodra het pakket draait. Er is nog niets gebouwd of gekopieerd.

Dit document zegt eerst **wat we nodig hebben** voor alles wat de tool moet kunnen, dan **welke voertuigen** dat worden, en hoe het pakket is opgebouwd. De voertuigen komen uit de scan van de downloads ([test_data.md](test_data.md#downloads-in-vehicles-21-okt-2026)) en uit `archive/` van de projectmap.

---

## Wat we nodig hebben

Per onderdeel van de tool, in Marks volgorde (B12): wat we willen testen, en wat voor voertuig daarvoor nodig is.

- ✓ = hebben we (welk voertuig, en waar het vandaan komt)
- **maken** = maken we zelf: een kopie van een schoon voertuig, met expres één fout erin
- **zoeken** = hebben we nog niet

### 0. Schone voertuigen, één per type

Nodig voor de templates per type (Q-M12, Q-S8) en als "goed"-referentie.

| Type | Waarom | Bron |
|------|--------|------|
| Auto | basis voor bijna alle gemaakte gevallen | ✓ `tltypes` (PLOKS) |
| Motor | eigen handling-klasse (`CBikeHandlingData`) en layout | ✓ `bati901` (Lore), maar de geluidsmap ontbreekt: **maken** we schoon |
| Trailer | geen motor, andere velden | **maken**: een schone kopie van `zaccflatlit` (het enige trailer-voorbeeld heeft fouten) |
| Heli | `CFlyingHandlingData`, andere meta-velden | ✓ `sheriffmav` (`11john11_sapo_pack`, archief) |
| Vliegtuig | idem | **zoeken** |
| Boot | `CBoatHandlingData` | **zoeken** |
| Hulpdienst | sirene en lichten met eigen id's | ✓ `umkscout` (`alamo`, archief): eigen sirene 232 |

### 1. Structuur, templates en meta's

| Wat we willen testen | Wat voor voertuig | Bron |
|----------------------|-------------------|------|
| De gekozen indeling (B24) | het schone voertuig, en een voertuig met onderdelen en liveries | ✓ `tltypes` (PLOKS), ✓ `atlas` (lds) |
| Minimale set per type (Q-S8) | het schone voertuig zonder `carvariations`, zonder `carcols`, zonder `vehiclelayouts`, zonder `dlctext`, zonder `shop_vehicle` | **maken** (5×) |
| Ontbrekende velden (Q-M14) | `vehicles.meta` waar één veld uit is (`audioNameHash`, `layout`, …) | **maken** |
| Kapotte XML (Q-M16) | `--` in een commentaar, een tag die niet dichtgaat, een verkeerde sluit-tag, NUL-bytes, spaties vóór `<?xml`; en een BOM en een losse `&` | ✓ `bolide`, `84rx7k`, `taycan` (PLOKS), `imperial`, `gstghell1` (lds); **maken**: BOM en `&` |
| Koppelingen (M4–M10) | model zonder `.yft` · `txdName` zonder `.ytd` · `handlingId` die niet bestaat · `handlingId` van vanilla · kit die nergens staat · licht-id die niet bestaat | ✓ `accolade` (lds) · **maken** · **maken** · ✓ `surano3` (lds) · ✓ `yosemiteswb` (lds) · ✓ `kriegerty2` (licht 140) |
| Ongeldige waarden | `vehicleClass` die niet bestaat · type en klasse die niet passen · layout die niet bestaat | ✓ `stingray` (PLOKS) · **maken** · **maken** |
| Naam (Q-M18, B26) | geen tekst · tekst via de hash · naam uit het manifest | ✓ `blistacr` (lds) · **maken** · **maken** |
| Liveries | soort 1 (in de `.ytd`) · soort 2 (mod-onderdeel) · soort 3 (livery2) · soort 4 (apart model) | **zoeken** · ✓ `atlas` (lds) · **zoeken** · ✓ `lsfd` (archief) |
| Geluid | eigen geluid in de resource · geluid uit een andere resource · geluids-resource ín een resource · ontbrekende geluidsmap | ✓ `buffaloh` (Lore) · ✓ Custom Engine Sounds (archief) · ✓ `zionks` (lds) · ✓ `bati901` (Lore) |
| Pack splitsen (B2) | pack met gedeelde handling · groot pack | ✓ `USSS` (archief) · ✓ `PLOKS_CARS` |

### 2. Manifest

| Wat we willen testen | Bron |
|----------------------|------|
| Onbekende `data_file`-types (Q-M15) | ✓ `kriegerty2` |
| Elke meta onder elk type (Q-S13) | ✓ `buffaloh` (Lore), met het manifest van de Lore-pack |
| Oud manifest en ontbrekende bestanden (Q-S9) | ✓ `zaccflatlit` |
| Escrow (Q-T7) | ✓ `strman`: start niet zonder recht |
| Meta niet in `files {}` (R15) · hoofdletters in een glob (R16) · `*` in een mapnaam · `stream/` niet in de root (F10) | **maken** (4×) |
| Resource in een resource (R13) | ✓ de geluids-resources van lds, de wielen-packs van Lore |

### 3. Botsingen (twee resources tegelijk)

| Wat we willen testen | Bron |
|----------------------|------|
| Zelfde kit-id | ✓ `rcf` (PLOKS) + `dubstag` (lds) |
| Zelfde stream-naam, andere inhoud | ✓ `f430s` + `gs350` (PLOKS) |
| Zelfde voertuig twee keer | ✓ `vorstand` (Lore + lds) |
| Vervangt een vanilla-voertuig | ✓ `futo2` (Lore) |
| Kit met een vanilla-naam | ✓ `wildtrak` (PLOKS) |
| Zelfde bestandsnaam in twee submappen van één resource (X7) | **maken** |

### 4. Textures

| Wat we willen testen | Bron |
|----------------------|------|
| Elke grens van de melding: 16, 32, 48 en 64 MiB | ✓ `cutlass` (26 MiB), `rhinetaxi` (40), `nissantitan17` (52), `i8` (128) |
| Textures in het model (`.yft`) | ✓ `ingotc` (lds) |
| Een `.ytd` om te verkleinen (Q-T4) | ✓ `i8.ytd`: 1,5 MB op schijf, 128 MiB in het geheugen |
| `txdRelationships` | ✓ `kriegerty2` (vanilla-ouder) |
| `.rpf` in `stream/` (Q-S14) | ✓ `rculi` (PLOKS) |

### 5. Handling-editor

| Wat we willen testen | Bron |
|----------------------|------|
| "Normaal" per klasse (Q-H4) | vanilla-voertuigen: geen add-on nodig, spawnen en uitlezen |
| Uitschieters | ✓ `720s` (10 versnellingen), `teslax` (1 versnelling), `ruiner6str` (kracht 4,79) |
| Niet-auto's | motor, heli, boot en vliegtuig uit 0 |
| Gedeelde handling | ✓ `USSS` (zes modellen op één `handlingId`) |

### 6. Intake (later)

| Wat we willen testen | Bron |
|----------------------|------|
| `dlc.rpf` uitpakken en omzetten (Q-A3) | ✓ `cle53amg` |

### Nog te zoeken

- een **vliegtuig** en een **boot**: echte add-ons met een model;
- een voertuig met **liveries in de `.ytd`** (soort 1, met `<liveries>` in `carvariations`), vaak politie of brandweer;
- een voertuig met **livery2** (dak-livery, soort 3).

---

## "Gemaakt": expres één fout erin

Een gemaakt geval is een kopie van een schoon voertuig (meestal `vt_00`, uit `tltypes`) waarin we **precies één** ding fout zetten: een meta weglaten, een veld weghalen, een `--` in een commentaar zetten, het manifest een ander pad geven. Zo weten we zeker welke fout welk gevolg heeft; gevallen uit de downloads hebben vaak meer dan één probleem tegelijk. Mark vindt dat prima, en "zelfs verstandig" (21 okt).

Alle gemaakte gevallen van `vt_00` gebruiken dezelfde model- en bestandsnamen, dus er draait er steeds één tegelijk.

| Geval | Fout | Vraag / controle |
|-------|------|------------------|
| `vt_60` t/m `vt_64` | zonder `carvariations`, `carcols`, `vehiclelayouts`, `dlctext`, `shop_vehicle` (één per geval) | Q-S8, Q-M9, Q-M2, Q-M3 |
| `vt_65` | één veld weg uit `vehicles.meta` (eerst `audioNameHash`, dan `layout`) | Q-M14 |
| `vt_66`, `vt_67` | een BOM vóór de XML; een losse `&` in een tekst | Q-M16, M1 |
| `vt_68` | `txdName` die niet bestaat | M5 |
| `vt_69` | een `layout` die niet bestaat | M11 |
| `vt_70` | type en klasse die niet passen (motor als `VC_SUPER`) | M17 |
| `vt_71`, `vt_72` | naam via `AddTextEntryByHash`; naam uit het manifest | Q-M18, Q-M20, B26 |
| `vt_73` | de meta's niet in `files {}` | R15 |
| `vt_74` | hoofdletters in een glob (`data/**/Vehicles.meta`) | R16 |
| `vt_75` | `*` in een mapnaam (`data/*/vehicles.meta`) | Q-S3 |
| `vt_76` | `stream/` niet in de root (`assets/stream/`) | F10 |
| `vt_77` | twee bestanden met dezelfde naam in `stream/mods/` en `stream/liveries/` | X7 |
| `vt_78` | kit-id boven 65.535 | Q-M4 |
| `vt_80`, `vt_81` | schone motor (uit `bati901`) en schone trailer (uit `zaccflatlit`) | 0 |

## De gevallen uit de downloads (eerste ronde)

Samen 31 gevallen (35 resources: de paren en de geluids-resource van `vt_01` tellen dubbel), ongeveer 430 MB. Een voertuig uit een pack krijgt de gekozen indeling (B24), behalve als het geval juist over de vorm gaat (zoals `vt_21` met het manifest van de Lore-pack); de bestanden zelf blijven zoals ze gedownload zijn.

Bijvangst die niet bij elk geval staat: bijna alle voertuigen uit `lds-lorevehicles`, en veel uit de andere packs, hebben geen tekst voor `gameName` (M16).

### Structuur, templates en meta's

| Geval | Voertuig (bron) | MB | Probleem | Vraag / controle |
|-------|-----------------|---:|----------|------------------|
| `vt_00_baseline` | `tltypes` (PLOKS) | 7,8 | geen: de scan vindt niets, naam via `AddTextEntry`, niets boven 16 MiB | referentie en basis voor de gemaakte gevallen |
| `vt_01_nested_resource` | `zionks` (lds), met zijn geluids-resource eerst ín, dan naast de resource | 10 | een resource in een resource laadt niet; dan ontbreekt het eigen geluid | R13 |
| `vt_02_xml_comment` | `bolide` (PLOKS) | 13,4 | `<!------…---->` in `vehicles.meta` | Q-M16, M1 |
| `vt_03_xml_wrong_close` | `84rx7k` (PLOKS) | 18,5 | `carcols.meta`: `<Kits>` gaat nooit dicht, en de kit staat binnen `<Lights>` | Q-M16, M1 |
| `vt_04_xml_nul_bytes` | `imperial` (lds) | 16,3 | NUL-bytes aan het eind van `carvariations.meta` | Q-M16, M1 |
| `vt_05_xml_space_before_decl` | `gstghell1` (lds) | 6,0 | drie spaties vóór `<?xml` in `carcols.meta` (bijvangst: eigen geluid zit in een geneste resource) | Q-M16, M1 |
| `vt_06_model_without_yft` | `accolade` (lds) | 4,8 | `vehicles.meta` noemt ook `accolade2`, maar daar is geen `.yft` voor | M4 |
| `vt_07_no_carvariations` | `sandero` (PLOKS) | 8,6 | geen `carvariations.meta` (bijvangst: handling van de vanilla `BALLER`) | Q-M9 |
| `vt_08_invalid_class` | `stingray` (PLOKS) | 31,1 | `vehicleClass` `VC_SPORTS` bestaat niet; `gameName` met een spatie (`corvette c8`) | Q-M17, M27 |
| `vt_09_no_label` | `blistacr` (lds) | 2,3 | geen tekst voor `gameName` | Q-M18, M16 |
| `vt_10_unknown_audio` | `hellenstorm` (lds) | 10,5 | `audioNameHash` (`hellenstorm`) die niet in de downloads staat en geen vanilla-voertuignaam is | M12 |
| `vt_11_vanilla_handling` | `surano3` (lds) | 5,3 | `handlingId` `SURANO` (vanilla): mag, verwacht geen fout | M28 |
| `vt_12_kit_not_defined` | `yosemiteswb` (lds) | 2,8 | `carvariations` noemt `0_suv_modkit`, die niet in de eigen `carcols` staat (of hij in vanilla bestaat: Q-M19) | M8 |
| `vt_13_livery_mods` | `atlas` (lds) | 6,2 | geen echt probleem: 16 liveries als mod-onderdeel (livery soort 2) | M22, [folder_structure.md](folder_structure.md) §2 |

### Manifest

| Geval | Voertuig (bron) | MB | Probleem | Vraag / controle |
|-------|-----------------|---:|----------|------------------|
| `vt_20_unknown_types` | `kriegerty2` | 7 | `DLCTEXT_FILE` en `VEHICLE_SHOP_FILE` staan niet in de officiële lijst | Q-M15, R14 |
| `vt_21_all_types_glob` | `buffaloh` (Lore), met het manifest van de Lore-pack | 5,6 | elke meta onder negen types, waarvan twee onofficieel | Q-S13, R6 |
| `vt_22_old_manifest` | `zaccflatlit` | 18,3 | `__resource.lua`, en twee meta's uit het manifest ontbreken | Q-S9, R2, R4 |

### Botsingen (paren: twee resources tegelijk)

| Geval | Voertuigen (bron) | MB | Probleem | Vraag / controle |
|-------|-------------------|---:|----------|------------------|
| `vt_30_kit_id_pair` | `rcf` (PLOKS) + `dubstag` (lds) | 24,1 | allebei kit-id 689 | Q-S6, X4 |
| `vt_31_stream_name_pair` | `f430s` + `gs350` (PLOKS) | 32,4 | allebei `spoiler_2.yft` en `spoiler_3.yft`, met andere inhoud | Q-S6, X1, X7 |
| `vt_32_same_vehicle_twice` | `vorstand` uit lds én uit Lore | 22,2 | zelfde model, stream-namen en kit-id 701 | X1, X2, X4 |
| `vt_33_vanilla_vehicle` | `futo2` (Lore) | 6,6 | vervangt de vanilla Futo GTX (bijvangst: `fInitialDriveForce` 4,79) | X5, Q-T6 |
| `vt_34_vanilla_kit` | `wildtrak` (PLOKS) | 26,2 | definieert kits met de naam van vanilla-voertuigen: `268_hermes_modkit` en `269_revolter_modkit` | Q-M19, M21 |

### Textures

| Geval | Voertuig (bron) | MB | Probleem | Vraag / controle |
|-------|-----------------|---:|----------|------------------|
| `vt_40_over_16` | `cutlass` (PLOKS) | 7,7 | 26 MiB: blauwe melding | Q-T1, T1 |
| `vt_41_over_32` | `rhinetaxi` (lds) | 6,8 | 40 MiB: gele melding | Q-T1, T1 |
| `vt_42_over_48` | `nissantitan17` (PLOKS) | 20,8 | 52 MiB: gele melding met "WILL lead to streaming issues" | Q-T1, Q-T2, T1 |
| `vt_43_over_64_ytd` | `i8` (PLOKS) | 16,8 | `i8.ytd`: 128 MiB uit 1,5 MB op schijf | Q-T1, Q-T2, Q-T4 |
| `vt_44_yft_with_textures` | `ingotc` (lds) | 5,4 | `ingotc_interiormod.yft`: 128 MiB phys, textures in het model | Q-T1, T1 |
| `vt_45_escrow` | `strman` | 26 | escrow; 76 MiB; `carcols.meta` uit het manifest ontbreekt | Q-T7, R9, T2 |
| `vt_46_rpf_in_stream` | `rculi` (PLOKS) | 37,9 | `rculi_mods.rpf` in `stream/` | Q-S14, F9 |

### Handling (voor de grenzen in de editor)

| Geval | Voertuig (bron) | MB | Probleem | Vraag / controle |
|-------|-----------------|---:|----------|------------------|
| `vt_50_ten_gears` | `720s` (PLOKS) | 13,1 | `nInitialDriveGears` 10 | Q-H14 |
| `vt_51_extreme_force` | `ruiner6str` (Lore) | 7,5 | `fInitialDriveForce` 4,79 (90% van de downloads zit tussen 0,20 en 0,525) | Q-H4, Q-H5, M19 |

---

## Opbouw

```text
resources/
  [vehicletests]/                 -- niet in server.cfg; elk geval los starten
    vt_00_baseline/               -- één geval = één resource, in de indeling van B24
      fxmanifest.lua
      README.md                   -- het geval: zie hieronder
      data/ …
      stream/ …
    vt_02_xml_comment/
    …
```

De `README.md` van elk geval:

- **Probleem:** wat er mis is, met het pad in de bron.
- **Bron:** pack, map, maker, en de downloaddatum (of: "gemaakt uit `vt_00`").
- **Verwacht van de tool:** welke controle afgaat (bijv. M1) en met welke ernst.
- **Vraag:** welke open vraag het beantwoordt (bijv. Q-M16).
- **In-game kijken:** console en F8 bij het starten, spawnen, naam, kleuren, mods, geluid.
- **Uitkomst:** na de test, met datum en het label `tested`.

Regels:

- **Nooit repareren** wat uit een download komt; daar gaat het om.
- **Eén geval tegelijk**, behalve de botsingsgevallen: die bestaan juist uit twee resources.
- **Niet samen met de downloads.** Zolang `ensure [Vehicles]` aan staat, draaien `PLOKS_CARS`, `Lore_Friendly_Car_Pack`, `lds-lorevehicles`, `kriegerty2` en `zaccflatlit` mee, en die botsen met hun kopieën in het pakket.
- **De voertuigen niet in git.** Ze zijn van andere makers, en samen honderden MB's. In de repo komen alleen de beschrijvingen en een lijst waar elk bestand vandaan komt, zodat het pakket opnieuw te maken is.

## Nog open

1. De indeling (B24) en de naam (B26) kiezen; daarna bouwen we `vt_00_baseline` en testen we die in-game.
2. De voertuigen uit "Nog te zoeken" vinden.
3. Begin met de gevallen van prioriteit 1 en 2 (structuur en manifest); textures en handling daarna.
