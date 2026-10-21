# FivemVehicleTool

> Naam, voorlopig: **vehicletools**. Het in-game deel heet `dev_vehicletools` (B17 in [doc/decisions.md](doc/decisions.md)).

Een all-in-one voertuigtool voor FiveM:

- een in-game editor: voertuig spawnen en de handling aanpassen binnen "normale" grenzen, met een schakelaar om die grenzen uit te zetten;
- een check op te grote textures en modellen (FiveM's "oversized assets"), en liefst een manier om ze te verkleinen;
- controle van meta-bestanden op de regels en de naamgeving, met templates zodat waarden altijd op dezelfde manier staan en ontbrekende waarden uit een template komen;
- een vaste mapstructuur voor voertuig-resources, ook met meerdere liveries.

**Fase: onderzoek.** De tool zelf wordt nog niet gebouwd. Op de dev-server staat een testpakket waarmee we de vragen in de game beantwoorden ([doc/test_pack.md](doc/test_pack.md)).

## Wat staat waar

| Map | Wat |
|-----|-----|
| [`doc/`](doc/README.md) | Alle documentatie (Nederlands). Begin bij `doc/README.md` |
| [`research/scripts/`](research/scripts/README.md) | Scripts voor het onderzoek; ze lezen alleen |
| [`archive/`](archive/README.md) | De eerste versie van deze repo (feb 2026), niet meer in gebruik |

## Keuzes tot nu toe (21 okt 2026)

- Eén resource per voertuig, met de liveries erbij (B1)
- Packs splitsen naar losse resources (B2)
- Eén tool als het kan, anders twee (B3)
- Volgorde: structuur en templates → manifest → textures → handling-editor (B12)
- Een voertuig-resource heet zoals het model, met `data/`, `stream/` (met `mods/` en `liveries/`) en `audio/`, en een vast manifest (B24); livery soort 4 in dezelfde resource (B23)
- De naam in de game staat in het manifest: `vehicle_label '<modelName>' '<naam>'` (B26)
- Een eigen testpakket, ook met expres gemaakte fouten (B25)
- Alles wat in FiveM draait volgt Marks standaard: `dev_<naam>`, geen dependencies behalve oxmysql, framework-koppeling via bridge-haken, NUI in React + Vite (V1–V8)

Meer in [doc/decisions.md](doc/decisions.md).

## Voertuigbestanden

Voertuigen van anderen komen niet in deze repo: ze zijn niet van ons en te groot. `.gitignore` houdt `.yft`, `.ytd`, `.rpf` en dergelijke buiten git. Het testpakket staat alleen op de dev-server; in de repo staan de beschrijving ([doc/test_pack.md](doc/test_pack.md)) en het script dat het maakt ([research/scripts/](research/scripts/README.md)).
