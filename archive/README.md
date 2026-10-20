# Archief

## `v1_organizer/`

De eerste versie van deze repo (23 feb 2026, commit "init"): een PyQt6-tool die een map met losse voertuig-resources scant en ordent tot één resource met per categorie een `stream/` en een `meta/`, met dry-run en een zip-back-up.

Niet meer in gebruik, omdat:

- de mapstructuur anders gekozen is: één resource per voertuig (B1 in [doc/decisions.md](../doc/decisions.md));
- FiveM een `stream/` dieper in de resource niet streamt, alleen `<resource>/stream/` (F10 in [doc/validation_rules.md](../doc/validation_rules.md));
- hij bij botsende namen bestanden hernoemde, en dat breekt het voertuig (B20).

Het idee (een hele map in één keer ordenen, met dry-run en back-up) gaat mee naar de nieuwe tool. De volledige beoordeling staat in [doc/inventory.md](../doc/inventory.md).
