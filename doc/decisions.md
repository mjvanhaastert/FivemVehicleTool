# Beslissingen

Wat Mark gekozen heeft, wat eerder besloten is (in de oude notities "team-standaard" of "teambeleid" genoemd), wat vastligt door Marks standaard, en wat nog gekozen moet worden.
Per beslissing: de bron, de status, en een voorstel.

Status: **gekozen** (Mark heeft gekozen, met datum), **vast** (geldt door de standaard), **houden?** (eerder besloten, voorstel om te houden; Mark bevestigt), **herzien** (eerder besloten, maar nieuwe kennis zet het op losse schroeven), **open** (nog te kiezen).

Bijgewerkt: 21 okt 2026.

---

## Gekozen door Mark (21 okt 2026)

| # | Keuze | Wat het betekent | Nog uit te zoeken |
|---|-------|------------------|-------------------|
| B1 | **Eén resource per voertuig.** Liveries horen bij het voertuig en gaan mee in dezelfde resource, met een duidelijke mapstructuur | Livery soort 1, 2 en 3 gebruiken hetzelfde model en horen dus in de resource van dat voertuig. Soort 4 (een apart model per uiterlijk, zoals `lsfd` … `lsfd5`) is voor de game een eigen voertuig: zie B23. Voorstel voor de indeling binnen de resource: [folder_structure.md](folder_structure.md) §3 | B23, B24 |
| B2 | **Packs splitsen** naar losse resources | Wat beter is voor de server (één grote resource of veel kleine): eerste antwoord uit de FiveM-broncode in [folder_structure.md](folder_structure.md) §3. Kort: geen limiet op het aantal resources, tijdens het spelen geen verschil; losse resources kosten vooral bij de eerste join en zijn goedkoper bij elke update | Q-S10 (meten) |
| B3 | **Eén tool als het kan, anders twee** | Het plan van maart koos twee tools omdat FiveM geen bestanden zou kunnen lezen of schrijven. Server-side kan dat binnen de sandbox wel. Of scannen en controleren in één FiveM-resource kan, beslissen Q-A1 en Q-A2 | Q-A1, Q-A2, Q-A4 |
| B12 | **Volgorde:** 1 structuur en templates, 2 manifest, 3 textures, 4 handling-editor | Het onderzoek en het testpakket volgen deze volgorde ([open_questions.md](open_questions.md), [test_pack.md](test_pack.md)) | – |
| B16 | **Het project komt in de repo `mjvanhaastert/FivemVehicleTool`** | De oude code van die repo gaat daar naar `archive/`. De oude lokale repo (`TrueRP/VehicleEditor`) staat met de rest van het oude werk in `archive/` van de projectmap | de naam (B17) |
| B17 | **Het in-game deel heet `dev_<naam>`**: een script voor anderen (standaard V6), geen `devkit_` | Mark wil een nieuwe naam voor het project. De lijst staat hieronder | welke naam |

### Namen om uit te kiezen (B17)

De naam wordt ook de naam van de repo (GitHub stuurt de oude URL door na een hernoeming) en van de resource: `dev_<naam>`.

| Naam | Resource | Idee |
|------|----------|------|
| **Carwright** | `dev_carwright` | "-wright" is een maker (shipwright, wheelwright): bouwt en repareert auto's. Kort en uniek |
| **PitCrew** | `dev_pitcrew` | Het team dat een auto snel klaarmaakt en afstelt. Iedereen snapt het meteen |
| **Paddock** | `dev_paddock` | De plek waar raceauto's worden voorbereid en gekeurd voordat ze de baan op gaan: intake, controle, afstellen |
| **Scrutineer** | `dev_scrutineer` | De technische keuring in de autosport. Past bij het controleren; minder bij de editor |
| **VehicleForge** | `dev_vehicleforge` | Voertuigen "smeden" tot ze op de server passen. Lang als resourcenaam |
| **Chassis** | `dev_chassis` | Het onderstel waar alles op rust; past bij prioriteit 1 (structuur en templates) |
| **Fleetsmith** | `dev_fleetsmith` | Een smid voor de hele vloot: werkt over alle voertuigen van de server |
| **Homolog** | `dev_homolog` | Van homologatie: de keuring of een auto aan de regels voldoet |

