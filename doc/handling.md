# Handling: velden, grenzen en de in-game editor

Wat de handling-velden doen, welke grenzen we al hebben, hoe "normale" waarden te bepalen zijn, en wat de in-game editor daarvoor nodig heeft.
De labels staan uitgelegd in [README.md](README.md#labels).

Mark wil: een voertuig spawnen, de waarden aanpassen (sneller, grip, enz.), binnen grenzen van wat "normaal" is, met een schakelaar om die grenzen uit te zetten.

---

## Voorbeeld: lezen en schrijven met natives

```lua
-- Client. Lezen en schrijven van één veld van CHandlingData
local value = GetVehicleHandlingFloat(vehicle, 'CHandlingData', 'fInitialDriveForce')
SetVehicleHandlingFloat(vehicle, 'CHandlingData', 'fInitialDriveForce', value * 1.1)

-- Gehele getallen en vectoren hebben eigen natives
local gears = GetVehicleHandlingInt(vehicle, 'CHandlingData', 'nInitialDriveGears')
local com = GetVehicleHandlingVector(vehicle, 'CHandlingData', 'vecCentreOfMassOffset')

-- Klasse en type, voor de juiste grenzen en het juiste veldenpakket
local class = GetVehicleClass(vehicle)   -- 0-22
```

`official` (FiveM-natives, zie [sources.md](sources.md)).

## Wat de FiveM-broncode zegt over de handling-natives

Gelezen in de broncode van FiveM (`citizenfx/fivem`, vooral `handling-loader-five/src/HandlingLoader.cpp`) en de native-docs, op 20 okt 2026. Label: `official` (broncode), **niet in-game getest**. De tests staan in [open_questions.md](open_questions.md).

**Hoe ver een wijziging reikt**

- `SetVehicleHandlingFloat/Int/Vector/Field` werken op een **eigen kopie per voertuig**. Elk voertuig krijgt bij het aanmaken een volledige kopie van zijn handling, ook van `SubHandlingData`. Andere voertuigen met dezelfde handling merken niets. (Q-H1)
- `SetHandlingFloat/Int/Vector/Field(handlingName, …)` (zonder voertuig) wijzigt de **gedeelde** handling. Alleen voertuigen die **daarna** worden gespawnd krijgen het. Daarom spawnde de oude editor het voertuig opnieuw. Geen herstel bij het stoppen van de resource (`aanname`).
- Alle handling-natives bestaan **alleen op de client**. Handling wordt niet gesynchroniseerd en de server kan hem niet lezen of afdwingen. De netwerk-eigenaar rekent de physics van een voertuig uit; wisselt de eigenaar, dan geldt diens handling. Idee: de server zet de aanpassingen in een state bag op het voertuig, en elke client past ze toe in de handler (die draait opnieuw als het voertuig weer in beeld komt). Testen met twee clients. (Q-H2, Q-H12)
- Een wijziging per voertuig verdwijnt als het voertuig opnieuw wordt aangemaakt (respawn, of uit beeld en weer terug). `aanname` (Q-H12)

**Welke velden live werken**

- `fInitialDriveForce` en `fInitialDriveMaxFlatVel` werken per voertuig pas na **`ModifyVehicleTopSpeed`**; die zet de transmissie opnieuw op (native-docs). (Q-H3, Q-H9)
- Sommige vlaggen werken alleen globaal (via `SetHandling*` en een respawn), volgens de native-docs. Welke, is niet bekend. (Q-H7)
- `fMass`, `vecCentreOfMassOffset` en `vecInertiaMultiplier` werken waarschijnlijk pas na een respawn (de physics krijgen ze bij het aanmaken); grip, remmen, vering, sturen en schade waarschijnlijk meteen (FiveM rekent de afgeleide waarden opnieuw uit). `aanname` (Q-H3)

**Eenheden: de natives gebruiken de eenheden van `handling.meta`**

FiveM rekent zelf om naar de interne waarden. Lezen en daarna als `handling.meta` opslaan gaat dus grotendeels één op één (Q-H13). Wat er intern gebeurt:

| Veld | In `handling.meta` en de natives | Intern |
|------|----------------------------------|--------|
| `fSteeringLock`, `fTractionCurveLateral` (en bij motoren `fMaxBankAngle`, `fFullAnimAngle`, `fBikeOnStandLeanAngle`) | graden | radialen |
| `fInitialDragCoeff` | zoals in de meta (4–15 in onze testdata) | × 0,0001 |
| `fSuspensionCompDamp`, `fSuspensionReboundDamp` | zoals in de meta | × 0,1 |
| `fInitialDriveMaxFlatVel` | "km/h-achtig" getal (95–281,5 in onze testdata) | ÷ 3,6 (m/s); FiveM rekent daaruit ook de afgeleide `fDriveMaxFlatVel` uit (÷ 3,6 × 1,2) |
| `fBrakeBiasFront`, `fTractionBiasFront`, `fSuspensionBiasFront`, `fAntiRollBarBiasFront` | 0–1 | × 2 voor, (1 − waarde) × 2 achter |
| `fDriveBiasFront` | 0–1 | onder 0,1 wordt het puur achter, boven 0,9 puur voor; een 0,05 lees je terug als 0 |
| `fPercentSubmerged` | **procent** (75–200 in onze testdata) | drijfvermogen = 100 ÷ waarde |

Dat verklaart ook de tegenspraak over `fInitialDriveMaxFlatVel` (K9 in [duplicates_and_conflicts.md](duplicates_and_conflicts.md)): de class-baselines (150–340) staan in meta-eenheden; de "0–200 m/s" uit het plan is waarschijnlijk de interne waarde.

**Namen en klassen**

- **Veldnamen zijn hoofdlettergevoelig.** `fDownForceModifier` (zo stond het in de oude editor) vindt niets; het is `fDownforceModifier`.
- De naam van de handling (`handlingName`) is niet hoofdlettergevoelig bij het opzoeken. Per voertuig is hij alleen als **hash** te lezen (`GetVehicleHandlingInt(veh, 'CHandlingData', 'handlingName')`). (Q-M8)
- De docs zeggen "only CHandlingData is supported", maar de broncode zoekt ook in `SubHandlingData` naar de klasse die je noemt (`CCarHandlingData`, `CBikeHandlingData`, `CFlyingHandlingData`, `CBoatHandlingData`, …). Heeft het voertuig die klasse niet, dan staat er "No such field" in F8. (Q-H6)
- Een onbekend veld geeft in F8 `No such field X during GET_VEHICLE_HANDLING_FLOAT`; de setters geven niets terug, dus de editor ziet niet of het lukte.
- Vlaggen (`strModelFlags`, `strHandlingFlags`, `strDamageFlags`, en `strAdvancedFlags` in `CCarHandlingData`) zijn als getal te lezen en te schrijven; in de meta staan ze als hex-tekst. Bij export omzetten. (Q-H7)

**Harde grenzen uit de broncode** (Q-H5)

- **Deling door nul** in FiveM als je deze velden op 0 zet: `fPercentSubmerged`, `fTractionSpringDeltaMax`, `fSteeringLock`, `fTractionCurveLateral`. Dus nooit 0, ook niet in de ontgrendelde modus.
- `fTractionCurveMax` = 0 en `fTractionCurveMin` > `fTractionCurveMax` vangt FiveM zelf op.
- `nInitialDriveGears`: een van de schrijfroutes kapt af op 7, terwijl add-ons tot 10 gebruiken. `aanname`, testen (Q-H14).

---

## Velden en grenzen volgens Eddlm (uit `docs/plan.md` §9)

Mark wil "alles wat de website heeft" ([Eddlm Handling Tools](https://eddlm.github.io/Handling-Tools/handling)). Dit zijn de grenzen zoals ze in het plan staan: `community`, niet nagekeken tegen de site (Q-H5).

| Sectie | Veld | Min | Max | Eenheid / betekenis |
|--------|------|-----|-----|---------------------|
| Aero | `fDownforceModifier` | 0 | 300 | 1–100 dynamisch, < 1 statisch hoog, > 100 statisch laag |
| Aero | `fInitialDragCoeff` | 0 | 20 | luchtweerstand |
| Chassis | `fMass` | 100 | 15000 | kg |
| Motor | `fInitialDriveForce` | 0 | 0,5 | G-kracht |
| Motor | `fDriveInertia` | 0 | 3 | factor |
| Motor | `fInitialDriveMaxFlatVel` | 0 | 200 | m/s ("÷ 0,75 = km/h" volgens het plan, Q-H9) |
| Transmissie | `nInitialDriveGears` | 1 | 10 | aantal |
| Transmissie | `fClutchChangeRateScaleUpShift` | 0 | 10 | factor |
| Transmissie | `fClutchChangeRateScaleDownShift` | 0 | 10 | factor |
| Transmissie | `fDriveBiasFront` | 0 | 1 | 0 = achter, 0,5 = 4x4, 1 = voor |
| Remmen | `fBrakeForce` | 0 | 2 | G per wiel |
| Remmen | `fBrakeBiasFront` | 0 | 1 | verdeling |
| Remmen | `fHandBrakeForce` | 0 | 2 | G, alleen achteras |
| Grip | `fTractionCurveMax` | 0 | 3 | G, maximale grip |
| Grip | `fTractionCurveMin` | 0 | 3 | G, grip bij slippen |
| Grip | `fTractionCurveLateral` | 10 | 30 | graden |
| Grip | `fTractionBiasFront` | 0 | 1 | verdeling |
| Grip | `fTractionLossMult` | 0 | 2 | gripverlies offroad |
| Grip | `fLowSpeedTractionLossMult` | 0 | 2 | burnout-effect |
| Grip | `fSteeringLock` | 0 | 60 | graden |
| Vering | `fSuspensionForce` | 0 | 10 | veersterkte |
| Vering | `fSuspensionCompDamp` | 0 | 5 | demping indrukken |
| Vering | `fSuspensionReboundDamp` | 0 | 5 | demping uitveren |
| Vering | `fSuspensionUpperLimit` | 0 | 0,5 | m |
| Vering | `fSuspensionLowerLimit` | -0,5 | 0 | m |
| Vering | `fSuspensionRaise` | -0,3 | 0,3 | m, rijhoogte |
| Vering | `fSuspensionBiasFront` | 0 | 1 | verdeling |
| Stabilisator | `fAntiRollBarForce` | 0 | 3 | |
| Stabilisator | `fAntiRollBarBiasFront` | 0 | 1 | |
| Stabilisator | `fRollCentreHeightFront` | 0 | 1 | m |
| Stabilisator | `fRollCentreHeightRear` | 0 | 1 | m |

Velden die een echte `handling.meta` ook heeft, maar die hier niet staan: `fPercentSubmerged`, `vecCentreOfMassOffset`, `vecInertiaMultiplier`, `fTractionSpringDeltaMax`, `fCamberStiffnesss`, `fCollisionDamageMult`, `fWeaponDamageMult`, `fDeformationDamageMult`, `fEngineDamageMult`, `fPetrolTankVolume`, `fOilVolume`, `fSeatOffsetDistX/Y/Z`, `nMonetaryValue`, `strModelFlags`, `strHandlingFlags`, `strDamageFlags`, `strAdvancedFlags`, `AIHandling`, en alles onder `SubHandlingData` (`tested`, gelezen in `kriegerty2/common/handling.meta`).

---

## Startwaarden per klasse (uit `docs/handling_template_principles.md`)

Onze eigen "baseline ranges" van maart 2026: startbereiken, geen harde grenzen. `aanname` (niet gemeten, niet getest).

| Veld | Compact/Sedan | SUV/Utility/Van | Muscle/Sports Classic | Sports | Super | Off-road |
|------|---------------|-----------------|-----------------------|--------|-------|----------|
| `fMass` | 1200–1850 | 1700–3200 | 1450–2100 | 1250–1750 | 1200–1650 | 1500–3200 |
| `fInitialDriveForce` | 0,18–0,34 | 0,16–0,32 | 0,26–0,45 | 0,30–0,52 | 0,40–0,70 | 0,22–0,42 |
| `fInitialDriveMaxFlatVel` | 150–220 | 140–210 | 180–255 | 220–300 | 260–340 | 150–235 |
| `fBrakeForce` | 0,45–0,70 | 0,40–0,65 | 0,45–0,75 | 0,55–0,95 | 0,70–1,20 | 0,42–0,75 |
| `fSteeringLock` | 34–42 | 32–40 | | 36–44 | 36–45 | |
| `fTractionCurveMax` | 2,00–2,45 | 1,85–2,30 | 1,95–2,35 | 2,20–2,80 | 2,40–3,20 | 1,95–2,45 |
| `fTractionCurveMin` | 1,85–2,30 | 1,70–2,15 | | 2,00–2,65 | 2,20–3,00 | |
| `fSuspensionForce` | 1,50–2,20 | 1,60–2,40 | 1,45–2,20 | 1,70–2,60 | 1,90–3,00 | |
| `fSuspensionCompDamp` | 1,20–1,90 | | | | | |
| `fSuspensionReboundDamp` | 1,30–2,10 | | | | | |
| `fSuspensionRaise` | | 0,00–0,06 | | | | 0,02–0,10 |
| `fDriveBiasFront` | | | 0,00–0,25 | | | |
| `fTractionLossMult` | | | 1,10–1,90 | | | 0,90–1,50 |
| `fLowSpeedTractionLossMult` | | | | | | 0,0–0,8 |
| `fSuspensionUpperLimit` | | | | | | 0,10–0,18 |
| `fSuspensionLowerLimit` | | | | | | -0,18 – -0,10 |
| `fDownforceModifier` | | | | 0,5–2,0 (alleen als logisch) | 1,0–4,0 | |

**Let op:** `fInitialDriveMaxFlatVel` staat hier op 150–340, terwijl het plan (Eddlm) 0–200 als hele bereik gaf. Waarschijnlijk zijn het twee eenheden: deze bereiken staan in meta-eenheden, de 0–200 is de interne waarde in m/s (zie "Eenheden" hierboven, Q-H9).

Emergency: de onderliggende klasse plus betere remmen (+0,05 tot +0,20 op `fBrakeForce`), strakker sturen, gewicht passend bij de uitrusting.

### Dezelfde bereiken als JSON-profielen (`VehicleTool/templates/handling/`)

De tabel hierboven staat ook als 12 JSON-bestanden, met een paar verschillen:

- Compact en sedan zijn apart: compact `fMass` 1200–1650 en `fInitialDriveMaxFlatVel` 150–210; sedan 1300–1850 en 160–220.
- `bike_default` en `heli_default` hebben **vaste** waarden (min = max) van één voorbeeldvoertuig, plus de velden van `CBikeHandlingData` (20) en `CFlyingHandlingData` (43). Een "bereik-check" is daar dus een gelijk-check.
- De drie emergency-profielen (politie-sedan, ambulance-van, brandweer) geven alleen verschillen ten opzichte van een basisprofiel (bijv. remmen +0,05–0,20; brandweer `fMass` +500–2500, `fSteeringLock` 30–38). **Geen code leest die.** Kies je zo'n profiel, dan draait de check stil niet.
- `edge_case_manual_review` is alleen een lijst met redenen (`pack_mode_detected`, `type_class_mismatch`, `extreme_handling_values`, `special_platform_behavior`).
- In de rapporten van maart ging de bereik-check **nooit** af: hij draait alleen als je in de UI een profiel kiest.

VehicleTool maakt bij een nieuw pack-voertuig een `handling.meta` met vaste autowaarden (o.a. `fMass` 1600, `fInitialDriveForce` 0,28, `fInitialDriveMaxFlatVel` 180, 6 versnellingen, `strModelFlags 440010`, `strHandlingFlags 20000`, `AIHandling AVERAGE`) en neemt alleen voor zeven velden het midden van het profiel. `aanname` ("afgeleid van voorbeelden"); niet als bron gebruiken.

**Let op de spelling:** de game gebruikt `fCamberStiffnesss` (drie keer s) en `fTurublence…`. Een template moet die tikfouten overnemen (`community`).

Niet-auto's: motoren in kleine stappen tunen; boot, vliegtuig en heli hebben eigen velden en eigen templates (niet mengen met auto-bereiken); trailers hebben weinig handling, focus op stabiliteit.

### Principes (zelfde document, en DriveV)

1. Eerst het karakter van het voertuig: een zware sedan rijdt niet als een supercar; offroad werkt beter op slecht terrein.
2. Verschillen per klasse in sturen, overhellen, remmen en grip.
3. Template als start, daarna per model bijstellen.
4. Downforce alleen waar het logisch is (vooral super, soms sports).
5. Varianten (taxi, politie) mogen een andere handling hebben.
6. Schade serieuzer dan arcade (uit DriveV).
7. Rijhoogte en overhellen realistisch: niet onnodig laag; zachte voertuigen hellen meer over, sportwagens minder (uit DriveV).

**Karakter per klasse** (uit `docs/plan.md` §6, als richting voor de templates; `aanname`): compact kleine motor en zachte vering · sedan gebalanceerd, comfort · SUV zwaar, stijve vering, vierwielaandrijving · coupé sportief gebalanceerd · muscle veel vermogen, achterwielaandrijving, veel wielspin · sports classic als muscle, ouder gedrag · sports veel grip, hoge snelheid · super maximaal · off-road veel bodemvrijheid, stijve vering · industrial zwaar en traag · utility middelzwaar werkvoertuig · van zwaar, zachte vering · service taxi, bus · emergency politie, ambulance · military gepantserd · commercial vrachtwagens · open wheel F1-stijl, veel downforce · motoren, fietsen, boten, heli's, vliegtuigen en treinen hebben eigen physics.

### Werkwijze per voertuig (zelfde document)

1. Type en klasse bepalen. 2. Template kiezen. 3. Modelwaarden invullen. 4. Rijtest (optrekken, bochten, remmen, offroad). 5. Afwijkingen vastleggen als `EDGE_CASE`, met reden. Per voertuig loggen: model, type/klasse, bronwaarden, gekozen waarden, motivatie. Doel: een "golden baseline" per klasse.

Een voertuig is een `EDGE_CASE` als: het template-bereik duidelijk niet past (er is een extreme afwijking nodig); het voertuig instabiel rijdt ondanks "normale" waarden; een pack-model een gedeelde handling heeft terwijl de varianten duidelijk anders horen te zijn; of klasse/type niet past bij het gedrag. Dan in het rapport de reden en de gekozen afwijking noteren, en later meenemen in een betere template ("template-v2").

De tool kan per voertuig ook een **suggestieblok** tonen met aanbevolen startwaarden voor zijn klasse (`docs/handling_template_principles.md` §8).

---

## Hoe bepalen we "normaal"? (voorstel)

De bereiken hierboven zijn geschat. Beter: meten.

1. Op de dev-server alle vanilla-voertuigen (930 in build 3889, al in `data/vehicles.json` van de kennisbasis) één voor één spawnen en alle `CHandlingData`-velden uitlezen. Zo deden we het al voor `data/vehicles.json` (met de dump van devkit_api).
2. Per klasse min, max en percentielen (bijv. 5% en 95%) berekenen.
3. "Normaal" = tussen de percentielen van de klasse. "Hard" = de grenzen waarbij de physics nog werken (Q-H5). "Ontgrendeld" = alleen de harde grenzen.

Zo krijgt elk veld drie lagen: normaal (per klasse), hard (per veld), en de schakelaar. Dit is Q-H4 en beslissing B18.

Ter vergelijking: de 356 handlings in de downloads van 21 okt (add-ons, geen vanilla). 90% zit binnen: `fMass` 900–2.700, `fInitialDriveForce` 0,20–0,525, `fInitialDriveMaxFlatVel` 130–257, `nInitialDriveGears` 4–7, `fBrakeForce` 0,315–1,5, `fTractionCurveMax` 1,7–2,88. Uitschieters: `fInitialDriveForce` 4,79 (`ruiner6str`, `futo2`), `fBrakeForce` 14,7, 10 versnellingen (`720s`), 1 versnelling (`teslax`, elektrisch). Zie [test_data.md](test_data.md#downloads-in-vehicles-21-okt-2026). Zulke uitschieters moet de editor kunnen tonen, ook als ze buiten "normaal" vallen.

---

## De in-game editor die we al hadden (`old/oldversion`, juli 2025)

Marks eigen eerdere editor: resource `VehicleHandlingEditor` 1.0.0, auteur Man1C, voor de TrueRP-server (26 commits in `TrueRP/VehicleEditor`, 1–21 juli 2025). Geen dependencies. Plain HTML, JS en CSS als NUI.

**Hoe hij werkte**

1. Servercommando `/handlingeditor` (ACE `command.handlingeditor`); geen toets.
2. De client leest het voertuig waar je in zit, bepaalt het type (`GetVehicleTypeRaw`), leest alle velden van dat type met `GetVehicleHandlingFloat/Int/Vector(veh, 'CHandlingData', veld)` en opent de NUI.
3. De NUI toont één lijst: eerst de volgorde uit `config.lua` (`AttributeOrder`), dan alfabetisch. Per veld een vriendelijke naam, uitleg, min/max-tekst, en knoppen Apply en Copy. Zoeken op naam, label en uitleg.
4. **Save** stuurt alle waarden naar de server, die een `handling.meta` schrijft naar `generated/<type>_<naam>_<tijd>.meta`, ingevuld in een template per type.

**Wat er mis was** (uit de code; de testlijst `VEHICLE_EDITOR_TESTS.md` is nooit ingevuld)

- **Apply kwam nooit aan:** de NUI stuurt naar `vehicleHandling:applyHandling`, de client luistert op `applyHandling`. Copy had geen handler.
- Was Apply wel aangekomen, dan zette hij de handling **globaal** (`SetHandling*` op de displaynaam van het model, niet de echte `handlingName`) en spawnde hij het voertuig opnieuw. Daarbij gaan mods, kleuren, kenteken, schade en passagiers verloren.
- **Grenzen werden niet afgedwongen:** alleen als HTML-`min`/`max`. Een ongeldige invoer werd 0 (bijv. `fMass` = 0). Geen schakelaar voor "onrealistisch".
- De kernvelden (motor, remmen, grip, vering, schade) stonden alleen bij het type auto; motoren, boten, heli's en vliegtuigen zagen ze niet. Velden van een sub-klasse werden gelezen als `CHandlingData` (geeft onzin).
- **De export was niet trouw:** vlaggen, `AIHandling` en `SubHandlingData` kwamen uit het template, niet van het voertuig. Na zoeken gingen alleen de zichtbare velden mee.
- De templates gebruiken klassen die niet bestaan (`CHeliHandlingData`, `CPlaneHandlingData`; heli's en vliegtuigen gebruiken `CFlyingHandlingData`); de motor-template heeft `CCarHandlingData` met verzonnen velden en werd nooit gekozen (het type heet `bike`, de template `motorcycle`). Boot, heli en vliegtuig delen gekopieerde autowaarden. `AIHandling` met `BOAT`, `HELI`, `PLANE` of `SPORTS_BIKE` komt in echte bestanden niet voor (daar alleen `AVERAGE`, `SPORTS_CAR`, `TRUCK`).
- **Het save-event op de server controleerde niets** (geen ACE, geen types, geen tempo). De sandbox beperkt het wel tot de eigen resource-map.
- Opslaan ging met `io.open` op een absoluut pad. Volgens de broncode bestaan `io` en `os` server-side wel, maar binnen de sandbox (zie "Voor de kennisbasis" in [open_questions.md](open_questions.md)).

**Grenzen in de oude editor die niet kloppen** (vergeleken met 42 handlings uit onze testdata; add-ons, dus een indicatie)

| Veld | Oude grens | Echte waarden | Probleem |
|------|------------|---------------|----------|
| `fInitialDragCoeff` | 10–120 | 4–15 | 31 van de 42 onder de ondergrens |
| `fPercentSubmerged` | 0–1 ("als decimaal, bijv. 0,85") | 75–200 | het is procent; 0 deelt door nul |
| `fYawMult` (vliegen) | 0–10 | negatief (−1,45 tot −0,0002) | alle drie buiten de grens |
| `fLeanFwdForceMult`, `fLeanBakForceMult` (motor) | 0–1 | 12 en 13,5 in de motor-template | bovengrens te laag |
| `fBrakingStabilityMult`, `fInAirSteerMult` (motor) | 0–1 | −1,5 en −2,5 | ondergrens te hoog |
| `fDownForceModifier` | 0–10 | `fDownforceModifier` 0,65–275 | verkeerde schrijfwijze, en de grens is te klein |
| `fSteeringLock` | 1–90 | 30–50 | goed, maar 0 mag nooit |

**Wat bruikbaar is**

- Het schema per veld uit `VehicleAttributes.lua` (119 velden: vriendelijke naam, uitleg, type, min/max). Wel aanpassen: de kernvelden voor alle types, per veld de klasse (`CHandlingData`, `CCarHandlingData`, …), eenheid en stap, een **zacht** bereik ("normaal") los van een **hard** bereik, en de fouten in de tabel hierboven.
- `VehicleTypes.lua`: de lijst van `GetVehicleTypeRaw` (0–15) klopt.
- De zoek- en labellogica en `AttributeOrder` uit de NUI. De waarden wel in een eigen model bewaren, niet in de HTML (anders verlies je wijzigingen als je zoekt).
- Opslaan op de server in de eigen map, maar met `SaveResourceFile`, een rechtencheck, controle van de waarden, een veilige bestandsnaam, en een export die alles schrijft wat gelezen is (vlaggen als hex, `AIHandling`, `SubHandlingData`).
- De testlijst als basis voor dolu-scenario's.

**Niet bruikbaar:** de templates, het invullen met `gsub`, respawnen bij elke wijziging, en de globale `SetHandling*`.

**Velden die in de oude lijst ontbraken** (gezien in onze testdata): `fRocketBoostCapacity`, `fBoostMaxSpeed`; bij `CCarHandlingData` `fBackEndPopUp*` en `strAdvancedFlags`; bij `CFlyingHandlingData` 28 velden (o.a. `fRollMult`, `fPitchMult`, `vecTurnRes`, `vecSpeedRes`, `fTurublence*`); bij `CTrailerHandlingData` o.a. `fUprightSpringConstant` en `fAttachedMaxDistance`. Of `fPopUpLightRotation` en `fPetrolConsumptionRate` bestaan, is niet zeker (Q-H15).

### Sub-klassen van handling

| Klasse | Voor | Status |
|--------|------|--------|
| `CCarHandlingData` | auto's | `tested` (gelezen) |
| `CBikeHandlingData` | motoren (20 velden) | `tested` (gelezen) |
| `CFlyingHandlingData` | vliegtuigen **én** heli's | `tested` (gelezen bij `SHERIFFMAV`, `LSFD12`) |
| `CBoatHandlingData` | boten (±30 velden) | `community` |
| `CTrailerHandlingData` | trailers | `tested` (gelezen bij `zaccflatlit`) |
| `CVehicleWeaponHandlingData` | bewapende voertuigen (arrays, geen losse waarden) | `tested` (gelezen in `USSS`) |
| `CSubmarineHandlingData`, `CSeaPlaneHandlingData`, `CSpecialFlightHandlingData` | onderzeeër, watervliegtuig, o.a. Deluxo en Oppressor Mk II | `aanname` |

## Natives die de editor nodig heeft

| Native | Waarvoor | Status |
|--------|----------|--------|
| `GetVehicleHandlingFloat/Int/Vector` | lezen (per voertuig) | `official` |
| `SetVehicleHandlingFloat/Int/Vector/Field` | schrijven op de eigen kopie van het voertuig | `official` (broncode) |
| `SetHandlingFloat/Int/Vector/Field` | schrijven op de gedeelde handling (alleen voor nieuwe voertuigen) | `official` (broncode) |
| `ModifyVehicleTopSpeed` | nodig om `fInitialDriveForce` en `fInitialDriveMaxFlatVel` per voertuig te laten werken | `official` (native-docs) |
| `SetVehicleMaxSpeed` | snelheid begrenzen (m/s; ≤ 0 = uit) | `official` (native-docs) |
| `GetVehicleClass`, `GetVehicleTypeRaw`, `GetVehicleClassFromName`, `IsThisModelA*` | juiste grenzen en velden kiezen | `official` |
| `GetDisplayNameFromVehicleModel`, `GetEntityModel` | naam en model | `official` |
| `ForceUseAudioGameObject` | motorgeluid wisselen | `aanname` (Q-H10) |

## Bestaande editors om van te leren

Q-H11, bekeken op 23 okt 2026: de code van drie open editors gelezen. Label `community` (andermans code, niet zelf getest), tenzij er iets anders staat.

| Editor | Licentie | Laatste commit | Wat | Sync | Grenzen |
|--------|----------|----------------|-----|------|---------|
| [BabiczHandlingEditor](https://github.com/STACHY225/BabiczHandlingEditor) 1.1.0 | **AGPL-3.0** | 17 sep 2024 | Lua en een HTML-NUI. `/handling <handlingName>`, daarna LSHIFT. 47 velden van `CHandlingData` | geen | geen |
| [carmineos/fivem-handling-editor](https://github.com/carmineos/fivem-handling-editor) | MIT | `master` 9 aug 2019, branch `rework` 26 jun 2020 | C# met MenuAPI (F7). Per veld min, max en uitleg in `HandlingInfo.xml`. Presets uit een server-XML en lokaal in KVP | decorators; elke client past ze toe binnen 150 m | per veld, in te stellen |
| [kerminal/vehicleDebug](https://github.com/kerminal/vehicleDebug) 1.1.0 | MIT | 22 nov 2025 | Lua en een NUI (rechter Alt). 46 velden met uitleg. Meet topsnelheid, acceleratie en vertraging | geen | geen |

**Licentie.** Babicz is AGPL-3.0. Code daaruit in onze tool maakt de hele tool AGPL: wie hem krijgt, ook een koper, heeft recht op de broncode. Ideeën overnemen mag, code kopiëren niet. carmineos en vehicleDebug zijn MIT: code mag, met hun copyright-regel erbij. Marks oude editor (`old/oldversion`) bevat geen code van Babicz, alleen hetzelfde idee: globaal `SetHandlingFloat` en opnieuw spawnen (gezocht op o.a. `CloneVehicle`, `RoundValue` en `execCommand`). `tested` (gelezen, 23 okt)

**Wat de drie bevestigen of toevoegen**

- **Sommige velden werken pas na een extra stap** (Q-H3, Q-H9). vehicleDebug roept na elke wijziging `ModifyVehicleTopSpeed(veh, 1.0)` aan, met als commentaar "needed for some values to work". Dat klopt met de native-docs. carmineos meldt dat sommige velden niets doen, en dat andere pas werken als de auto een stukje rijdt of schade krijgt. Babicz lost het op met globaal schrijven en opnieuw spawnen. Zonder `handlingName` waarschuwt hij: "some values may not work".
- **Sync (Q-H2, Q-H12): carmineos doet al wat wij met state bags willen.** Per gewijzigd veld zet hij een decorator op het voertuig, plus `<veld>_def` met de originele waarde. Elke client loopt elke 1000 ms de voertuigen binnen 150 m langs en zet de waarden met `SetVehicleHandling*`. Elke client moet het dus zelf toepassen. Met de originele waarde op het voertuig kan iedereen terugzetten en vergelijken (F-A4, F-A5). Decorators zijn de oude vorm; wij nemen een state bag (Q-H2).
- **`handlingName` invoeren** (Q-M8). Babicz laat de gebruiker de naam typen, omdat die per voertuig alleen als hash te lezen is. Idee voor ons: de server bouwt een tabel van hash naar naam uit alle `handling.meta`'s van de resources (`LoadResourceFile`) en de vanilla-lijst in `data/`. `aanname`
- **Opnieuw spawnen zonder verlies.** Babicz' `CloneVehicle` (de eigenschappen komen uit ESX) bewaart: kenteken en kentekenstijl, schade aan carrosserie en motor, brandstof, vuil, kleuren (ook RGB, parelmoer en velgkleur), wieltype, raamtint, neon (aan en kleur), extra's 0–12, bandenrook, mods 0–46 met turbo, xenon en rook, en de livery (mod 48 plus `SetVehicleLivery`). Vooraf `SetVehicleModKit(veh, 0)`. Niet bewaard: passagiers, deuken, deuren, ramen en banden, xenon-kleur, dak-livery, interieur- en dashboardkleur, en de mod-variatie (custom tyres). Het nieuwe voertuig krijgt ook een nieuw net-ID, dus scripts voor sleutels, brandstof of garage raken het kwijt. Dit is nodig als een veld alleen bij het spawnen werkt (Q-H3).
- **Veldnamen (Q-H15).** De lijst van carmineos (56 regels, waarvan 50 getallen; bron handling.dat en de GTAMods-wiki) heeft in `CHandlingData` ook `fWeaponDamageScaledToVehHealthMult`, `fPopUpLightRotation`, `fDownforceModifier`, `fRocketBoostCapacity` en `fBoostMaxSpeed`, elk met een bereik. `fPetrolConsumptionRate`, dat Babicz leest, staat er niet in. Babicz schrijft `fDownForceModifier` en zette die regel uit, "apparently this value does not exist on some vehicles": dat is de hoofdletter (zie "Namen en klassen"). Nog testen door de lijst langs te lopen en op "No such field" te letten.
- **Bereiken per veld (Q-H4, Q-H5).** carmineos geeft per veld een min en max die op de uitersten van vanilla lijken. Bijvoorbeeld `fInitialDriveMaxFlatVel` 10–328,6, `fInitialDriveForce` 0–18, `fSteeringLock` 20–55, `fTractionCurveLateral` 1–120, `fMass` 100–60.000, `fPercentSubmerged` 45–200 en `fSuspensionRaise` −0,085–0,35. Bruikbaar als tweede mening tot onze eigen meting op build 3889. Een `fInitialDriveMaxFlatVel` tot 328,6 past bij de meta-eenheden (K9, Q-H9), niet bij "0–200 m/s".
- **`nInitialDriveGears` (Q-H14).** carmineos zette dit veld uit: "wrong type in the ExtraNative" (2019). Testen of dat nog zo is.
- **Stapgrootte.** Babicz heeft per veld een stap voor de knoppen + en −. Een aantal stappen is groter dan het hele bereik: 1,0 bij `fSuspensionUpperLimit`, `fSuspensionLowerLimit`, `fSuspensionRaise`, de bias-velden en de rolhoogtes. carmineos gebruikt één stap van 0,01. Beter: per veld een stap als deel van het normale bereik.
- **Export en klembord (F-A6, Q-H8).** Babicz en vehicleDebug exporteren alleen `fMass` t/m `nMonetaryValue`: geen vlaggen, geen `AIHandling` en geen `SubHandlingData`. Beide kopiëren via een verborgen `textarea` en `document.execCommand("copy")`. Dat werkt dus in de NUI van FiveM (twee bronnen). Babicz schrijft 15 decimalen, met de ruis van float32 (zoals 0,30000001192093); vehicleDebug kapt af. De volgorde in het template van Babicz is een aanwijzing voor de vanilla-volgorde; nakijken tegen een vanilla-bestand.
- **Meten (F-A5).** vehicleDebug houdt de hoogste snelheid (mph), acceleratie en vertraging bij, uit een buffer met snelheden. Met een knop "Reset Stats".
- **Rijden met de editor open.** vehicleDebug zet `SetNuiFocusKeepInput(true)`: je stuurt terwijl je waarden aanpast.

**Fouten in Babicz om te vermijden**

- De UI stuurt alleen waarden die "waar" zijn (`if(value)`). Een 0 kun je niet invoeren, ook niet waar 0 klopt (`fDriveBiasFront` 0 = achterwielaandrijving).
- Knoppen zonder werking: `strModelFlags` (twee keer), `strHandlingFlags` en `fDownForceModifier` staan in de HTML, maar niet in de Lua. `fPopUpLightRotation` en `fPetrolConsumptionRate` worden gelezen, maar niet getoond.
- Geen grenzen en geen controle: `Number()` neemt ook `1e9`.
- Het commando vraagt ACE `command.handling`, maar daarna opent LSHIFT de editor zonder nieuwe check.

**Marks kopie** in `F:\scripts\BabiczHandlingEditor` is upstream 1.1.0 (commit `a3bb5e9`) plus debugregels van 13 juli 2025. Eén daarvan (`'handlingName: '..handlingName`) geeft een fout bij elke wijziging van een float als je geen `handlingName` meegaf. `tested` (gelezen, diff tegen upstream)

`vehiclehandler/` in onze map is van een derde (QuantumMalice, GPL-3.0, vereist ox_lib) en gaat over schade en reparatie, niet over handling. Niet tegelijk laten draaien met handling-tests: het verlaagt het koppel bij motorschade en zet besturing uit bij kantelen. Zie [inventory.md](inventory.md).

## Open vragen

Q-H1 t/m Q-H15 in [open_questions.md](open_questions.md).
