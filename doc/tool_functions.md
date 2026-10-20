# Functies van de tool

Wat een all-in-one voertuigtool voor FiveM moet kunnen, per onderdeel. Per functie: wat er al bestaat in de projectmap, waar de functie kan draaien, en welke open vraag eerst beantwoord moet zijn.
Dit is de lijst om in het onderzoek af te werken; het is nog geen ontwerp.

**Waar draait het?**
`client` = in-game, bij de speler · `server` = server-side in FiveM (Lua of JavaScript, binnen de sandbox) · `extern` = los programma op de pc.

**ID's:** elke functie heeft een ID met `F-` ervoor (`F-A1`), zodat ze niet botsen met de controles in [validation_rules.md](validation_rules.md) (`R7`, `M21`, …) en de beslissingen in [decisions.md](decisions.md) (`B1`, …).

Het plan van maart 2026 koos voor twee tools: extern voor alles met bestanden, in-game voor handling (`docs/plan.md` §2). Dat ging uit van "in FiveM kun je geen bestanden lezen of schrijven". Server-side kan dat wel, binnen de sandbox. Mark koos op 21 okt: één tool als het kan, anders twee (B3 in [decisions.md](decisions.md)). Daarom staat bij veel functies "server of extern": welke het wordt, hangt af van Q-A1 en Q-A4.

---

## Het idee in één beeld

```text
                    ┌──────────────────────── in FiveM ───────────────────────┐
  GTA-mod (.rpf) ─► │ E. intake ─► B. scannen ─► C. controleren ─► D. ordenen │
  losse resource ─► │                   │              │              │       │
  pack ───────────► │                   ▼              ▼              ▼       │
                    │            rapport (NUI)   F. textures     nette resource│
                    │                                                         │
                    │ A. in-game: spawnen ─► handling aanpassen ─► exporteren │
                    └─────────────────────────────────────────────────────────┘
                     (wat niet in FiveM kan, zoals .ytd herschrijven: extern)
```

De volgorde van de checks (B5 in [decisions.md](decisions.md)): manifest → structuur → meta → textures. Alleen-lezen controles mogen altijd; fixes pas als de stap ervoor groen is.

---

## A. In-game editor

| # | Functie | Bestaat al | Waar | Open vragen |
|---|---------|------------|------|-------------|
| F-A1 | **Voertuig kiezen en spawnen**: lijst van vanilla en add-on voertuigen, zoeken, spawnen bij de speler, oude weghalen | Lijst van vanilla: `data/vehicles.json` in de kennisbasis (930, build 3889). Spawnen: dolu_tool (dev-menu) | client + server | Hoe vinden we add-on modellen (lijst uit de manifests, Q-A2)? |
| F-A2 | **Handling live aanpassen**, per sectie, met zoeken, vriendelijke namen en uitleg per veld | `old/oldversion` (juli 2025): lezen werkte, Apply kwam nooit aan; het schema per veld en het zoeken zijn bruikbaar (zie [handling.md](handling.md)) | client | Q-H1, Q-H3, Q-H6, Q-H7, Q-H13, Q-H15 |
| F-A3 | **Grenzen**: "normaal" per klasse, harde grenzen per veld, en een schakelaar om de grenzen uit te zetten. Ook in de ontgrendelde modus nooit 0 bij de vier velden die door nul delen | Startbereiken per klasse (`handling_template_principles.md`), Eddlm-ranges (`plan.md` §9), JSON-templates; de oude editor had alleen een HTML-hint, deels met foute grenzen | client + server (wie mag ontgrendelen) | Q-H4, Q-H5, B18 |
| F-A4 | **Reset**: per veld, per sectie, alles terug naar de waarde bij het openen | Idee in `plan.md` §9. Omdat elk voertuig een eigen kopie heeft, volstaat het de waarden bij het openen te bewaren | client | – |
| F-A5 | **Meten en vergelijken**: topsnelheid, 0–100, remweg; verschil met de originele waarden of met een ander voertuig | Idee in `plan.md` §9 ("metrics panel", "vergelijking") | client | Q-H9 |
| F-A6 | **Exporteren**: een correcte `handling.meta` voor dit voertuig, met alles wat gelezen is (ook vlaggen als hex, `AIHandling`, `SubHandlingData`); kopiëren of op de server opslaan | `old/oldversion` (opslaan werkte, maar vlaggen en sub-handling kwamen uit een template); `plan.md` (klembord) | client + server | Q-H8, Q-H13, B15 |
| F-A7 | **Importeren**: een `handling.meta` plakken en op het voertuig zetten | Idee in `plan.md` §9 | client | – |
| F-A8 | **Presets**: per klasse een startpunt laden (een "suggestieblok" met aanbevolen startwaarden); eigen presets opslaan | JSON-templates in `VehicleTool/templates/handling/` | client + server | – |
| F-A9 | **Sync**: wie ziet de aangepaste handling (alleen de bestuurder, iedereen)? | – (idee: de server zet de waarden in een state bag op het voertuig, elke client past ze toe) | server + client | Q-H2, Q-H12 |
| F-A10 | **Uiterlijk testen**: mods uit de kit, liveries, extras, kleuren, wielen; meteen zien of `carcols`/`carvariations` kloppen | – | client | – |
| F-A11 | **Diagnose van het voertuig**: model, klasse, type, `handlingName`, `txdName`, welke textures laden | – | client | Q-T2 |
| F-A12 | **Geluid uitproberen** (`audioNameHash` wisselen) | – | client | Q-H10 |
| F-A13 | **Rechten en logging**: alleen met ACE-recht (via een bridge-haak), elke wijziging gelogd | Plan §9 (ACE-check) | server | B14 |

