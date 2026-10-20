# Bronnen

Alle links uit de oude notities en de code, één keer, per onderwerp. "Gebruikt in" zegt waar we de bron al voor gebruikten.
Labels van de bron zelf: `official` (FiveM/Cfx of Rockstar-data), `community` (wiki, forum, andermans tool).

---

## FiveM (official)

| Bron | Waarvoor |
|------|----------|
| [GetVehicleClass](https://docs.fivem.net/natives/?_0x29439776AAA00A62) | klassen 0–22 |
| [GetVehicleType](https://docs.fivem.net/natives/?_0xDE73BC10) | `VEHICLE_TYPE_*` |
| [SetVehicleHandlingFloat](https://docs.fivem.net/natives/?_0x90DD0F9DDA78B8BF) | handling schrijven |
| [GetVehicleHandlingFloat](https://docs.fivem.net/natives/?_0x358C9DAF02C98D9D) | handling lezen |

## FiveM-broncode (official, gelezen op 20 okt 2026)

Gelezen om de oude editor te beoordelen. Commit `8f3b0fad` van [citizenfx/fivem](https://github.com/citizenfx/fivem) en `34321568` van [citizenfx/natives](https://github.com/citizenfx/natives).

| Bestand | Waarvoor |
|---------|----------|
| `code/components/handling-loader-five/src/HandlingLoader.cpp` | handling-natives: kopie per voertuig, globaal tegenover per voertuig, eenheden, hoofdletters, sub-klassen, deling door nul |
| `code/components/citizen-scripting-lua/src/LuaScriptRuntime.cpp`, `LuaIO.cpp`, `LuaOS.cpp` | `io` en `os` server-side, binnen de sandbox |
| `code/components/citizen-scripting-core/src/FilesystemPermissions.cpp`, `code/components/vfs-impl-server/src/Manager.cpp` | wat een resource mag lezen en schrijven |
| `MetadataScriptFunctions.cpp` | `SaveResourceFile` |
| `ext/native-decls/` en `citizenfx/natives` `VEHICLE/` | o.a. `SetVehicleHandlingFloat`, `ModifyVehicleTopSpeed`, `SetVehicleMaxSpeed`, `GetVehicleTypeRaw` |

Gelezen op 21 okt 2026 (zelfde commit), voor de structuur, het manifest en de textures:

| Bestand | Waarvoor |
|---------|----------|
| `code/components/citizen-server-impl/src/ServerResourceList.cpp`, `ServerResourceMounter.cpp` | hoe de server resources vindt: categorieën met haken, "does not have a resource manifest", dubbele namen ([folder_structure.md](folder_structure.md) §5) |
| `code/components/citizen-server-impl/src/ResourceStreamComponent.cpp` | `stream/` recursief, alleen de bestandsnaam, en de oversized-melding met de grenzen 16/32/48/64 MiB ([textures.md](textures.md#de-melding-van-fivem)) |
| `code/components/citizen-server-impl/src/ResourceFilesComponent.cpp` | `.y*`-bestanden uit `stream/` gaan niet mee in `files` (behalve `.ytyp`) |
| `code/components/citizen-resources-core/src/ResourceMetaDataComponent.cpp` | hoe globs werken (`*`, `?`, `**`, hoofdlettergevoelig) |
| `code/components/citizen-resources-gta/src/ResourcesTest.cpp` | wat de client met `data_file` doet ([meta_files.md](meta_files.md) §10) |

## Meta-bestanden (community)

| Bron | Waarvoor |
|------|----------|
| [GTAMods: Vehicles.meta](https://gtamods.com/wiki/Vehicles.meta) | velden van `vehicles.meta` |
| [GTAMods: Carcols.ymt](https://gtamods.com/wiki/Carcols.ymt) (en [#type](https://gtamods.com/wiki/Carcols.ymt#type)) | kits, kit-id, `VMT_*`-types, lichten, sirenes |
| [GTAMods: Carvariations.ymt](https://gtamods.com/wiki/Carvariations.ymt) | kleuren, liveries, kits, kentekens |
| [Dawnstar: index](https://docs.dwnstr.com/) | handleidingen per bestand |
| [Dawnstar: vehicles](https://docs.dwnstr.com/data-files/vehicles) | |
| [Dawnstar: handling](https://docs.dwnstr.com/data-files/handling) | |
| [Dawnstar: carcols](https://docs.dwnstr.com/data-files/carcols) | modkits, `modelName` van onderdelen |
| [Dawnstar: carvariations](https://docs.dwnstr.com/data-files/carvariations) | siren- en light-id's |
| [Vanilla kitName-lijst (Mentozz, 2021)](https://forum-cfx-re.akamaized.net/original/4X/6/9/9/6990851be012e0b402f55585c38322eb4b676a35.txt) | bezette kit-id's in vanilla |
| [GTA V-kleurentabel](https://gtaforums.com/topic/836998-list-of-gta-5-vehicle-colors/) | kleur-indices in `carvariations` |
| [DurtyFree: gta-v-data-dumps](https://github.com/DurtyFree/gta-v-data-dumps) | lijsten (audio-namen, modellen); onze kennisbasis gebruikt hem al voor peds en wapens |

## Handling: editors en rekenhulpen (community)

| Bron | Waarvoor | Status |
|------|----------|--------|
| [Eddlm Handling Tools (web)](https://eddlm.github.io/Handling-Tools/handling) en [broncode](https://github.com/Eddlm/Handling-Tools) | velden, eenheden, min/max; Mark wil "alles wat de website heeft" | ranges overgenomen in `docs/plan.md` §9 |
| [carmineos/fivem-handling-editor](https://github.com/carmineos/fivem-handling-editor) | bestaande in-game editor | nog niet bekeken (Q-H11) |
| [STACHY225/BabiczHandlingEditor](https://github.com/STACHY225/BabiczHandlingEditor) | bestaande editor | nog niet bekeken (Q-H11) |
| [kerminal/vehicleDebug](https://github.com/kerminal/vehicleDebug) | debug-tool | nog niet bekeken (Q-H11) |
| [DriveV FiveM-port](https://github.com/Weilher420/DriveV_Fivem_port) | realistische handling voor alle vanilla-voertuigen; staat in `research/DriveV` | bekeken (README in `research/DriveV`) |

## Omzetten en uitpakken (community)

| Bron | Waarvoor | Status |
|------|----------|--------|
| [convert.cfx.rs (ZeroDream)](https://convert.cfx.rs/en) | GTA-mod → FiveM-resource; onze variant A | uitvoer bekeken (`kriegerty2`) |
| [VIRUXE/rpf-cli](https://github.com/VIRUXE/rpf-cli) | `.rpf` uitpakken via de command line | getest in maart: verwacht een RPF7-archief; een losse `.ytd` (RSC7) gaat niet |
| [Piliii/RPF-Extractor](https://github.com/Piliii/RPF-Extractor) | Python-schil om rpf-cli | basis van `trp_rpf_to_fivem_converter` |
| [zfbx/fivem-meta-splitter](https://github.com/zfbx/fivem-meta-splitter) | pack-meta splitsen | nog niet bekeken |
| [S0L0LEVELING/vehiclepack](https://github.com/S0L0LEVELING/vehiclepack) ([README](https://github.com/S0L0LEVELING/vehiclepack/blob/main/README.md), [veh_names.lua](https://github.com/S0L0LEVELING/vehiclepack/blob/main/VehiclePack/veh_names.lua)) | voorbeeld van een pack met `AddTextEntry` | bekeken |
| [SMmest3r/duplicatedTuningIdFinder](https://github.com/SMmest3r/duplicatedTuningIdFinder) | dubbele kit-id's zoeken en hernummeren | alleen als idee; wij hernummeren niet |

## Textures en assets (community)

| Bron | Waarvoor | Status |
|------|----------|--------|
| [flobros/CodeWalker.API](https://github.com/flobros/CodeWalker.API) | HTTP-API rond CodeWalker voor uitpakken en vervangen | geprobeerd (map `noneWorking`), endpoints bekend, paden lukten niet |
| [Sollumz](https://github.com/Sollumz/Sollumz) | Blender-add-on voor GTA-modellen en textures | terugvaloptie |
| OpenIV | handmatig exporteren en importeren | werkt, maar met de hand |
| Texture Magic | textures optimaliseren na uitpakken | optioneel, niet bekeken |
| [woodruffw/pyrage](https://github.com/woodruffw/pyrage) | **niet bruikbaar**: Python-binding voor de versleutelingstool `age`, niets met RAGE/GTA | uitgesloten |

## Scripts die in de map zitten maar niet van ons zijn

| Bron | Wat |
|------|-----|
| [QuantumMalice/vehiclehandler](https://github.com/QuantumMalice/vehiclehandler) | map `vehiclehandler/` (versie 1.4.3; GPL-3.0; vereist ox_lib); zie [inventory.md](inventory.md) |

---

## Nog te bekijken voor het onderzoek

Deze links staan nog nergens in onze notities. Ze zijn de eerste plek om de open vragen te beantwoorden.

| Bron | Voor vraag |
|------|------------|
| [FiveM: resource manifest](https://docs.fivem.net/docs/scripting-reference/resource-manifest/resource-manifest/) (sectie `data_file`) | Q-S12. Gelezen op 21 okt: "This directive supports globbing in the filename field" |
| [FiveM: data files](https://docs.fivem.net/docs/game-references/data-files/) | gelezen op 21 okt: de officiële lijst van types (Q-M1, Q-M10 klaar); Q-M2 |
| [Cfx.re: Oversized assets can and WILL lead to streaming issues](https://forum.cfx.re/t/oversized-assets-can-and-will-lead-to-streaming-issues/1761205) | Q-T1, Q-T2 |
| [Cfx.re: Virtual/physical memory for assets](https://forum.cfx.re/t/virtual-physical-memory-for-assets/1689728/4) | Q-T1 |
| [Qbox: how fxmanifests work](https://docs.qbox.re/blog/how-fxmanifests-work) (`community`) | Q-S3, Q-S12 |
| [FiveM-broncode (citizenfx/fivem)](https://github.com/citizenfx/fivem) | Q-S10 (kosten per resource); Q-T1, Q-S3 en Q-S4 zijn op 21 okt gelezen (zie boven) |
| [FiveM natives](https://docs.fivem.net/natives/) (categorie VEHICLE) | Q-H1 t/m Q-H3, Q-H10 |
| [CodeWalker (dexyfex)](https://github.com/dexyfex/CodeWalker) | Q-T4, Q-A5 (YTD lezen en schrijven) |
| [DirectXTex / texconv (Microsoft)](https://github.com/microsoft/DirectXTex) | Q-T4 (DDS opnieuw comprimeren) |
| [GTAMods: Handling.meta](https://gtamods.com/wiki/Handling.meta) | Q-H5 (grenzen per veld) |
| [Cfx.re-forum](https://forum.cfx.re/) | ervaringen met oversized assets en kit-id's |