Liever niet: "VehicleTool(s)" (bestaat al als script op het Cfx-forum en is te algemeen), "Dyno" (een gewone functie in tuning-scripts) en "MOT" of "APK" (er bestaat al een MOT-keuringsscript; "apk" leest buiten Nederland als Android). Kort gezocht op 21 okt 2026; voor de andere namen vonden we geen FiveM-project met dezelfde naam, maar dat is geen garantie.

---

## Vast door de standaard (okt 2026)

| # | Beslissing | Bron |
|---|------------|------|
| V1 | Het in-game deel volgt de standaard: alles `local`, logs Engels met kleur en `[RESOURCE]`, comments Nederlands, events `resource:side:action` | kennisbasis `prompt.md` §3–4 |
| V2 | Geen dependencies, behalve oxmysql als er een database is. Dus geen ox_lib, ox_target of framework | standaard §2 en §17, afspraak 18 okt 2026 |
| V3 | Framework-koppeling (sleutels, brandstof, meldingen, rechten) alleen via bridge-haken in `src/config/bridge_*.lua` | standaard §10 |
| V4 | De server beslist: elke actie van de NUI opnieuw controleren op de server (rechten, waarden, afstand) | standaard §15 en §18 |
| V5 | NUI in React + Vite | CLAUDE.md van de dev-server |
| V6 | Scriptnamen `dev_<naam>`, geen serverprefix; de oude `trp_*`-namen verdwijnen | kennisbasis `prompt.md` §3 |
| V7 | Testen op de dev-server via dolu_fivem_mcp; kennis terug naar de kennisbasis (`info/`, `data/`, `examples/`, `research/`) | kennisbasis `prompt.md` §2 |
| V8 | Schrijven alleen binnen de eigen resource (FiveM-sandbox), tenzij `add_filesystem_permission` (werkt alleen bij het opstarten). Lezen van andere resources kan wel, met `LoadResourceFile` | standaard §2, `info/runtime/sandbox.md` (getest) |

## Eerder besloten

