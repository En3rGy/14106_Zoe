# Zoe (14106)
Logikmodul zur Kommunikation mit einer Renault Zoe für den Gira KNX Homeserver. Abgeleitet vom [zoe-widget.js](https://gist.github.com/mountbatt/772e4512089802a2aa2622058dd1ded7)

## Voraussetzungen
HSL 2.0.4

## Installation
Die .hslz Datei mit dem Gira Experte importieren. Das Logikmodul ist dann in der Rubrik "Datenaustausch" verfügbar.

## Eingänge

| Nr. | Eingang | Initwert | Beschreibung |
| --- | --- | --- | --- |
| 1 | Benutzername | | MyRenault Benutzername / Email-Adresse |
| 2 | Passwort | | MyRenault Passwort 
| 3 | VIN | | VIN des Fahrzeugs |
| 4 | Zoe Modell | 2 | 1 = Phase 1<br/>2 = Phase 2 |
| 5 | Intervall [s] | 0 | Intervall, in dem MyRenault nach den Daten des Fahrzeugs abgefragt werden soll. Wenn der Wert 0 ist, findet *keine* periodische Abfrage statt.<br>Ein ggf. noch laufender Zyklus wird nach Ablauf des Intervalls noch mit einer Abfrage beendet. |
| 6 | Trigger | 0 | Wenn der Eingang eine 1 empfängt, werden die Fahrzeugdaten von MyRenault abgefragt. | 
| 7 | Klimatisierung E/A | 0 | Eine 1 am Eingang startet die Klimatisierung, eine 0 beendet sie. |
| 8 | Laden Start | 0 | Eine 1 startet den Ladevorgang. |

## Ausgänge
Alle Ausgänge sind Send-by-Change ausgeführt.

| Nr. | Ausgang                  | Initwert | Beschreibung                                                                                                                   |
|-----|--------------------------| --- |--------------------------------------------------------------------------------------------------------------------------------|
| 1   | Foto-URL                 | | URL zum Abruf eines Fotos des Fahrzeuges in der individuellen Konfiguration und Farbe.                                         |
| 2   | Batterie Lvl [%]         | 0 | Ladezustand der Batterie in %                                                                                                  |
| 3   | Restreichweite [km]      | 0 | Reichweite mit der aktuellen Akku-Ladung in km.                                                                                |
| 4   | Restladung [kWh]         | 0 | Aktuelle Ladung der Batterie in kWh.                                                                                           |
| 5   | Temperatur Batterie [°C] | 0 | Temperatur Batterie in °C                                                                                                      |
| 6   | Eingesteckt              | 0 | 1 wenn ein Ladekabel an das Fahrzeug angeschlossen ist, 0, wenn nicht.                                                         |
| 7   | Lädt                     | 0 | 1 wenn das Fahrzeugt gerade lädt, 0, wenn nicht.                                                                               |
| 8   | Gesamt km                | 0 | Gesamte bisherige Fahrleistung des Fahrzeugs in km                                                                             |
| 9   | Lat                      | 0 | Letzte gemeldete N-Position des Fahrzeugs                                                                                      |
| 10  | Lon                      | 0 | Letzte gemeldete E-Position des Fahrzeugs                                                                                      |
| 11  | Positionszeit            |  | Zeitstempel, für den zuletzt die Fahrzeugposition empfangen wurde.                                                             |
| 12  | Klimatisierung RM        | 0 | 1 - wenn Anfrage gesendet aber Antwort ausstehend<br/> 2 - für 5 min bei erfolgreichem Start der Klimatisierung<br/> 0 - sonst |
| 13  | Heartbeat                | 0 | 1 - Datenabfrage erfolgreich                                                                                                   |

## Sonstiges

- Neuberechnung beim Start: Nein
- Baustein ist remanent: Nein
- Interne Bezeichnung: 14106

### Change Log

- v01.00
    - Impr.: Fixed wrong Kameron API key May 2023
- v0.9
    - Impr.: Unit test detects broken kemeron API key
	- Bug: Fixed wrong Kameron API key March 2022
	- Impr: All outputs SBC
	- Impr: Internal variable handling
- v0.8
    - Improvement: RM Vorklimatisierung nach Ampelschema
	- Improvement: Code Refactoring
- v0.7
    - Improvement: 5min Timer für RM Klimatisierung
	- Improvement: Ausgang *Query RM* zu *Klimatisierungs RM* umbenannt
	- Improvement: Doku um fehlenden Ausgamg *Klimatisierungs RM* ergänzt
- v0.6
    - Fix: Aktualisierte Einwahldaten
- v0.5
- v0.4
    - Temperatur der Vorklimatisierung als Eingangsgröße
- v0.3
    - Fix: local variable 'gigyaJWTToken' referenced before assignment
    - Kontext auf "14106_Zoe" geändert
- v0.2
    - Query-Funktionen hinzugefügt
- v0.1
    - Initial

### Open Issues / Known Bugs

- [Vorklimatiierung Ende scheint nicht zu funktionieren, tbc](https://github.com/En3rGy/14106_Zoe/issues/2)
- [Einstellung der Temperatur der Vorklimatiisierung scheint nicht zu funktionieren, tbc](https://github.com/En3rGy/14106_Zoe/issues/3)

### Support

Für Fehlermeldungen oder Feature-Wünsche, bitte [github issues](https://github.com/En3rGy/14106_Zoe/issues) nutzen.
Fragen am besten als Thread im [knx-user-forum.de](https://knx-user-forum.de) stellen. Dort finden sich ggf. bereits Diskussionen und Lösungen.

## Code

Der Code des Bausteins befindet sich in der hslz Datei oder auf [github](https://github.com/En3rGy/14106_Zoe).

### Entwicklungsumgebung

- [Python 2.7.18](https://www.python.org/download/releases/2.7/)
    - Install python *markdown* module (for generating the documentation) `python -m pip install markdown`
- Python editor [PyCharm](https://www.jetbrains.com/pycharm/)
- [Gira Homeserver Interface Information](http://www.hs-help.net/hshelp/gira/other_documentation/Schnittstelleninformationen.zip)

## Anforderungen

-

## Software Design Description

Abgeleitet / Inspiriert von [zoe-widget.js](https://gist.github.com/mountbatt/772e4512089802a2aa2622058dd1ded7):

Die Zugangsdaten zur Anmeldung bei renault werden in einer *keychain* gehalten. Die Zugangsdaten werden zum Wechsel jeder vollen Stunde verworfen und neue erzeugt / angefordert.

## Validierung und Verifikation

-

## Lizenz

Copyright 2021 T. Paul

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
