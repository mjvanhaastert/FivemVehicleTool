# Open vragen: het onderzoek dat nog moet

Wat we nog niet weten, waarom het telt, en hoe we het uitzoeken. Per vraag:

- **Aanpak:** `bron` = opzoeken (FiveM-docs, FiveM-broncode, wiki), `test` = op de dev-server, `meten` = een script over bestanden.
- **Prio:** hoog = bepaalt een beslissing of de opzet van de tool; middel = nodig voor een onderdeel; laag = nice to know.
- **Status:** open, bezig, klaar (met datum en waar het antwoord staat).

Testen gaat volgens de werkwijze: eerst `status` van dolu_fivem_mcp (draait de server, is de client verbonden), dan zelf testen met de dolu-tools. Wat Mark zelf moet doen (voertuigen klaarzetten, in-game kijken), staat in de takenlijst onderaan.

---

## S. Structuur en manifest

| # | Vraag | Waarom | Aanpak | Prio | Status |
|---|-------|--------|--------|------|--------|
| Q-S1 | Maakt de mapnaam van de meta's uit (`common/`, `data/`, `meta/`, root)? | Welke structuren de tool moet accepteren | test: hetzelfde voertuig in drie vormen | middel | open |
| Q-S2 | Mag een meta-bestand elke naam hebben (`krieger_handling.meta`)? | Naamgeving binnen een pack | test | laag | open |
| Q-S3 | Werken globs in `data_file` (`data/**/handling.meta`), en laden ze alle gevonden bestanden? | Manifest-generator; de downloads gebruiken ze allemaal | bron (broncode) + test met twee voertuigen | middel | **deels** (21 okt, broncode en testpakket): de client globt elk `data_file`-pad zoals `files` en laadt elk gevonden bestand onder dat type. In de game getest: hoofdlettergevoelig, ook op Windows (`vt_74`: `data/**/Vehicles.meta` vindt `vehicles.meta` niet, geen voertuig), en een `*` in een mapnaam vindt niets (`vt_75`). Dat `**` werkt, staat in de broncode; in de game nog met `vt_21`. Zie [meta_files.md](meta_files.md) §10 |
| Q-S4 | Streamt FiveM ook submappen van `stream/` (`stream/krieger/krieger.yft`)? En een `stream/` die niet in de root staat (`<categorie>/stream/`, zoals de repo maakt)? | Indeling binnen de resource (B24) | bron + test | middel | **beantwoord** (21 okt, `tested`): liveries uit `stream/liveries/` (`vt_13b`, livery zichtbaar op de auto) en onderdelen uit `stream/mods/` (`vt_11`, de nieuwe voorbumper zichtbaar) werken in de game. Een `stream/` die niet in de root staat, wordt niet gestreamd: de meta's laden, maar het model laadt nooit (`vt_76`) |
| Q-S5 | Breekt een kapotte meta (XML-fout, onbekend veld) alleen dat bestand, of de hele resource? Wat staat er in de console? | Eén bestand per voertuig of per pack (B2) | test | **hoog** | open |
| Q-S6 | Twee bestanden met dezelfde stream-naam (in twee resources, of in submappen van één resource), dezelfde `modelName`, `handlingName` of kit-id: wie wint, en meldt FiveM het? | Botsingscontrole over de hele server | test | **hoog** | open; nu goed te testen: de Lore-pack en `lds-lorevehicles` draaien sinds 21 okt allebei, met 20 dezelfde voertuigen. Voorbeelden uit de downloads: `spoiler_2.yft` bij drie auto's in `PLOKS_CARS`; kit-id 964 in drie packs ([test_data.md](test_data.md#downloads-in-vehicles-21-okt-2026)). Uit de broncode: binnen één resource houdt de server stil het eerste bestand met die naam; bij dubbele resourcenamen wint de eerste gevonden, met een melding |
| Q-S7 | Maakt de volgorde van `data_file` in het manifest uit (layouts vóór vehicles)? | De "team-standaard" uit `meta_reference` §1 | bron + test | middel | open |
| Q-S8 | Welke meta's zijn echt nodig per type (auto, motor, heli, boot, vliegtuig, trailer)? Wat mis je zonder `carvariations`, `carcols`, `dlctext`, `shop_vehicle`? | Minimale set en templates; de bronnen spreken elkaar tegen | test: `alamo` steeds met één bestand minder | **hoog** | **deels** (21 okt, `tested`): zonder `carcols.meta` werkt een auto, met de kleuren uit `carvariations`, maar zonder kit (`vt_61`). De rest (`vt_60`, `vt_62`, motor, trailer) nog te testen |
| Q-S9 | Werkt `__resource.lua` nog op onze FXServer (37389)? | Omzetten of alleen waarschuwen | test (`zaccflatlit`) | laag | **klaar** (21 okt, serverlog, `tested`): `zaccflatlit` met `__resource.lua` start ("Started resource zaccflatlit (3 warnings)": één oversized-bestand en twee ontbrekende bestanden). De melding "outdated manifest" komt alleen als de resource `client_script`s heeft (broncode). Of het voertuig in-game werkt, nog kijken |
| Q-S10 | Wat is beter voor de server en de spelers: één grote voertuig-resource, of veel kleine (starttijd, joinen, downloaden, geheugen, herstarten)? | B1 en B2: Mark koos één resource per voertuig en wil weten wat dat kost | bron (broncode, Cfx-forum) + test: dezelfde voertuigen als 1 pack en als losse resources, starttijd en jointijd meten | **hoog** | **deels** (21 okt, broncode en forum): geen limiet op het aantal resources; tijdens het spelen geen verschil; losse resources kosten vooral bij de eerste join, en zijn goedkoper bij elke update. Zie [folder_structure.md](folder_structure.md) §3. Nog meten |
| Q-S11 | Wat doet `_manifest.ymf` in `stream/`, en wat als twee voertuigen er een hebben (in een gedeelde pack botst hij altijd)? | Pack splitsen | bron + test (bron van `pigeonp`; zes in de Lore-pack) | laag | open |
| Q-S12 | Leest FiveM `data_file 'TYPE' { 'a.meta', 'b.meta' }` met een tabel (zoals de repo schrijft)? | Manifest-generator | bron + test | laag | open |
| Q-S13 | Wat doet de game met een meta die onder het verkeerde type geladen wordt? De Lore-pack laadt elke meta onder negen types (ook `vehicles.meta` als `HANDLING_FILE`) | Ernst van R6; zo'n pack splitsen | test (één voertuig uit de Lore-pack, met dat manifest) | middel | open |
| Q-S14 | Wat doet FiveM met een `.rpf` in `stream/` (`PLOKS_CARS/stream/[ROLLSROYCE]/rculi/rculi_mods.rpf`)? | Ernst van F9 | test | laag | open |
| Q-S15 | Wat gebeurt er met kits en variaties in de client als een resource stopt, en als een andere resource daarna hetzelfde model laadt? En waarom verloren `calico`, `tailgater2` en `futo2` hun vanilla-kit toen de vijf packs stopten? | Testmethode; de editor (gaat een wijziging in `carcols` of `carvariations` zonder opnieuw verbinden?); de controle op kit-id's | test | **hoog** | **deels** (21 okt, `tested`): de client houdt per model de eerste kit-koppeling vast, ook na `stop`; een latere resource met hetzelfde model verandert die niet (`vt_13` na `vt_13c` had de kit van `vt_13c`; `vt_00` na `vt_61` had geen kit). Opnieuw verbinden maakt de client schoon. Het verlies van de vanilla-kits na het stoppen van de packs is nog niet verklaard: alleen `futo2` stond in een pack, en een los geval (`vt_03`, `vt_13`) gaf het niet. Zie [test_pack.md](test_pack.md#uitkomsten) |

