# Testpakket: voorstel om te bespreken

Mark vroeg (21 okt 2026): "zou het een oplossing zijn om eerst een soort van test vehicle pakket te maken met de verschillende problemen?" Dit is het voorstel. **Nog niets gebouwd of gekopieerd**; Mark beslist (B25 in [decisions.md](decisions.md)).

De voertuigen hieronder komen uit de scan van de downloads in `[Vehicles]` ([test_data.md](test_data.md#downloads-in-vehicles-21-okt-2026)). Groottes zijn op schijf, met de map van het voertuig in `data/` en `stream/`.

---

## Advies: ja, met een paar regels

**Waarom:**

1. **De downloads zelf zijn te groot en te verweven om mee te testen.** Ruim 10 GB, 362 voertuigen, 1.352 bestanden boven de oversized-grens, en packs die elkaar overlappen: de Lore-pack en `lds-lorevehicles` delen 20 voertuigen, 1.474 bestandsnamen en 29 kit-id's. Laad je alles tegelijk, dan zie je niet welk probleem welk effect heeft.
2. **Bijna elke open vraag is "slikt de game dit?"** (Q-M16, Q-S13, Q-M15, Q-M17, Q-S6, …). Dat zie je alleen goed met één probleem tegelijk.
3. **Dezelfde set test later de tool.** Elk geval krijgt een verwacht resultaat: welke controle moet afgaan ([validation_rules.md](validation_rules.md)). Als de tool verandert, moet hij op deze set nog steeds hetzelfde vinden.
4. **Klein en los te starten.** Elk geval is een eigen resource; via dolu start en stop je er één tegelijk.

**Regels:**

- **Eén probleem per geval**, zo goed als het kan. Gevallen uit het wild hebben vaak meer dan één probleem; de bijvangst staat er dan bij.
- **Nooit repareren.** De bestanden blijven zoals ze gedownload zijn; daar gaat het om.
- **Eén geval tegelijk** draaien, behalve de botsingsgevallen: die bestaan juist uit twee resources.
- **De voertuigen niet in git.** Ze zijn van andere makers, en samen honderden MB's. In de repo komen alleen de beschrijvingen, de verwachte uitkomsten en een lijst waar elk bestand vandaan komt, zodat het pakket opnieuw te maken is.

## Twee soorten gevallen

| Soort | Wat | Goed voor |
|-------|-----|-----------|
| **Uit het wild** (dit voorstel, eerste ronde) | Een voertuig uit de downloads, onveranderd, met het probleem dat het heeft | Laten zien dat de tool met echte rommel overweg kan; wat doet de game met echte fouten |
| **Gemaakt** (later) | Het schone basisvoertuig (`vt_00`), met precies één ding veranderd | Systematische tests: de minimale set (Q-S8), ontbrekende velden (Q-M14), hoofdletters in globs (R16), `stream/` buiten de root (F10), meta niet in `files {}` (R15), kit-id boven 65535 (Q-M4), dezelfde stream-naam in twee submappen (X7) |

## Opbouw

```text
resources/
  [vehicletests]/                 -- niet in server.cfg; elk geval los starten
    vt_00_baseline/               -- één geval = één resource
      fxmanifest.lua              -- het manifest zoals het geval het nodig heeft
      data/ …
      stream/ …
      CASE.md                     -- zie hieronder
    vt_02_xml_comment/
    …
```

`CASE.md` per geval:

- **Probleem:** wat er mis is, met het pad in de bron.
- **Bron:** pack, map, maker, en de downloaddatum.
- **Verwacht van de tool:** welke controle afgaat (bijv. M1) en met welke ernst.
- **Vraag:** welke open vraag het beantwoordt (bijv. Q-M16).
- **In-game kijken:** wat we controleren (console en F8 bij het starten, spawnen, naam, kleuren, mods, geluid).
- **Uitkomst:** na de test, met datum en het label `tested`.

## De gevallen (eerste ronde, uit het wild)

Samen 31 gevallen (35 resources: de paren en de geluids-resource van `vt_01` tellen dubbel), ongeveer 430 MB. Volgorde zoals Mark de onderdelen wil (B12).

### 1. Structuur, templates en meta's

| Geval | Voertuig (bron) | MB | Probleem | Vraag / controle |
|-------|-----------------|---:|----------|------------------|
| `vt_00_baseline` | `tltypes` (PLOKS) | 7,8 | geen: de scan vindt niets, naam via `AddTextEntry`, niets boven 16 MiB | referentie en basis voor de gemaakte gevallen |
| `vt_01_nested_resource` | `zionks` (lds), met zijn geluids-resource eerst ín, dan naast de resource | 10 | een resource in een resource laadt niet; dan ontbreekt het eigen geluid | R13 |
| `vt_02_xml_comment` | `bolide` (PLOKS) | 13,4 | `<!------…---->` in `vehicles.meta` | Q-M16, M1 |
| `vt_03_xml_wrong_close` | `84rx7k` (PLOKS) | 18,5 | `carcols.meta` sluit `<Kits>` af met `</Lights>` | Q-M16, M1 |
| `vt_04_xml_nul_bytes` | `imperial` (lds) | 16,3 | NUL-bytes aan het eind van `carvariations.meta` | Q-M16, M1 |
| `vt_05_xml_space_before_decl` | `gstghell1` (lds) | 6,0 | twee spaties vóór `<?xml` in `carcols.meta` (bijvangst: eigen geluid zit in een geneste resource) | Q-M16, M1 |
| `vt_06_model_without_yft` | `accolade` (lds) | 4,8 | `vehicles.meta` noemt ook `accolade2`, maar daar is geen `.yft` voor | M4 |
| `vt_07_no_carvariations` | `sandero` (PLOKS) | 8,6 | geen `carvariations.meta` (bijvangst: handling van de vanilla `BALLER`) | Q-M9 |
| `vt_08_invalid_class` | `stingray` (PLOKS) | 31,1 | `vehicleClass` `VC_SPORTS` bestaat niet; `gameName` met een spatie (`corvette c8`) | Q-M17, M27 |
| `vt_09_no_label` | `blistacr` (lds) | 2,3 | geen tekst voor `gameName` | Q-M18, M16 |
| `vt_10_unknown_audio` | `hellenstorm` (lds) | 10,5 | `audioNameHash` die nergens bestaat | M12 |
| `vt_11_vanilla_handling` | `surano3` (lds) | 5,3 | `handlingId` `SURANO` (vanilla): mag, verwacht geen fout | M28 |
| `vt_12_kit_not_defined` | `yosemiteswb` (lds) | 2,8 | `carvariations` noemt `0_suv_modkit`, die nergens staat | M8 |
| `vt_13_livery_mods` | `atlas` (lds) | 6,2 | geen probleem: 16 liveries als mod-onderdeel (livery soort 2) | M22, [folder_structure.md](folder_structure.md) §2 |

### 2. Manifest

| Geval | Voertuig (bron) | MB | Probleem | Vraag / controle |
|-------|-----------------|---:|----------|------------------|
| `vt_20_unknown_types` | `kriegerty2` | 7 | `DLCTEXT_FILE` en `VEHICLE_SHOP_FILE` staan niet in de officiële lijst | Q-M15, R14 |
| `vt_21_all_types_glob` | `buffaloh` (Lore), met het manifest van de Lore-pack | 5,6 | elke meta onder tien types, ook twee onofficiële | Q-S13, R6 |
| `vt_22_old_manifest` | `zaccflatlit` | 18,3 | `__resource.lua`, en twee meta's uit het manifest ontbreken | Q-S9, R2, R4 |

### 3. Botsingen (paren: twee resources tegelijk)

| Geval | Voertuigen (bron) | MB | Probleem | Vraag / controle |
|-------|-------------------|---:|----------|------------------|
| `vt_30_kit_id_pair` | `rcf` (PLOKS) + `dubstag` (lds) | 24,1 | allebei kit-id 689 | Q-S6, X4 |
| `vt_31_stream_name_pair` | `f430s` + `gs350` (PLOKS) | 32,4 | allebei `spoiler_2.yft` en `spoiler_3.yft`, met andere inhoud | Q-S6, X1, X7 |
| `vt_32_same_vehicle_twice` | `vorstand` uit lds én uit Lore | 22,2 | zelfde model, stream-namen en kit-id 701 | X1, X2, X4 |
| `vt_33_vanilla_vehicle` | `futo2` (Lore) | 6,6 | vervangt de vanilla Futo GTX (bijvangst: `fInitialDriveForce` 4,79) | X5, Q-T6 |
| `vt_34_vanilla_kit` | `wildtrak` (PLOKS) | 26,2 | definieert de vanilla-kits `268_hermes_modkit` en `269_revolter_modkit` opnieuw | Q-M19, M21 |

### 4. Textures

| Geval | Voertuig (bron) | MB | Probleem | Vraag / controle |
|-------|-----------------|---:|----------|------------------|
| `vt_40_over_16` | `cutlass` (PLOKS) | 7,7 | 26 MiB: blauwe melding | Q-T1, T1 |
| `vt_41_over_32` | `rhinetaxi` (lds) | 6,8 | 40 MiB: gele melding | Q-T1, T1 |
| `vt_42_over_48` | `nissantitan17` (PLOKS) | 20,8 | 52 MiB: gele melding met "WILL lead to streaming issues" | Q-T1, Q-T2, T1 |
| `vt_43_over_64_ytd` | `i8` (PLOKS) | 16,8 | `i8.ytd`: 128 MiB uit 1,5 MB op schijf | Q-T1, Q-T2, Q-T4 |
| `vt_44_yft_with_textures` | `ingotc` (lds) | 5,4 | `ingotc_interiormod.yft`: 128 MiB phys, textures in het model | Q-T1, T1 |
| `vt_45_escrow` | `strman` | 26 | escrow; 76 MiB; `carcols.meta` uit het manifest ontbreekt | Q-T7, R9, T2 |
| `vt_46_rpf_in_stream` | `rculi` (PLOKS) | 37,9 | `rculi_mods.rpf` in `stream/` | Q-S14, F9 |

### 5. Handling (voor de grenzen in de editor)

| Geval | Voertuig (bron) | MB | Probleem | Vraag / controle |
|-------|-----------------|---:|----------|------------------|
| `vt_50_ten_gears` | `720s` (PLOKS) | 13,1 | `nInitialDriveGears` 10 | Q-H14 |
| `vt_51_extreme_force` | `ruiner6str` (Lore) | 7,5 | `fInitialDriveForce` 4,79 (90% van de downloads zit tussen 0,20 en 0,525) | Q-H4, Q-H5, M19 |

### Wat er nog niet in zit

- Livery soort 1 (in de `.ytd`) en soort 3 (livery2): geen voorbeeld in de downloads. Soort 4 (apart model per uiterlijk): `lsfd` in `archive/research/`.
- Een boot, een vliegtuig en een heli als echte resource ([test_data.md](test_data.md), "Wat ontbreekt").
- `cle53amg` (alleen `dlc.rpf`, 307 MB): hoort bij de intake (Q-A3), niet bij dit pakket.

## Te bespreken met Mark

1. **Maken we het pakket?** (B25) Zo ja: eerst de gevallen van prioriteit 1 en 2 (17 gevallen, ±175 MB), de rest daarna.
2. **Ook gemaakte gevallen** vanaf `vt_00`, voor de systematische tests?
3. **Plek en namen:** `resources/[vehicletests]/vt_<nn>_<onderwerp>`, niet in `server.cfg`, starten via dolu. Of liever een andere plek of prefix?
4. **De downloads:** nu start `ensure [Vehicles]` bij elke serverstart `lds-lorevehicles` (98 voertuigen, 1,7 GB, 469 oversized-meldingen), `kriegerty2`, `strman` en `zaccflatlit`. Voorstel: de ruwe downloads buiten `resources/` bewaren (bijvoorbeeld `F:\fivem_dev\vehicle_sources\`) en alleen kopieën in het testpakket zetten. Dat scheelt ook de opstarttijd: de server berekent bij elke nieuwe of gewijzigde stream-file een hash.
5. **Niet in git:** akkoord dat alleen de beschrijvingen en de bronlijst in de repo komen?
