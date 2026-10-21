# Vehicle tool: documentatie

Alles wat we weten over het plan voor een all-in-one voertuigtool voor FiveM: een in-game editor (spawnen, handling aanpassen), een check op te grote textures, controle en templates voor meta-bestanden, en een vaste mapstructuur.

**Fase: onderzoek.** We bouwen nog niets. Deze map verzamelt wat er al in de projectmap stond (oude notities, code, testdata), haalt dubbelingen weg, en zet de open vragen op een rij. Het oude werk zelf staat sinds 21 okt in `archive/` van de projectmap.

Bijgewerkt: 21 okt 2026.

---

## In het kort (21 okt 2026)

- **Keuzes van Mark:** één resource per voertuig, met de liveries erbij; packs splitsen; één tool als het kan; volgorde structuur en templates → manifest → textures → handling-editor; het project gaat in de repo `FivemVehicleTool`; het in-game deel heet `dev_<naam>`. De naam zelf kiest Mark uit de lijst bij B17 ([decisions.md](decisions.md)).
- **Mapstructuur:** een voorstel voor de indeling van één voertuig-resource staat in [folder_structure.md](folder_structure.md) §3 (B24). Uit de FiveM-broncode: de server kijkt alleen in mappen met haken, een resource in een andere resource laadt nooit, en `stream/` moet in de root van de resource staan maar mag submappen hebben.
- **Textures:** FiveM meet per bestand, phys en virt apart, en meldt boven 16, 32 en 64 MiB; boven 48 MiB met de waarschuwing over streamingproblemen (broncode). De grootte op schijf zegt niets: `i8.ytd` is 1,5 MB op schijf en 128 MiB in het geheugen ([textures.md](textures.md)).
- **Downloads in `[Vehicles]`:** 364 voertuigen, ruim 10 GB. Twee van de drie packs laden niet zoals ze er nu staan, 1.352 bestanden zitten boven de 16 MiB, en de packs botsen op namen en kit-id's ([test_data.md](test_data.md#downloads-in-vehicles-21-okt-2026)).
- **Testpakket:** een voorstel om te bespreken: 31 kleine gevallen met elk één probleem ([test_pack.md](test_pack.md)).
- **Meta's:** de officiële lijst van `data_file`-types is nagekeken; vijf types uit de downloads staan er niet in. De oude notities en templates bevatten fouten (o.a. `vehicleClass` als getal, `dlctext.meta` met namen, verzonnen root-elementen, overal kit-id 10000) ([meta_files.md](meta_files.md), [duplicates_and_conflicts.md](duplicates_and_conflicts.md)).
- **Handling:** volgens de FiveM-broncode krijgt elk voertuig een eigen kopie van zijn handling, alleen op de client, in de eenheden van `handling.meta`. Sync naar andere spelers moet de tool zelf regelen ([handling.md](handling.md)).

## Waar staat wat

| Document | Inhoud |
|----------|--------|
| [inventory.md](inventory.md) | Wat er in de projectmap en de GitHub-repo staat: per map wat het is, de staat, en wat ermee moet |
| [duplicates_and_conflicts.md](duplicates_and_conflicts.md) | Wat dubbel stond, en waar de oude notities elkaar of de werkelijkheid tegenspreken |
| [tool_functions.md](tool_functions.md) | **Welke functies de tool nodig heeft**, per onderdeel: wat er al is en wat nog niet |
| [folder_structure.md](folder_structure.md) | Mapstructuur van voertuig-resources en packs, liveries, de open keuze |
| [meta_files.md](meta_files.md) | Elk meta-bestand, hoe ze aan elkaar hangen, `data_file`-types, minimale set, templates |
| [validation_rules.md](validation_rules.md) | Alle controles die de tool moet doen (manifest, structuur, meta, namen, botsingen, veiligheid) |
| [handling.md](handling.md) | Handling-velden, grenzen, "normale" waarden, de in-game editor |
| [textures.md](textures.md) | Te grote textures ("oversized assets"), bestandsformaten, wat we al probeerden |
| [audio.md](audio.md) | Eigen motorgeluid in een voertuig-resource |
| [test_data.md](test_data.md) | De testvoertuigen en packs (ook de downloads in `[Vehicles]`), en welke test bij welk voorbeeld hoort |
| [test_pack.md](test_pack.md) | **Voorstel testpakket** (om te bespreken): kleine gevallen met elk één probleem |
| [open_questions.md](open_questions.md) | **Het onderzoek dat nog moet**: per vraag hoe we het uitzoeken (bron of test op de dev-server) |
| [decisions.md](decisions.md) | Marks keuzes, wat vastligt door de standaard, wat Mark nog moet kiezen, en de namenlijst |
| [sources.md](sources.md) | Alle links, één keer, per onderwerp |

## Labels

Net als in de kennisbasis (`mjvanhaastert/Fivem`), plus twee voor dit onderzoek:

