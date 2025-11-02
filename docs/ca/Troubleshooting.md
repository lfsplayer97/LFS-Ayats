# Resolució d’errors

## No es pot connectar a InSim
- Revisa host/port i que LFS estigui en execució.
- Tallafoc: permet entrada/sortida per a l’aplicació.
- Prova `127.0.0.1` si tot corre a la mateixa màquina.

## Sense telemetria
- Assegura que hi ha una sessió activa a LFS (en pista).
- Comprova l’estat “Connected” a la UI.
- Activa logs a nivell `debug` i mira les entrades recents.

## Unitats incorrectes
- Canvia a SI a **Settings**. Refes la sessió.