## M. Meta-inhoud

| # | Vraag | Waarom | Aanpak | Prio | Status |
|---|-------|--------|--------|------|--------|
| Q-M1 | `shop_vehicle.meta`: is het `VEHICLE_SHOP_DLC_FILE` of `VEHICLE_SHOP_FILE` (of beide)? | Onze bronnen gebruiken allebei | bron | middel | **klaar** (21 okt, `official`): alleen `VEHICLE_SHOP_DLC_FILE` staat in de officiële lijst; wat het in FiveM doet, is Q-M3 |
| Q-M2 | Doet `dlctext.meta` iets in FiveM? | Verplicht of niet (B13) | test met en zonder | laag | open |
| Q-M3 | Doet `shop_vehicle.meta` iets in FiveM? | Verplicht of niet (B13) | test met en zonder | laag | open |
| Q-M4 | Welk bereik mag een kit-id hebben? GTAMods zegt 0–1023, onze testdata heeft o.a. 1101–1105, 3995 en 64378. Wat gebeurt er boven 1023? | Kit-id-controle en vrije-id-voorstel | bron + test | middel | **beantwoord** (21 okt, `tested`): kit-id 1500 werkt (`vt_13c`, in een schone sessie: kit en 16 liveries). Wat niet werkt, is een id dat vanilla al gebruikt: dan krijgt het voertuig geen kit (`vt_13`, id 620 = `620_gt750_modkit`; zie M21). Boven 65.535 nog open (`vt_78`). In de downloads liggen minstens 85 van de 241 kit-id's die we konden lezen boven 1023, tot `123123135` |
| Q-M5 | Hoe hangen `VC_*` (in `vehicles.meta`) en `GetVehicleClass` 0–22 samen? VehicleTool heeft de `VC_*`-namen in de volgorde 0–22 (`ui.py`); nog niet bevestigd | Templates en grenzen per klasse | meten in de game (vanilla-meta naast `GetVehicleClass`) | middel | open |
| Q-M6 | Maximale lengte van `modelName`, `txdName`, `handlingId`, `gameName`? (oude notities: ~11 en ~14 tekens; kennisbasis: een `AddTextEntry`-sleutel van 16 tekens werkt bij `BeginTextCommandDisplayText`, van 20 niet) | Naamregels | bron + test | middel | open |
| Q-M7 | Hoe werkt livery2 (dak-livery), en welke bestanden horen erbij? | Livery-regels | bron | laag | open |
| Q-M8 | Is `handlingId` ↔ `handlingName` hoofdlettergevoelig? | Naamregels (`scout2020` naast `SCOUT2020`) | test | laag | **deels**: de handling-natives zoeken de naam zonder hoofdletters (broncode); de koppeling in de meta's zelf nog testen |
| Q-M9 | Wat gebeurt er zonder `carvariations.meta`? | Deel van Q-S8 | test | middel | open |
| Q-M10 | Wat is de officiële lijst van `data_file`-types (ook `FIVEM_LOVES_YOU_*`)? | Manifest-check en -generator | bron | middel | **klaar** (21 okt, `official`): de pagina "Data files" op docs.fivem.net; zie [meta_files.md](meta_files.md) §10 |
| Q-M11 | Welk `data_file`-type hoort bij `.dat10.rel` (synth/amp)? | Audio-check | bron | laag | **klaar** (20 okt, gelezen): `AUDIO_SYNTHDATA`, zie [audio.md](audio.md); in-game nog niet getest |
| Q-M12 | Waar halen we echte vanilla-meta's per type vandaan, als basis voor de templates? | De huidige templates kloppen deels niet | bron (game-bestanden via CodeWalker/OpenIV) | **hoog** | open |
| Q-M13 | Hoe controleren we dat een `audioNameHash` bestaat (vanilla-lijst + eigen `.dat151.rel`)? | Audio-check | bron (DurtyFree) | laag | **deels**: de `.nametable` naast een `.rel` geeft de namen (gebruikt in de scan van 21 okt); een vanilla-lijst van geluiden ontbreekt nog. Vier voertuigen in de downloads hebben een geluid dat niet in de downloads staat en geen vanilla-voertuignaam is |
| Q-M14 | Welke velden in `vehicles.meta` zijn verplicht? Wat doet de game als een veld ontbreekt (standaardwaarde of fout)? | "Ontbrekende waarden aanvullen uit de template" | test | middel | open |
| Q-M15 | Wat doet FiveM met een `data_file`-type dat niet in de officiële lijst staat (`DLCTEXT_FILE`, `VEHICLE_SHOP_FILE`, `CARCONTENTUNLOCKS_FILE`, `CAR_ADDON_CONTENT_UNLOCKS`, `VEHICLE_SETTINGS_FILE`)? Negeren, of een melding in de console of F8? | Ernst van R14 | test (`kriegerty2`) | middel | open |
| Q-M16 | Slikt de game XML die een strikte parser weigert: `--` in een commentaar, verkeerde sluit-tags, NUL-bytes aan het eind, spaties vóór `<?xml`? | Ernst van M1; of de tool zulke bestanden moet repareren | test (vier voorbeelden uit de downloads, [test_pack.md](test_pack.md)) | **hoog** | **beantwoord** (21 okt, `tested`, testpakket): de game laadt `--` in een commentaar (`vt_02`), NUL-bytes aan het eind (`vt_04`), spaties voor `<?xml` (`vt_05`) en een BOM (`vt_66`). Een losse `&` laadt ook, maar verminkt de tekst: `Acura&Co` wordt `Acura?o` (`vt_67`). Bij een `<Kits>` die nooit dichtgaat (`vt_03`) werkt het voertuig, maar die kit gebruikt het niet, dus of de rest van die `carcols` laadt, weten we niet. De server meldt niets |
| Q-M17 | Welke klasse krijgt een voertuig met een `vehicleClass` die niet bestaat (`VC_SPORTS`, `VC_COMPACTS`)? | Ernst van M27 | test (`GetVehicleClass`) | laag | open |
| Q-M18 | Wat ziet de speler als er geen tekst is voor `gameName` ("NULL", de modelnaam)? En werkt `AddTextEntryByHash` met de hash van `gameName` net zo goed als `AddTextEntry`? | Ernst van M16 | test | middel | **deels** (21 okt, `tested`): zonder tekst geeft `GetLabelText` "NULL" (`vt_00` voor `AddTextEntry`). `AddTextEntryByHash` nog open (`vt_71`) |
| Q-M19 | Wat gebeurt er als een add-on een kit met een vanilla-naam opnieuw definieert (`0_default_modkit`, `268_hermes_modkit`)? Welke kit-id's gebruikt de game zelf in build 3889? | Kit-controle (M21, X4) | test + dump | middel | open |
| Q-M20 | Kan een voertuig zijn naam krijgen zonder script, bijvoorbeeld met een GTA-tekstbestand (`.gxt2`) in `stream/` of via `TEXTFILE_METAFILE`? En werkt `GetResourceMetadata` op de client voor eigen sleutels als `vehicle_label`? | Keuze B26 (hoe een voertuig zijn naam krijgt) | bron + test | middel | **deels** (21 okt, `tested`): `GetResourceMetadata` leest eigen sleutels op de client, ook bij een resource zonder scripts: `vehicle_label` gaf `tltypes`, `vehicle_label_extra` gaf `"Acura TL Type-S"` (de tweede waarde als JSON). Daarmee werkt B26 (b). Een `.gxt2` is nog niet getest |