**Al klaar in de kennisbasis** (`examples/`, getest, zonder ox_lib): `streaming.lua` (model laden met een deadline, voor F-A1), `callback.lua` (client vraagt, server antwoordt), `nui_focus.lua` (meer schermen, één met focus), `keybind.lua` (toets om de editor te openen), `notify.lua`, `log.lua`, `sanitize.lua` en `json_safe.lua` (invoer en presets), `rate_limiter.lua` en `patterns/server_event_guards.lua` (server-checks), `patterns/netid_entity.lua` (voertuig over het netwerk), `patterns/resource_cleanup.lua` (gespawnde voertuigen opruimen).

## B. Scannen

| # | Functie | Bestaat al | Waar | Open vragen |
|---|---------|------------|------|-------------|
| F-B1 | Een map of de hele server doorzoeken naar voertuig-resources en packs | `VehicleTool`, FivemVehicleTool-repo (scanner), VehicleOptimizer | server of extern | Q-A1 |
| F-B2 | Soort resource herkennen: los voertuig, pack, wielen-pack, geluidspakket, escrow, niet omgezet (`.rpf`) | deels (`VehicleTool`) | server of extern | – |
| F-B3 | Alle `data_file`-regels van elke resource lezen | `VehicleTool` (manifest-parser; leest `server_scripts {}` en `shared_scripts {}` niet) | server (`GetResourceMetadata`?) of extern | Q-A2 |

## C. Controleren

Alle controles staan in [validation_rules.md](validation_rules.md) (R, F, M, X, A, T).

| # | Functie | Bestaat al | Waar | Open vragen |
|---|---------|------------|------|-------------|
| F-C1 | Manifest-controles (R) | `VehicleTool` (deels; R7 met veel vals alarm) | server of extern | Q-S7, Q-M10 |
| F-C2 | Structuur-controles (F) | `VehicleTool` | server of extern | B1 |
| F-C3 | Meta-controles en koppelingen (M) | `VehicleTool` (deels; alleen het eerste voertuig per bestand; koppelingen alleen in de split) | server of extern | Q-S8, Q-M4, Q-M6 |
| F-C4 | **Botsingen over de hele server** (X): stream-namen, `modelName`, `handlingName`, kit-id's | `VehicleTool` (alleen binnen de eigen pack) | server of extern | Q-S6 |
| F-C5 | Audio-controles (A) | `VehicleTool` | server of extern | Q-M11, Q-M13 |
| F-C6 | Rapport: per controle PASS/WARN/FAIL, tekst en JSON, en in de NUI | `VehicleTool` (`reporting.py`) | server + NUI of extern | – |

