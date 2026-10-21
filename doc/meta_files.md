# Meta-bestanden van een voertuig

Wat elk meta-bestand doet, hoe ze aan elkaar en aan `stream/` hangen, welk `data_file`-type erbij hoort, en welke set een voertuig minimaal nodig heeft.
De labels staan uitgelegd in [README.md](README.md#labels). Veel van dit document komt uit onze oude notities en is nog niet getest: dat staat er per regel bij.

---

## 1. Overzicht

De root-elementen zijn `tested`: gelezen uit alle meta's in onze testdata (20 okt 2026). De `data_file`-types zijn nagekeken tegen de officiële lijst op docs.fivem.net (21 okt 2026, zie §10): `VEHICLE_SHOP_DLC_FILE` staat erin, `VEHICLE_SHOP_FILE` en `DLCTEXT_FILE` niet, terwijl de converter ze allebei schrijft. Wat FiveM met een onbekend type doet (negeren, waarschuwen), is Q-M15.

| Bestand | Root-element | Wat staat erin | `data_file` | Nodig? |
|---------|--------------|----------------|-------------|--------|
| `vehicles.meta` | `CVehicleModelInfo__InitDataList` | Het voertuig: `modelName`, `txdName`, `handlingId`, `gameName`, merk, type, klasse, layout, geluid, vlaggen, LOD, `txdRelationships` | `VEHICLE_METADATA_FILE` | ja |
| `handling.meta` | `CHandlingDataMgr` | Rijgedrag per `handlingName`, met `SubHandlingData` (auto, motor, vliegen, boot) | `HANDLING_FILE` | ja, tenzij `handlingId` een vanilla-handling is (Q-S8) |
| `carvariations.meta` | `CVehicleModelInfoVariation` | Per `modelName`: kleuren, kits, livery-schakelaars, kentekens, `lightSettings`, `sirenSettings` | `VEHICLE_VARIATION_FILE` | aanbevolen (Q-M9) |
| `carcols.meta` | `CVehicleModelInfoVarGlobal` | Definities: modkits (`Kits`), lichten (`Lights`), sirenes (`Sirens`), wielen (`Wheels`, bijv. 308 in `vanillawheels`). Geen koppeling naar een voertuig | `CARCOLS_FILE` | alleen bij eigen kits, sirenes, lichten of wielen |
| `vehiclelayouts.meta` | `CVehicleMetadataMgr` | Eigen zit- en instaplayouts | `VEHICLE_LAYOUTS_FILE` | alleen als `layout` geen vanilla-layout is |
| `dlctext.meta` | `CExtraTextMetaFile` | **Alleen drie vlaggen** (`hasGlobalTextFile`, `hasAdditionalText`, `isTitleUpdate`). Geen namen | `DLCTEXT_FILE` (staat **niet** in de officiële lijst) | waarschijnlijk niet (Q-M2) |
| `shop_vehicle.meta` | `ShopVehicleDataArray` | Winkeldata: `lockHash`, `modelNameHash`, `cost`, `textLabel` | `VEHICLE_SHOP_DLC_FILE` (officieel; `VEHICLE_SHOP_FILE` staat niet in de lijst, Q-M1) | waarschijnlijk niet (Q-M3) |
| `contentunlocks.meta` | `SContentUnlocks` | Unlocks. In `vanillawheels` leeg (`<listOfUnlocks />`) | `CONTENT_UNLOCKING_META_FILE` | zelden |
| `vehicleweapon_*.meta`, `weapon*.meta` | `CWeaponInfoBlob` | Voertuigwapens (`vehicleweapon_bcat.meta` in `11john11_sapo_pack`, `weaponminigun.meta` in `USSS`) | `WEAPONINFO_FILE` | alleen bij wapens |
| `vehicleaihandlinginfo.meta` | (niet bekeken) | AI-rijgedrag (DriveV) | `FIVEM_LOVES_YOU_447B37BE29496FA0` | optioneel |
| `ptfxassetinfo.meta` | (niet bekeken) | Particle-assets | `PTFXASSETINFO_FILE` (officieel; in de VehicleOptimizer-template en in twee packs uit de downloads, die het bestand niet hebben) | zelden |
| audio | `.dat151.rel`, `.dat54.rel`, `.dat10.rel`, `.awc` | Eigen motorgeluid | `AUDIO_GAMEDATA`, `AUDIO_SOUNDDATA`, `AUDIO_SYNTHDATA`, `AUDIO_WAVEPACK` | zie [audio.md](audio.md) |

**Fout in onze oude notities:**

- `dlctext.meta` bevat **geen** weergavenamen (`docs/plan.md` §4 zei van wel). De naam in het spel komt van een tekstlabel met de sleutel `gameName`; in FiveM zet je die met `AddTextEntry` (zie §3). `tested` (gelezen).
- De VehicleTool-templates voor `dlctext.meta` en `shop_vehicle.meta` gebruiken root-elementen die in geen enkel echt bestand voorkomen (`CVehicleModelInfoNameData`, `CShopVehicleData`). Zie [duplicates_and_conflicts.md](duplicates_and_conflicts.md), K17.

---

## 2. Hoe alles aan elkaar hangt

```text
vehicles.meta
  modelName ──────────► stream/<modelName>.yft  (+ <modelName>_hi.yft)
  txdName ────────────► stream/<txdName>.ytd     (+ <txdName>+hi.ytd)
  txdRelationships ───► parent-.ytd als een texture ontbreekt (keten)
  handlingId ─────────► handling.meta  <handlingName>
  layout ─────────────► vanilla LAYOUT_* of vehiclelayouts.meta
  audioNameHash ──────► vanilla voertuiggeluid of eigen audio (dat151)
  gameName ───────────► tekstlabel (naam in het spel)
  vehicleMakeName ────► tekstlabel (merk)

carvariations.meta  (per <modelName>, zelfde naam als vehicles.meta)
  <kits><Item> ───────► carcols.meta  <Kits><Item><kitName>
  <sirenSettings> ────► carcols.meta  <Sirens> id
  <lightSettings> ────► carcols.meta  <Lights> id
  <liveries> ─────────► livery-slots in de .ytd van het model

carcols.meta
  <Kits>…<visibleMods>…<modelName> ──► stream/<naam>.yft (mod-onderdeel)
```

Bron: GTAMods en Dawnstar (`community`), samengevat uit `VehicleTool/docs/CARCOLS_CARVARIATIONS_REFERENCE.md`. In het kort:

- `carcols.meta` zegt nergens voor welk voertuig het is. De koppeling loopt via `carvariations.meta`: `modelName` → `kitName` → kit in `carcols`. (GTAMods, `community`)
- Eén `carcols.meta` mag dus meerdere voertuigen bedienen; dat is normaal in packs.
- Een `.yft` voor elk `visibleMods/modelName` moet ergens in `stream/` staan.
- Klopt een naam in deze keten niet (`modelName`, `txdName`, `handlingId`, `gameName`), dan spawnt het voertuig volgens `docs/plan.md` §3 "stil" niet, zonder foutmelding. Het plan dacht ook dat convert.cfx.rs die namen controleert. `aanname`.

---

## 3. `vehicles.meta`: de velden die er het meest toe doen

| Veld | Wat | Regel | Status |
|------|-----|-------|--------|
| `modelName` | spawnnaam; naam van de `.yft` | gelijk aan de bestandsnaam zonder extensie | `community` |
| `txdName` | naam van de `.ytd` | meestal gelijk aan `modelName` | `community` |
| `handlingId` | verwijzing naar `handlingName` in `handling.meta` | moet bestaan; hoofdletters gangbaar; "max. ~14 tekens" | lengte: `aanname` (Q-M6); hoofdletters: Q-M8 |
| `gameName` | sleutel van het tekstlabel met de naam | "max. ~11 tekens" | `aanname` (Q-M6) |
| `vehicleMakeName` | sleutel van het merklabel | | `community` |
| `type` | `VEHICLE_TYPE_*`, zie de lijst hieronder | enum | `tested` (gelezen) |
| `vehicleClass` | `VC_SUPER`, `VC_EMERGENCY`, `VC_HELICOPTER`, `VC_MOTORCYCLE`, … | **tekst, geen getal, en ook bij helikopters en motoren** | `tested` (gelezen); koppeling naar `GetVehicleClass` 0–22: Q-M5 |
| `wheelType` | `VWT_*`, zie de lijst hieronder | logische combinatie met type/klasse (backlog) | `community` |
| `layout` | `LAYOUT_LOW_RESTRICTED` enz. | vanilla, of uit `vehiclelayouts.meta` | `community` |
| `audioNameHash` | geluid van een vanilla-voertuig, of eigen audio | moet bestaan | `community` |
| `flags` | `FLAG_SPORTS FLAG_RICH_CAR …` | spaties ertussen | `tested` (gelezen) |
| `lodDistances`, `HDTextureDist` | renderafstanden | | `community` |
| `txdRelationships` | parent/child-keten voor textures | zie [textures.md](textures.md#txdrelationships) | `community` |

**`VEHICLE_TYPE_*`** (uit `docs/plan.md` §6, gelijk aan `GetVehicleTypeRaw`; `official` volgens de native-docs): `NONE` = -1, `CAR` = 0, `PLANE` = 1, `TRAILER` = 2, `QUADBIKE` = 3, `DRAFT` = 4, `SUBMARINECAR` = 5, `AMPHIBIOUS_AUTOMOBILE` = 6, `AMPHIBIOUS_QUADBIKE` = 7, `HELI` = 8, `BLIMP` = 9, `AUTOGYRO` = 10, `BIKE` = 11, `BICYCLE` = 12, `BOAT` = 13, `TRAIN` = 14, `SUBMARINE` = 15.

**`VWT_*`** (uit `docs/meta_reference_and_load_order.md` §8): `VWT_SPORT`, `VWT_MUSCLE`, `VWT_LOWRIDER`, `VWT_SUV`, `VWT_OFFROAD`, `VWT_TUNER`, `VWT_BIKE`, `VWT_HIEND`, `VWT_SUPERMOD1` t/m `VWT_SUPERMOD5`. Doel voor later: per klasse/type een passende set, en een waarschuwing bij een onlogische combinatie (bijv. een motor zonder `VWT_BIKE`).

**Fout in `docs/plan.md` §4:** daar stond `<vehicleClass>6</vehicleClass>` en "alleen voor auto's". In echte bestanden is het `VC_SUPER` enz., ook voor helikopters (`VC_HELICOPTER`) en motoren (`VC_MOTORCYCLE`). `tested` (gelezen, 62 entries buiten DriveV).

**Naam in het spel.** Onze kennisbasis heeft al een geteste valkuil (`info/natives/text.md`): met `BeginTextCommandDisplayText` werkte een `AddTextEntry`-sleutel van 16 tekens, van 20 of meer niet (17–19 niet getest); `GetLabelText` vond de lange sleutel wel, en de help-tekst werkte met 22. Voor `gameName` dus: kort houden. Dat raakt ook Q-M6. Een pack-voorbeeld met `AddTextEntry` staat in `veh_names.lua` van [VehiclePack](https://github.com/S0L0LEVELING/vehiclepack) (`community`). Let op: dat is een `.lua`-bestand in een voertuig-resource (zie de Lua-regel in [validation_rules.md](validation_rules.md)).

---

## 4. Volgorde in `fxmanifest.lua`

`docs/meta_reference_and_load_order.md` noemde dit de "team-standaard" (`aanname`, nooit getest):

1. `carcols.meta` → `CARCOLS_FILE`
2. `carvariations.meta` → `VEHICLE_VARIATION_FILE`
3. `contentunlocks.meta` → `CONTENT_UNLOCKING_META_FILE`
4. `handling.meta` → `HANDLING_FILE`
5. `shop_vehicle.meta` → `VEHICLE_SHOP_DLC_FILE`
6. `vehiclelayouts.meta` → `VEHICLE_LAYOUTS_FILE` (vlak boven `vehicles.meta`)
7. `vehicles.meta` → `VEHICLE_METADATA_FILE` (altijd als laatste)

De uitvoer van convert.cfx.rs (`kriegerty2`) gebruikt een andere volgorde (dlctext, layouts, handling, vehicles, carcols, variations, shop). Of de volgorde in het manifest iets uitmaakt, is open (Q-S7). Wat FiveM met elke regel doet (globs, ontbrekende bestanden), staat in §10.

Voorbeeld uit de oude notities, ingekort (zonder `contentunlocks` en `shop_vehicle`), met `files` en `data_file` per bestand:

```lua
files {
    'common/carcols.meta',
    'common/carvariations.meta',
    'common/handling.meta',
    'common/vehiclelayouts.meta',
    'common/vehicles.meta',
}

data_file 'CARCOLS_FILE'           'common/carcols.meta'
data_file 'VEHICLE_VARIATION_FILE' 'common/carvariations.meta'
data_file 'HANDLING_FILE'          'common/handling.meta'
data_file 'VEHICLE_LAYOUTS_FILE'   'common/vehiclelayouts.meta'
data_file 'VEHICLE_METADATA_FILE'  'common/vehicles.meta'
```

---

## 5. Minimale set per type: de bronnen spreken elkaar tegen

| Bron | Auto / motor | Heli / vliegtuig / boot | Trailer |
|------|--------------|-------------------------|---------|
| `docs/plan.md` §5 | vehicles, handling, carcols, carvariations, dlctext, shop_vehicle | vehicles, handling, carcols, carvariations, dlctext | vehicles, carcols, carvariations |
| `docs/meta_reference_and_load_order.md` §3 | vehicles, handling, carcols, carvariations, dlctext | idem | vehicles, carcols, carvariations |
| `VehicleTool/docs/Naamloos.canvas` | vehicles, handling, carcols, carvariations ("dlctext en shop_vehicle worden nooit gebruikt in FiveM") | – | – |
| `VehicleTool/checks.py` | vehicles, handling, carcols, carvariations, dlctext, shop_vehicle (voor **elk** type; vehiclelayouts optioneel) | idem | idem |
| Echte resource `strman` (auto) | vehicles, handling, carvariations (het manifest noemt ook `carcols`, maar dat bestand ontbreekt) | – | – |
| Echte resource `zaccflatlit` (trailer) | – | – | vehicles, handling, carvariations (het manifest noemt ook `carcols` en `vehiclelayouts`, maar die ontbreken) |
| Rapporten van maart (de 8 resources met een recent rapport, van de 10 van de oude server) | 5× zonder shop_vehicle, 3× zonder dlctext, 3× zonder carcols (o.a. de heli's `bell505` en `dc_mdheli`, en de auto `bow`) | | |

Volgens `docs/plan.md` §5 erft een trailer zijn handling van het voertuig dat hem trekt (`aanname`).

Conclusie: niemand heeft getest wat écht nodig is. Dat wordt test Q-S8 op de dev-server: een voertuig steeds met één bestand minder starten, en kijken wat er misgaat (spawnen, naam, kleuren, mods, sirenes).

---

## 6. Modkits: `kitName` en `id`

| Wat | Status |
|-----|--------|
| `kitName` moet exact gelijk zijn in `carvariations` en `carcols` | `community` (Dawnstar, GTAMods) |
| Gangbare naam: `<id>_<model>_modkit`, bijv. `64378_kriegerty2_modkit` | `tested` (gelezen) |
| Het `id` moet uniek zijn over alles wat de server laadt (vanilla en andere packs); dubbel = kits overlappen, LSC-opties breken | `community` |
| Vanilla gebruikt o.a. de bereiken 83–91 en 96–453 (met uitzonderingen) en 999 (een placeholder, met hydraulics te maken). Bron: de kitName-lijst van Mentozz (Cfx-forum, 2021); geen garantie na latere game-updates | `community` |
| Geldig bereik 0–1023 (GTAMods); hoger kan "overflowen" | **twijfel**: in onze testdata hebben kits ook de id's `1101`–`1105`, `3995` en `64378` (Q-M4). Let op: `941` (kriegerty2) is een licht-id en `6001`–`6013` (USSS) zijn sirene-id's; die tellen niet als kit. In de downloads van 21 okt liggen minstens 85 van de 241 kit-id's die we konden lezen boven 1023, tot `123123135` (`PLOKS_CARS`, `yPG205t16`); acht `carcols.meta` waren niet te lezen |
| Add-ons met kits die de naam van een vanilla-kit dragen | `tested` (gelezen, downloads 21 okt): `PLOKS_CARS/[FORD]/wildtrak/carcols.meta` definieert `268_hermes_modkit` en `269_revolter_modkit` (Hermes en Revolter zijn vanilla-voertuigen; of dit ook hun kit-id's zijn, is nog niet nagekeken), en vijf auto's definiëren `0_default_modkit` (id 0) opnieuw, leeg. Wat dat in de game doet (vervangt het de vanilla-kit?), is een test (Q-M19) |
| Lege "placeholder"-kits met hetzelfde id | `tested` (gelezen): elf auto's in `PLOKS_CARS` hebben elk een eigen kit met id 135 en nul onderdelen |
| Nooit automatisch hernummeren; wel een index bijhouden | eerdere keuze (zie [decisions.md](decisions.md), B9) |
| Een id met de hand reserveren: in VehicleTool een regel in `pack/modkit_ids.json` met `"source": "manual"` (zonder `handlingId` = gereserveerd); zo'n regel blijft staan en blokkeert dat id | VehicleTool (`README.md`, `PACK_VALIDATION.md`) |

Let op: de VehicleTool-template zet bij elk voertuig `id 10000`. De vier pack-voertuigen hebben daardoor allemaal hetzelfde kit-id (zie K18 in [duplicates_and_conflicts.md](duplicates_and_conflicts.md)).

---

## 7. `carvariations.meta`: wat de velden doen (`community`, GTAMods)

- `colors`: max. 25 kleurvariaties per voertuig. `indices`: 1 primary, 2 secondary, 3 pearlescent, 4 wiel, 5 extra1 (vaak interieur), 6 extra2 (vaak dashboard); een 7e waarde wordt genegeerd.
- `liveries`: positie = livery-nummer in de `.ytd`. Zet geen modkit-liveries (`VMT_LIVERY_MOD`) of livery2 aan.
- `kits`: de `kitName` uit `carcols`. Bij politievoertuigen ontbreekt `<kits>` soms, of is het aangepast.
- `plateProbabilities`: kansen, samen 100. Een eigen plaatnaam moet in `carcols` bestaan als `TextureSetName`.
- `lightSettings` / `sirenSettings`: id uit `carcols` (`Lights` / `Sirens`).

## 8. `carcols.meta`: wat de secties doen (`community`, GTAMods)

- `Kits`: `kitName`, `id`, `kitType`, `visibleMods` (`modelName` = `.yft`, `type` zoals `VMT_SPOILER`, `VMT_LIVERY_MOD`, `bone`, `collisionBone`), `liveryNames` (alleen voor liveries in de `.ytd`).
- `Lights` en `Sirens`: eigen `id`, te gebruiken vanuit `carvariations`. Daarnaast koplamp- en achterlichtinstellingen (sequencers, coronas).
- `Wheels`: eigen wielen (de wielen-packs in `research/`).
- Sommige globale data (bepaalde kentekens, kleuren, xenon-standaarden) kan een add-on niet toevoegen; die hoort bij de vanilla `carcols.ymt`.

---

## 9. Templates die we al hebben

| Waar | Wat | Bruikbaar? |
|------|-----|------------|
| `VehicleTool/templates/meta/` | `vehicles`, `handling`, `carvariations`, `carcols`, `dlctext`, `shop_vehicle` met placeholders (`MODEL_NAME_HERE`, `HANDLING_ID_HERE`, …) | Deels. `vehicles.template.meta` heeft nette comment-secties, maar is een **auto**-basis (`LAYOUT_LOW`, `VDT_SULTAN`, `VWT_SPORT`) en wordt ook voor motor, heli en boot gebruikt; `txdRelationships` leeg. `carvariations` verwijst naar `0_default_modkit`, niet naar de eigen kit. `carcols` heeft een vast kit-id (10000). `dlctext` en `shop_vehicle` hebben een verzonnen root-element. `handling.template.meta` wordt niet gebruikt: de generator staat vast in `ui.py`. Geen template voor `vehiclelayouts` |
| `VehicleTool/templates/handling/*.json` | handling-bereiken per klasse | zie [handling.md](handling.md) |
| `old/oldversion/src/templates/*_handling.meta` | handling-meta per type (auto, boot, heli, motor, vliegtuig, standaard) | **Nee**: heli en vliegtuig gebruiken klassen die niet bestaan (`CHeliHandlingData`, `CPlaneHandlingData`), de motor een auto-klasse; boot, heli en vliegtuig delen gekopieerde autowaarden. Alleen de auto-template is plausibel (zie [handling.md](handling.md)) |
| `VehicleOptimizer/data/*.meta` | meta's met `{placeholders}` | **Nee**: `vehicles` en `handling` zijn van een vliegtuig (Alkonost, `CFlyingHandlingData`, 55.500 kg), `carcols` en `carvariations` van een `xc90`, met twee verschillende kits |

Regel uit `VehicleTool/templates/README.md`: alleen de handling-templates zijn echt per klasse, type en dienstvariant (politie, ambulance); de andere meta-templates zijn structuur met placeholders, want ze bevatten veel voertuigeigen data (namen, lichten, kits, layouts, audio).

Wat we nog nodig hebben: één set **correcte** templates per type, gemaakt uit echte vanilla-bestanden (Q-M12). Een template geeft ook de vaste volgorde van de velden, zodat de tool een meta altijd in dezelfde vorm kan wegschrijven (wens van Mark).

---

## 10. `data_file`: de officiële types en wat FiveM ermee doet

### Officiële lijst

De pagina [Data files](https://docs.fivem.net/docs/game-references/data-files/) op docs.fivem.net noemt 89 types (`official`, gelezen 21 okt 2026). Voor voertuigen tellen vooral: `VEHICLE_METADATA_FILE`, `HANDLING_FILE`, `VEHICLE_VARIATION_FILE`, `CARCOLS_FILE`, `VEHICLE_LAYOUTS_FILE`, `VEHICLE_SHOP_DLC_FILE`, `CONTENT_UNLOCKING_META_FILE`, `VEHICLEEXTRAS_FILE`, `VFXVEHICLEINFO_FILE`, `PTFXASSETINFO_FILE`, `WEAPONINFO_FILE`, `DLC_ITYP_REQUEST`, `AMBIENT_VEHICLE_MODEL_SET_FILE`, de `AUDIO_*`-types en de drie `FIVEM_LOVES_YOU_*`-types. De pagina zegt niet welke types in FiveM-resources werken.

Niet in de lijst, maar wel gezien:

| Type | Waar |
|------|------|
| `DLCTEXT_FILE` | convert.cfx.rs (`kriegerty2`) |
| `VEHICLE_SHOP_FILE` | convert.cfx.rs (`kriegerty2`) |
| `CARCONTENTUNLOCKS_FILE` | `lds-lorevehicles` (downloads 21 okt) |
| `CAR_ADDON_CONTENT_UNLOCKS`, `VEHICLE_SETTINGS_FILE` | `Lore_Friendly_Car_Pack` (downloads 21 okt) |

Wat FiveM met zo'n type doet (stil negeren of een melding), is Q-M15.

### Wat FiveM met een `data_file`-regel doet

`official`, gelezen in de FiveM-broncode (`code/components/citizen-resources-gta/src/ResourcesTest.cpp` en `citizen-resources-core/src/ResourceMetaDataComponent.cpp`, master 20 okt 2026). Nog niet in-game getest.

- De client verwerkt de regels als de resource start. Elk pad gaat door dezelfde glob als `files`. `**` staat voor nul of meer mappen en werkt. `*` en `?` werken alleen betrouwbaar in de bestandsnaam, het laatste deel van het pad: bij een `*` in een mapnaam laat de code het teken vóór de `/` weg, zodat `data/*/handling.meta` niets vindt, en een `?` in een mapnaam telt als gewoon teken. **Hoofdlettergevoelig**: de namen worden met `std::regex` vergeleken, zonder `icase`.
- Elk gevonden bestand wordt met het opgegeven type in de laadlijst van de game gezet. Een glob die alles vindt (`data/**/*.meta`), zet dus **elk** bestand onder dat type. De Lore-pack doet dat voor negen types tegelijk (Q-S13).
- Vindt een pad **zonder** `*` niets, dan geeft FiveM het pad toch aan de game. Daardoor werken de audio-regels: `'audio/x_game.dat'` bestaat niet als bestand, maar het pad komt bij de game, die `x_game.dat151.rel` laadt (dat laatste is `aanname`: zo staat het in werkende resources, zie [audio.md](audio.md)). Vindt een glob **met** `*` niets, dan gebeurt er stil niets.
- De glob kijkt naar de bestanden van de resource zoals de client ze heeft, en de client heeft alleen wat hij gedownload heeft. Daarom moeten de meta's ook in `files {}` staan (`aanname`, afgeleid; R15 in [validation_rules.md](validation_rules.md)).
- De server controleert `data_file` niet. Bij het starten van een resource meldt hij wel ontbrekende `files`, `client_script`, `server_script` en `shared_script` ("could not find file `…` (defined in fxmanifest.lua:12)"), maar alleen als het begin van het pad niet bestaat: een glob in een bestaande map die niets vindt (`data/*.meta`) meldt hij niet. Ook de oversized-bestanden meldt hij, en telt die op in "Started resource x (n warnings)" (`ServerResources.cpp`).
- Aparte regel in de code: een resource met `data/ai/vehicleweapons_caracara.meta` krijgt geen enkel `data_file` geladen (oude "assault vehicles"-packs die crashten).

---

## Links

- GTAMods: [Vehicles.meta](https://gtamods.com/wiki/Vehicles.meta), [Handling.meta](https://gtamods.com/wiki/Handling.meta), [Carcols.ymt](https://gtamods.com/wiki/Carcols.ymt), [Carvariations.ymt](https://gtamods.com/wiki/Carvariations.ymt)
- Dawnstar: [vehicles](https://docs.dwnstr.com/data-files/vehicles), [handling](https://docs.dwnstr.com/data-files/handling), [carcols](https://docs.dwnstr.com/data-files/carcols), [carvariations](https://docs.dwnstr.com/data-files/carvariations)
- Vanilla kitName-lijst (Mentozz, 2021): https://forum-cfx-re.akamaized.net/original/4X/6/9/9/6990851be012e0b402f55585c38322eb4b676a35.txt
- FiveM: [Data files](https://docs.fivem.net/docs/game-references/data-files/) (de officiële lijst), [Resource manifest](https://docs.fivem.net/docs/scripting-reference/resource-manifest/resource-manifest/) ("This directive supports globbing")
- Meer in [sources.md](sources.md).

## Beperkingen

- Niets in dit document is in-game getest, behalve wat "gelezen" heet (dat is: zo staat het in bestanden).
- `wheelType`-beleid (welke `VWT_*` bij welke klasse) staat nog op de backlog uit `docs/meta_reference_and_load_order.md` §8.