| # | Beslissing | Bron | Status | Voorstel |
|---|------------|------|--------|----------|
| B4 | Externe tool in Python, met een simpele UI (eerst `rich` CLI, later tkinter) | `docs/plan.md` §7 | **open** | In de praktijk werden het drie UI's: Tk (VehicleTool), PyQt6 (FivemVehicleTool), CLI (converter). Kiezen na B3 en Q-A4 |
| B5 | Vaste volgorde van checks: manifest → structuur → meta → textures; textures pas als 1–3 groen zijn | `docs/plan.md` §7 | **houden?** | Houden voor fixes; de header-check van textures (alleen lezen, zie [textures.md](textures.md)) mag altijd meteen draaien |
| B6 | `.lua` in een voertuig-resource: waarschuwen, nooit automatisch verwijderen | `docs/plan.md` §7 | **houden?** | Houden; uitbreiden met escrow (`.fxap`), map-bestanden en vanilla-namen in `stream/`. De downloads van 21 okt laten zien waarom: twee packs doen bij het starten een versiecheck via HTTP en zetten `SetConvarServerInfo('tags', …)` ([test_data.md](test_data.md#downloads-in-vehicles-21-okt-2026)) |
| B7 | Niet inpakken als ZIP | `docs/plan.md` (Mark, maart) | **houden?** | Houden |
| B8 | De bron wordt nooit verplaatst; de tool kopieert naar een doel | `docs/vehicle_intake_procedure.md` §6 | **houden?** | Houden; ook dry-run en back-up (FivemVehicleTool had die) |
| B9 | Kit-id's nooit automatisch hernummeren; wel een index bijhouden en een vrij id voorstellen | `VehicleTool/README.md` | **houden?** | Houden. De downloads hebben minstens 44 kit-id's die dubbel gebruikt worden, 29 daarvan tussen verschillende packs ([test_data.md](test_data.md#downloads-in-vehicles-21-okt-2026)) |
| B10 | Meta buiten `common/` = waarschuwing `META_WRONG_LOCATION` | `docs/vehicle_intake_procedure.md` §2 | **open** | Hangt af van de indeling binnen de resource (B24) |
| B11 | Doelgroep: eerst Mark en een kleine groep, later publiek | `docs/plan.md` (Mark, maart) | **houden?** | Houden; publiek betekent: framework-onafhankelijk via de bridge (V3) |
| B13 | `dlctext.meta` en `shop_vehicle.meta` verplicht (FAIL als ze ontbreken) | `VehicleTool/AUDIT.md` (beperking 3), `docs/plan.md` §5 | **herzien** | Hun nut in FiveM is twijfelachtig (Q-M2, Q-M3); voorlopig alleen INFO. `DLCTEXT_FILE` staat niet in de officiële lijst van `data_file`-types ([meta_files.md](meta_files.md)) |
| B14 | Handling-editor alleen met ACE-recht | `docs/plan.md` §9 | **houden?** | Houden; rechten via een bridge-haak (`isAdmin`), standaard ACE |
| B15 | Export van handling: XML naar het klembord (plan) of server schrijft het bestand (oude editor) | `docs/plan.md` §9, `old/oldversion` | **open** | Allebei aanbieden? Hangt af van Q-H8 |
| B20 | Botsende stream-namen: blokkeren en melden, nooit automatisch hernoemen | VehicleTool (blokkeert); de converter en de repo hernoemden wel, en dat breekt het voertuig (K25) | **houden?** | Houden |
| B21 | Bij ordenen of samenvoegen: de meta's uit de bron overnemen; een template alleen gebruiken voor wat ontbreekt | nieuw, na K20 (VehicleTool verloor zo handling, kits en `txdRelationships`) | **voorstel** | Mark bevestigt |

## Nog te kiezen

| # | Vraag | Voorstel | Waarom nu |
|---|-------|----------|-----------|
| B23 | Livery soort 4 (een apart model per uiterlijk, zoals `lsfd` … `lsfd5`): in de resource van het basisvoertuig, of elk een eigen resource? | In de resource van het basisvoertuig: ze delen meestal handling en textures, en voor de speler is het één voertuig | Volgt uit B1; nodig voor de templates |
| B24 | Indeling binnen een voertuig-resource: naam van de resource, map voor de meta's (`data/` of `common/`), submappen in `stream/` | Zie [folder_structure.md](folder_structure.md) §3 | Prioriteit 1 (B12): zonder indeling geen templates |
| B25 | Testpakket: maken we een vaste set testvoertuigen, met één probleem per voertuig? En hoe (zie het voorstel)? | Ja; zie [test_pack.md](test_pack.md) | Mark wil dit eerst bespreken |
| B22 | Code uit `vehiclehandler` (GPL-3.0, ox_lib) niet overnemen; alleen ideeën | Zo doen | Licentie en standaard V2; zie [inventory.md](inventory.md) |
| B18 | Handling-grenzen: hoe bepalen we "normaal"? Per klasse uit vanilla-data (voorstel), of uit de Eddlm-ranges, of uit onze class-baselines? | Vanilla per klasse | Marks wens: grenzen met een schakelaar om ze uit te zetten. Zie [handling.md](handling.md) en Q-H4 |
| B19 | Mag de tool textures zelf verkleinen (en dus `.ytd`'s herschrijven), of alleen melden en adviseren? | Eerst melden; herschrijven na Q-T4 | Hangt af van Q-T4; het grootste technische risico |