| Label | Betekenis |
|-------|-----------|
| `official` | Uit officiële FiveM/Cfx-documentatie of de broncode |
| `tested` | Zelf gecontroleerd, met datum. "Gelezen" betekent: zo staat het echt in de bestanden; nog niet in-game getest |
| `community` | Uit community-bronnen (GTAMods, Dawnstar, forum, andermans tool), niet zelf nagekeken |
| `aanname` | Uit onze oude notities (deels een gesprek met een AI) of afgeleid; behandelen als hypothese |
| `fout` | Bleek niet te kloppen; blijft staan zodat we de fout niet opnieuw maken |

## Hoe we verder werken

1. **Open vraag** → staat in [open_questions.md](open_questions.md), met de aanpak.
2. **Uitgezocht** → het antwoord in het juiste document hier, met label en datum; de vraag op "klaar".
3. **Algemene FiveM-kennis** (niet alleen voor deze tool) → naar `info/` van de kennisbasis; lijsten (bijv. vanilla-handling per klasse) naar `data/`; herbruikbare code naar `examples/`.
4. **Beslissing nodig** → [decisions.md](decisions.md); Mark kiest.

De standaard (`FIVEM_CODING_STANDARDS.md` en `prompt.md` in de kennisbasis) geldt voor alles wat in FiveM draait. Wat dat voor deze tool betekent, staat in [decisions.md](decisions.md) (V1–V8).

---

## Waar de oude documenten gebleven zijn

Niets is weggegooid: de oude bestanden staan sinds 21 okt 2026 in `archive/` van de projectmap (zie `archive/README.md` en [inventory.md](inventory.md)). Wat erin stond, staat nu hier. In de tabel staan de oude paden; zet er `archive/` voor.

| Oud bestand | Nu in |
|-------------|-------|
| `docs/plan.md` (plan van aanpak v0.3, maart 2026, met het gesprek ervoor) | [tool_functions.md](tool_functions.md) (architectuur, onderdelen, fasering), [validation_rules.md](validation_rules.md) (de vier stappen), [folder_structure.md](folder_structure.md) (§5), [meta_files.md](meta_files.md) (§3–§6), [textures.md](textures.md) (§8, §8b), [handling.md](handling.md) (§9), [sources.md](sources.md) (§10), [decisions.md](decisions.md) |
| `docs/meta_reference_and_load_order.md` | [meta_files.md](meta_files.md) (§1–§3, §5), [folder_structure.md](folder_structure.md) (§4, §9, §12), [textures.md](textures.md) (§4.5), [audio.md](audio.md) (§10), [validation_rules.md](validation_rules.md) (§7, §11) |
| `docs/handling_template_principles.md` | [handling.md](handling.md) |
| `docs/vehicle_intake_procedure.md` | [validation_rules.md](validation_rules.md), [folder_structure.md](folder_structure.md) (§2, §5, §8), [audio.md](audio.md) (§4), [textures.md](textures.md) (§9) |
| `VehicleTool/docs/CARCOLS_CARVARIATIONS_REFERENCE.md` | [meta_files.md](meta_files.md) (§2, §6–§8) |
| `VehicleTool/docs/META_SPLIT_POLICY.md` | [folder_structure.md](folder_structure.md) (§3), [validation_rules.md](validation_rules.md), [decisions.md](decisions.md) (B2) |
| `VehicleTool/docs/PACK_VALIDATION.md` | [validation_rules.md](validation_rules.md), [test_data.md](test_data.md) |
| `VehicleTool/docs/vehicles_meta_fields.md` | [meta_files.md](meta_files.md) (§3) |
| `VehicleTool/docs/ROADMAP.md` | [tool_functions.md](tool_functions.md) |
| `VehicleTool/docs/Naamloos.canvas` (stroomschema) | [tool_functions.md](tool_functions.md), [meta_files.md](meta_files.md) (§5) |
| `VehicleTool/docs/TEST_PLAN.md`, `VehicleTool/README.md`, `VehicleTool/AUDIT.md` | blijven bij de code; samengevat in [inventory.md](inventory.md) en [validation_rules.md](validation_rules.md) |
| `VehicleTool/templates/README.md`, `templates/meta/README.md` | [meta_files.md](meta_files.md) (§9), [handling.md](handling.md) |
| `research/README.md`, `research/DriveV/README.md` | [test_data.md](test_data.md), [handling.md](handling.md) |
| `old/oldversion/README.md`, `VEHICLE_EDITOR_TESTS.md` | [handling.md](handling.md), [inventory.md](inventory.md) |
| `trp_dds_inspector/README.md`, `noneWorking/trp_codewalker_ytd_toolkit/README.md` | [textures.md](textures.md), [inventory.md](inventory.md) |
| `VehicleOptimizer/README.md`, `vehiclehandler/README.md`, README van de repo FivemVehicleTool | [inventory.md](inventory.md) |