## D. Ordenen en normaliseren

| # | Functie | Bestaat al | Waar | Open vragen |
|---|---------|------------|------|-------------|
| F-D1 | Een resource omzetten naar de gekozen mapstructuur (één resource per voertuig, B1) | FivemVehicleTool-repo (per categorie; klasse-tabel fout, hernoemt bij botsingen), `VehicleTool` (pack; manifest ongeldig) | server (met schrijfrecht) of extern | B24 |
| F-D2 | Een pack splitsen naar één resource per voertuig (B2, gekozen) | `VehicleTool/split_multi_vehicle.py` (verliest `Lights`/`Sirens` en commentaar; verplaatst geen stream, audio of manifest) | server of extern | B23, B24 |
| F-D3 | Losse voertuigen samenvoegen tot één pack | `VehicleTool` (pack-sync), FivemVehicleTool-repo | server of extern | K20 in [duplicates_and_conflicts.md](duplicates_and_conflicts.md) |
| F-D4 | **Meta normaliseren**: elk bestand in dezelfde vorm en volgorde schrijven, met comment-secties | `VehicleTool/templates/meta/vehicles.template.meta` (secties). In de UI van VehicleTool waren de identiteitsvelden (`modelName`, `txdName`, `handlingId`) alleen-lezen en de rest bewerkbaar; een goede keuze om te houden | server of extern | Q-M12 |
| F-D5 | **Ontbrekende velden of bestanden aanvullen uit een template** per type en klasse | `VehicleTool` (templates, deels fout) | server of extern | Q-M12, Q-M14, Q-S8 |
| F-D6 | Manifest maken of herschrijven | `VehicleTool`, repo, converter | server of extern | Q-M10, Q-S7 |
| F-D7 | Register bijhouden: welk bestand en welk kit-id hoort bij welk voertuig; vrij kit-id voorstellen; id's met de hand reserveren | `VehicleTool` (`registry/vehicles_index.json`, `modkit_ids.json` met `"source": "manual"`) | server of extern | Q-M4 |
| F-D8 | Dry-run en back-up vóór elke wijziging; de bron nooit verplaatsen | FivemVehicleTool-repo (dry-run, zip-back-up); B8 | – | – |

## E. Intake

| # | Functie | Bestaat al | Waar | Open vragen |
|---|---------|------------|------|-------------|
| F-E1 | GTA-mod (`dlc.rpf`) uitpakken naar een FiveM-resource | `trp_rpf_to_fivem_converter` (met rpf-cli; werkt half: audio valt weg, hernoemt dubbele namen, geen manifest) | extern | Q-A3 |
| F-E2 | Oud manifest (`__resource.lua`) omzetten | idee in `plan.md` | server of extern | Q-S9 |
| F-E3 | Een voertuig toevoegen aan de pack: controleren, kopiëren, register bijwerken | `VehicleTool` (UI) | server of extern | – |