## T. Textures en assets

| # | Vraag | Waarom | Aanpak | Prio | Status |
|---|-------|--------|--------|------|--------|
| Q-T1 | Wat is de exacte grens voor "oversized", wat meet FiveM (phys, virt, per bestand?), en wat is de tekst van de melding? | Kern van de texture-check | bron (FiveM-broncode) + serverlog | **hoog** | **klaar** (21 okt, broncode en serverlog, `tested`): per bestand, phys en virt apart, meldingen boven 16, 32 en 64 MiB, met de zin over streamingproblemen boven 48 MiB. Het aantal meldingen per pack klopt met onze scan. Zie [textures.md](textures.md#de-melding-van-fivem) |
| Q-T2 | Wat gebeurt er in-game bij een te groot bestand (laadt niet, laat, crash)? | Hoe streng de tool moet zijn | test | middel | open |
| Q-T3 | Zijn er ook grenzen per texture (resolutie, aantal per `.ytd`, macht van 2)? | Claims uit `plan.md` | bron + test | laag | open |
| Q-T4 | Kunnen we een `.ytd` zelf herschrijven (mip-levels weglaten, textures vervangen)? Via een eigen parser, CodeWalker als bibliotheek, of CodeWalker.API? | Of de tool kan **oplossen** of alleen **melden** (B19) | bron + prototype | **hoog** | open |
| Q-T5 | Wanneer laadt de game `<txd>.ytd` en wanneer `<txd>+hi.ytd`; tellen ze samen? | Rapportage per voertuig | bron + test | laag | open |
| Q-T6 | Vervangt een vanilla-naam in `stream/` (`vehicles_stanier_interior.ytd`) die texture voor alle voertuigen? | Waarschuwing in de check | test | laag | open |
| Q-T7 | Escrow: welke bestanden zijn versleuteld? Kan de tool altijd de header lezen? | Escrow herkennen en alleen melden | meten over meer escrow-packs | laag | **deels** (21 okt, serverlog): zonder recht op het asset start de resource niet ("You lack the required entitlement to use strman", daarna "Couldn't start resource strman."). In de downloads alleen `strman`: de twee `.yft`'s versleuteld, de `.ytd` niet |
| Q-T8 | Een te grote `.ytd` splitsen in twee met `txdRelationships`: verdwijnt de melding en laadt alles? | Alternatieve oplossing zonder kwaliteitsverlies | test | middel | open |

## H. Handling en de in-game editor

| # | Vraag | Waarom | Aanpak | Prio | Status |
|---|-------|--------|--------|------|--------|
| Q-H1 | Werkt `SetVehicleHandlingFloat` op één voertuig, of op alle voertuigen met dezelfde handling op die client? | Opzet van de editor | test (twee voertuigen van hetzelfde model) | **hoog** | **deels**: de broncode geeft elk voertuig een eigen kopie ([handling.md](handling.md)); in-game bevestigen |
| Q-H2 | Zien andere spelers de aangepaste handling? Moet de server de waarden naar iedereen sturen (state bag)? | Sync in de editor | test met twee clients | **hoog** | **deels**: de natives zijn alleen client-side en niet gesynchroniseerd (broncode); de state-bag-aanpak testen |
| Q-H3 | Welke velden werken direct, en welke pas na opnieuw instappen of spawnen? | Live aanpassen vs. respawn | test per veld | **hoog** | **deels**: `fInitialDriveForce` en `fInitialDriveMaxFlatVel` pas na `ModifyVehicleTopSpeed` (native-docs); de rest testen |
| Q-H4 | Wat zijn de "normale" waarden per klasse? | Grenzen in de editor (B18) | meten: alle vanilla-voertuigen spawnen en uitlezen, dataset in `data/` van de kennisbasis | **hoog** | open |
| Q-H5 | Harde grenzen per veld: waar breekt de physics of crasht het? Kloppen de Eddlm-ranges? | De "ontgrendelde" modus | bron + test | middel | **deels**: 0 deelt door nul bij vier velden (broncode) |
| Q-H6 | Kunnen we `SubHandlingData` (`CCarHandlingData`, `CBikeHandlingData`, `CFlyingHandlingData`, `CBoatHandlingData`) live lezen en schrijven? | Editor voor niet-auto's | test | middel | **deels**: de broncode zoekt ook in de sub-klassen, de docs zeggen van niet; testen |
| Q-H7 | Kunnen we vlaggen (`strModelFlags`, `strHandlingFlags`, `strDamageFlags`, `strAdvancedFlags`) live aanpassen? Welke werken alleen globaal? | Volledige editor | test | laag | **deels**: als getal te lezen en te schrijven (broncode); sommige alleen globaal (native-docs) |
| Q-H8 | Hoe schrijven we een `handling.meta` precies in het formaat van de game (getallen, vectoren, volgorde)? | Export | bron (vanilla-bestand) | middel | open |
| Q-H9 | Topsnelheid: hoe verhouden `fInitialDriveMaxFlatVel`, `ModifyVehicleTopSpeed` en de echte topsnelheid zich? Welke eenheid? (de bronnen zeggen 0–200 én 150–340) | Grenzen en metingen | bron + test (meten op een rechte weg) | middel | **deels**: meta-eenheid, intern ÷ 3,6 (broncode); de echte topsnelheid nog meten |
| Q-H10 | Werkt `ForceUseAudioGameObject` in FiveM om motorgeluid te wisselen? | Extra in de editor | test | laag | open |
| Q-H11 | Wat doen de bestaande editors (carmineos, Babicz, vehicleDebug) goed of fout? | Leren zonder het wiel opnieuw uit te vinden | bron (code lezen, licentie checken) | middel | open |
| Q-H12 | Blijft een aanpassing staan als het voertuig van netwerk-eigenaar wisselt? | Sync | test met twee clients | middel | open |
| Q-H13 | Geven de natives de waarde uit de meta terug, of een omgerekende waarde (m/s, radialen, verdeling)? | Export naar `handling.meta` klopt anders niet | test: waarde in meta vs. `GetVehicleHandlingFloat` | **hoog** | **deels**: meta-eenheden, FiveM rekent zelf om (broncode); behalve `fDriveBiasFront` onder 0,1 of boven 0,9. In-game bevestigen |
| Q-H14 | Kapt FiveM `nInitialDriveGears` af op 7 (add-ons gebruiken tot 10)? | Grenzen | test: 10 zetten en teruglezen | laag | open |
| Q-H15 | Welke veldnamen bestaan echt (bijv. `fPopUpLightRotation`, `fPetrolConsumptionRate`, `fWeaponDamageScaledToVehHealthMult`)? | Veldenlijst van de editor | test: alle namen langslopen en op "No such field" letten | middel | open |

## A. Architectuur en tooling

| # | Vraag | Waarom | Aanpak | Prio | Status |
|---|-------|--------|--------|------|--------|
| Q-A1 | Kan de "externe" kant (scannen, meta-check, header-check) als server-side FiveM-resource draaien? Leest `LoadResourceFile` ook binaire bestanden en niet-gestarte resources? Wat kunnen `io` en `os` server-side binnen de sandbox? | Eén tool in FiveM of twee tools (B3) | test | **hoog** | open |
| Q-A2 | Kan de server met `GetResourceMetadata` alle `data_file`-regels van elke resource lezen? | Manifest-check zonder het bestand te parsen | test | **hoog** | open |
| Q-A3 | Pakt `rpf-cli` een echt `dlc.rpf` uit (`cle53amg`)? Kapt hij bestanden vanaf 16 MB af (waarschuwing in de converter)? Welke versie is onze `rpf-cli.exe`, en heeft een nieuwere de opdrachten `textures` en `resource info`? | Intake vanaf GTA-mods; misschien ook textures lezen | test + bron | middel | open |
| Q-A4 | Welke taal voor het deel buiten de game: Python (zoals nu), Node (draait ook in FXServer), of C# (.NET, met CodeWalker)? | Hangt af van Q-A1 en Q-T4 | afweging | **hoog** | open |
| Q-A5 | Kunnen we CodeWalker als bibliotheek gebruiken (lezen en schrijven van `.ytd`, `.yft`, `.rpf`, `.rel`) zonder GUI? Licentie? | Texture-fix, audio-check | bron | **hoog** | open |
| Q-A6 | Hoe testen we een voertuig automatisch via dolu (spawnen, rijden, meten)? | Testen zonder Mark | test | middel | open |

---

## Voor de kennisbasis (na testen)

Dingen die niet alleen voor deze tool gelden. Na een test horen ze in de kennisbasis (`mjvanhaastert/Fivem`):

| Wat | Waar | Nu |
|-----|------|----|
| `io` en `os` bestaan server-side wél in FXServer, maar binnen de sandbox (`..` in een pad werkt niet; schrijven buiten de eigen resource wordt stil alleen-lezen; `os.createdir` bestaat). De kennisbasis zegt nu "Niet: `io.*`" | `info/runtime/sandbox.md` | broncode gelezen (`LuaScriptRuntime.cpp`, `LuaIO.cpp`, `LuaOS.cpp`, `FilesystemPermissions.cpp`); eerst testen |
| `SaveResourceFile` blokkeert `..` niet zelf: bestandsnamen altijd zelf opschonen | `info/runtime/sandbox.md` | broncode (`MetadataScriptFunctions.cpp`); testen |
| Hoe de handling-natives werken (eigen kopie per voertuig, alleen client, eenheden, hoofdletters) | nieuw: `info/natives/vehicle_handling.md` | broncode; testen (Q-H1 t/m Q-H3, Q-H13) |
| Vanilla-handling per voertuig, als dataset | nieuw: `data/handling.json` | nog te maken (Q-H4) |
| De RSC7-header lezen (geheugengrootte van een asset) | `examples/` (Python of Lua) | script getest op 20 okt ([textures.md](textures.md)) |
| Hoe de server resources vindt (haken, geneste resources laden niet, dubbele namen) en hoe `stream/` werkt (recursief, alleen de bestandsnaam, alleen in de root) | `info/` (resources) | broncode gelezen op 21 okt ([folder_structure.md](folder_structure.md) §5); in-game bevestigen |
| De oversized-melding: grenzen 16/32/48/64 MiB, per bestand, phys en virt | `info/` (streaming) | broncode gelezen op 21 okt ([textures.md](textures.md#de-melding-van-fivem)); in de serverlog bevestigen |
| Wat FiveM met `data_file` doet (globs, ontbrekende paden, hoofdlettergevoelig) en de officiële lijst van types | `info/` (manifest) | broncode en docs gelezen op 21 okt ([meta_files.md](meta_files.md) §10); in-game bevestigen |

## Volgorde van aanpak (voorstel)

Volgens Marks volgorde (B12): eerst structuur en templates, dan manifest, dan textures, dan de handling-editor.

1. **Bronnen** (geen dev-server nodig): Q-M12, Q-A5, Q-H11, Q-M20. Klaar op 21 okt: Q-T1, Q-M1, Q-M10, Q-S9; deels Q-S3, Q-S4, Q-S10, Q-T7.
2. **Indeling kiezen** (B24, B26) en het **testpakket** opbouwen ([test_pack.md](test_pack.md)), te beginnen met `vt_00_baseline` in de gekozen indeling.
3. **Structuur- en meta-tests** (dev-server, met client): Q-S4 in-game, Q-S5, Q-S6 (kan nu al: Lore en lds draaien allebei), Q-S8 (minimale set), Q-S13, Q-M15, Q-M16, Q-M9, Q-M14, Q-M18; daarna Q-M2, Q-M3, Q-M4, Q-M19.
4. **Manifest-tests**: Q-S3 in-game, Q-S7, Q-S12; architectuur Q-A1 en Q-A2 (één tool of twee, B3).
5. **Textures**: Q-T2, het prototype voor Q-T4 en Q-T8.
6. **Handling** (met speler): Q-H1, Q-H2, Q-H3, Q-H13, daarna de dataset voor Q-H4.

## Takenlijst voor Mark (voor de tests)

- [ ] In-game komen (één client) voor de tests die een speler nodig hebben; voor Q-H2 en Q-H12 later twee clients.
- [ ] De indeling kiezen (B24) en hoe een voertuig zijn naam krijgt (B26), zie [folder_structure.md](folder_structure.md) §3.
- [ ] Ontbrekende testvoertuigen zoeken: een boot, een vliegtuig, een voertuig met liveries in de `.ytd` (soort 1) en een met livery2 (zie [test_pack.md](test_pack.md)). Als de map `[vehicles_pack]` van de oude server er nog is: die tien resources zijn ook goede testdata.
- [ ] Zodra het testpakket draait: `ensure [Vehicles]` uit `server.cfg` halen (B25).
