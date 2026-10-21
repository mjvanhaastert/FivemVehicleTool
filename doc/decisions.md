# Beslissingen

Wat Mark gekozen heeft, wat eerder besloten is (in de oude notities "team-standaard" of "teambeleid" genoemd), wat vastligt door Marks standaard, en wat nog gekozen moet worden.
Per beslissing: de bron, de status, en een voorstel.

Status: **gekozen** (Mark heeft gekozen, met datum), **vast** (geldt door de standaard), **houden?** (eerder besloten, voorstel om te houden; Mark bevestigt), **herzien** (eerder besloten, maar nieuwe kennis zet het op losse schroeven), **open** (nog te kiezen).

Bijgewerkt: 21 okt 2026.

---

## Gekozen door Mark (21 okt 2026)

| # | Keuze | Wat het betekent | Nog uit te zoeken |
|---|-------|------------------|-------------------|
| B1 | **Eén resource per voertuig.** Liveries horen bij het voertuig en gaan mee in dezelfde resource, met een duidelijke mapstructuur | Livery soort 1, 2 en 3 gebruiken hetzelfde model en horen dus in de resource van dat voertuig. Soort 4 (een apart model per uiterlijk, zoals `lsfd` … `lsfd5`) komt ook in de resource van het basisvoertuig (B23). De indeling binnen de resource: B24 | – |
| B2 | **Packs splitsen** naar losse resources | Wat beter is voor de server (één grote resource of veel kleine): eerste antwoord uit de FiveM-broncode in [folder_structure.md](folder_structure.md) §3. Kort: geen limiet op het aantal resources, tijdens het spelen geen verschil; losse resources kosten vooral bij de eerste join en zijn goedkoper bij elke update | Q-S10 (meten) |
| B3 | **Eén tool als het kan, anders twee** | Het plan van maart koos twee tools omdat FiveM geen bestanden zou kunnen lezen of schrijven. Server-side kan dat binnen de sandbox wel. Of scannen en controleren in één FiveM-resource kan, beslissen Q-A1 en Q-A2 | Q-A1, Q-A2, Q-A4 |
| B12 | **Volgorde:** 1 structuur en templates, 2 manifest, 3 textures, 4 handling-editor | Het onderzoek en het testpakket volgen deze volgorde ([open_questions.md](open_questions.md), [test_pack.md](test_pack.md)) | – |
| B16 | **Het project komt in de repo `mjvanhaastert/FivemVehicleTool`** | De oude code van die repo staat daar in `archive/` (PR #1, samengevoegd op 21 okt). De oude lokale repo (`TrueRP/VehicleEditor`) staat met de rest van het oude werk in `archive/` van de projectmap | – |
| B17 | **Naam, voorlopig: "vehicletools".** Het in-game deel heet dus `dev_vehicletools` (een script voor anderen, standaard V6) | Mark (21 okt): "laten we het maar houden op vehicletools voor nu". De andere namen hieronder blijven bewaard voor als hij later toch iets anders wil | – |
| B25 | **We maken een eigen testpakket**, ook met gevallen waarin we expres een fout zetten | Gebouwd op 21 okt: `resources/[vehicletests]/`, 55 gevallen. Eerste uitkomsten in de game: [test_pack.md](test_pack.md#uitkomsten). `ensure [Vehicles]` staat uit in `server.cfg` (back-up `server.cfg.bak-2026-10-21-vehicletests`). Zie [test_pack.md](test_pack.md) | welke voertuigen we nog zoeken |
| B24 | **Indeling van een voertuig-resource: het voorstel uit [folder_structure.md](folder_structure.md) §3, met de `modelName` als naam van de resource** (dus `kriegerty2/`, niet `veh_kriegerty2/`) | Mark (21 okt): "voor de folder structure, gaan we voor de modelName als naam van de resource, de andere keuzes gaan we voor de voorstel die je zelf doet". Dus: `data/` met vaste namen, een manifest met vaste paden en `files { 'data/*.meta' }`, `stream/` met `mods/` en `liveries/`, `audio/`, geen scripts. De gevallen in het testpakket heten `vt_<nn>_<onderwerp>`: dat zijn testgevallen, geen voertuigen. In de game getest (21 okt, `tested`): `vt_00_baseline`, en liveries uit `stream/liveries/` (`vt_13b`) en onderdelen uit `stream/mods/` (`vt_11`) | een `modelName` die al de naam van een andere resource is |
| B23 | **Livery soort 4** (een apart model per uiterlijk) **in de resource van het basisvoertuig** | Voorstel overgenomen (21 okt). Elk model staat naast het basismodel in `stream/`, met een `Item` per model in dezelfde meta's | – |
| B26 | **De naam van een voertuig staat in het manifest** (keuze b), en `dev_vehicletools` zet de tekst | Voorstel overgenomen (21 okt). Vorm: `vehicle_label '<modelName>' '<naam>'`, twee waarden, zodat ook een familie van modellen (soort 4) per model een naam kan hebben. Getest met `vt_00_baseline` (21 okt, `tested`): de client leest `vehicle_label` en `vehicle_label_extra` (de naam als JSON-tekst) met `GetResourceMetadata`, ook bij een resource zonder scripts; `AddTextEntry` vanuit een andere resource werkt, en de game toont "Acura TL Type-S" in plaats van "NULL". In de downloads heeft 152 van de 362 gelezen voertuigen geen naam | hoe `dev_vehicletools` namen zet voor resources die later starten |

### Andere namen (B17)

Mark koos voorlopig "vehicletools". Deze lijst bleef over; de naam wordt ook de naam van de repo (GitHub stuurt de oude URL door na een hernoeming) en van de resource: `dev_<naam>`.

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

Waarom de lijst er was: "Vehicle Tools" bestaat al als script op het Cfx-forum en is algemeen. Als werknaam is dat geen probleem; bij publiceren nog eens kijken. Ook liever niet: "Dyno" (een gewone functie in tuning-scripts) en "MOT" of "APK" (er bestaat al een MOT-keuringsscript; "apk" leest buiten Nederland als Android). Kort gezocht op 21 okt 2026; voor de andere namen vonden we geen FiveM-project met dezelfde naam, maar dat is geen garantie.

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
| B22 | Code uit `vehiclehandler` (GPL-3.0, ox_lib) niet overnemen; alleen ideeën | Zo doen | Licentie en standaard V2; zie [inventory.md](inventory.md) |
| B18 | Handling-grenzen: hoe bepalen we "normaal"? Per klasse uit vanilla-data (voorstel), of uit de Eddlm-ranges, of uit onze class-baselines? | Vanilla per klasse | Marks wens: grenzen met een schakelaar om ze uit te zetten. Zie [handling.md](handling.md) en Q-H4 |
| B19 | Mag de tool textures zelf verkleinen (en dus `.ytd`'s herschrijven), of alleen melden en adviseren? | Eerst melden; herschrijven na Q-T4 | Hangt af van Q-T4; het grootste technische risico |