**Hoe een GTA-mod eruitziet** (uit `docs/plan.md` §3): `mods/update/x64/dlcpacks/<naam>/dlc.rpf`, met daarin `x64/models/cdimages/` (de `.yft` en `.ytd`, die naar `stream/` gaan) en `data/` (de meta's). De converter pakt het archief uit, sorteert, en maakt het manifest.

**Volgorde voor een nieuw voertuig** (uit `META_SPLIT_POLICY.md`): 1. de stream-bestanden vastleggen (model, textures, mod-onderdelen, liveries); 2. `vehicles.meta` (één model); 3. `handling.meta` voor die `handlingId`; 4. `carvariations.meta` voor dat model; 5. `carcols.meta` met de kits die stap 4 noemt; 6. controleren (elke `visibleMods/modelName` heeft een bestand). Eerst de stream, omdat de game modellen op bestandsnaam laadt en de meta daarop moet aansluiten.

De stroom uit het canvas (`VehicleTool/docs/Naamloos.canvas`):

```text
map scannen
  ├─ .rpf ─────────────► omzetten naar FiveM
  ├─ __resource.lua ───► omzetten naar fxmanifest.lua ─┐
  ├─ geen resource ────► stoppen met een fout          │
  └─ fxmanifest.lua ───────────────────────────────────┴─► bestanden kopiëren
        ├─ alle textures verzamelen
        ├─ alle audio verzamelen
        └─ aantal voertuigen in vehicles.meta
              ├─ meer dan één ─► splitsen: per voertuig eigen meta's
              └─ één ─► type bepalen ─► zijn alle meta's er (minimaal vehicles, handling, carcols, carvariations)?
                        ├─ nee ─► ontbrekende meta maken uit onze template
                        └─ ja ──► klopt alle informatie?
                                  ├─ ja ──► meta omzetten naar onze vaste vorm
                                  └─ nee ─► standaardwaarde uit de template gebruiken
```

## F. Textures

| # | Functie | Bestaat al | Waar | Open vragen |
|---|---------|------------|------|-------------|
| F-F1 | Geheugen per bestand uit de header (phys/virt) en waarschuwen boven de grens | script getest op 20 okt ([textures.md](textures.md)) | server of extern | Q-T1 |
| F-F2 | Per texture: naam, resolutie, formaat, mips | `trp_dds_inspector` (op met OpenIV geëxporteerde `.dds`; alleen kijken) | extern (of server met eigen parser) | Q-T4, Q-A5 |
| F-F3 | Advies per bestand: welke textures het grootst zijn en wat kleiner kan | – | server of extern | – |
| F-F4 | **Verkleinen**: mip-levels weglaten, of opnieuw comprimeren, en de `.ytd` terugschrijven | – (`noneWorking/` kwam niet verder dan uitpakken; `trp_dds_inspector` verkleint wel, maar ongecomprimeerd) | extern | Q-T4, B19 |
| F-F5 | Splitsen over twee `.ytd`'s met `txdRelationships` | – | server of extern | Q-T8 |
| F-F6 | Dubbele textures onder andere namen vinden | md5-vergelijking (20 okt) | server of extern | – |
| F-F7 | Escrow herkennen en overslaan | header-check (20 okt) | server of extern | Q-T7 |

## G. Kennis en data die de tool nodig heeft

| # | Wat | Bestaat al | Open vragen |
|---|-----|------------|-------------|
| F-G1 | Vanilla-voertuigen met klasse en type | `data/vehicles.json` (kennisbasis) | – |
| F-G2 | Vanilla-handling per voertuig → bereiken per klasse | – | Q-H4 |
| F-G3 | Vanilla kit-id's en kitnamen | lijst van Mentozz (2021, `community`) | Q-M4 |
| F-G4 | Vanilla-layouts, audio-namen, `txd`-namen (voor M11, M12, X5) | – | Q-M13 |
| F-G5 | Correcte meta-templates per type, uit vanilla-bestanden | deels, met fouten | Q-M12 |
| F-G6 | Officiële lijst van `data_file`-types | – | Q-M10 |

---

## Wat het oude plan nog meer wilde (backlog)

Uit `VehicleTool/docs/ROADMAP.md` en `docs/plan.md` §11:

- Na pack-sync ook de bron-`vehicles.meta` bijwerken (alleen met een duidelijke knop).
- Na het wisselen van profiel automatisch opnieuw controleren.
- Bron-`carcols` en -`carvariations` overnemen of samenvoegen in plaats van alleen de template (zie K20 in [duplicates_and_conflicts.md](duplicates_and_conflicts.md)).
- Hetzelfde handling-profiel in de CLI als in de UI.
- Tests met vaste voorbeeldmappen (pytest) en een controle in CI.
- `dlctext`/`shop_vehicle` niet meer als harde FAIL (B13).
- Fasering van maart: 0 analyse (klaar), 1 YTD-test met rpf-cli (klaar: past niet), 1b CodeWalker.API (stond op "actief", nooit afgemaakt), 1c handmatig met OpenIV (tijdelijke werkwijze), 2 controles 1–3, 3 texture-rapport en uitzoeken of een `.ytd` te schrijven is, 3b verkleinen, 4 handling-editor, 4b presets/meten/vergelijken, 5 afwerking en publiek.
