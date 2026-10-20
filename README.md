# FivemVehicleTool

> Werknaam. Mark kiest een nieuwe naam (lijst in [doc/decisions.md](doc/decisions.md), B17). Het in-game deel gaat `dev_<naam>` heten.

Een all-in-one voertuigtool voor FiveM:

- een in-game editor: voertuig spawnen en de handling aanpassen binnen "normale" grenzen, met een schakelaar om die grenzen uit te zetten;
- een check op te grote textures en modellen (FiveM's "oversized assets"), en liefst een manier om ze te verkleinen;
- controle van meta-bestanden op de regels en de naamgeving, met templates zodat waarden altijd op dezelfde manier staan en ontbrekende waarden uit een template komen;
- een vaste mapstructuur voor voertuig-resources, ook met meerdere liveries.

**Fase: onderzoek.** Er wordt nog niets gebouwd.

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
- Alles wat in FiveM draait volgt Marks standaard: `dev_<naam>`, geen dependencies behalve oxmysql, framework-koppeling via bridge-haken, NUI in React + Vite (V1–V8)

Meer in [doc/decisions.md](doc/decisions.md).

## Voertuigbestanden

Voertuigen van anderen komen niet in deze repo: ze zijn niet van ons en te groot. `.gitignore` houdt `.yft`, `.ytd`, `.rpf` en dergelijke buiten git. Een testpakket staat alleen beschreven ([doc/test_pack.md](doc/test_pack.md)).
