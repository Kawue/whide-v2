# whide-v2
New implementation of Whide.

## Project setup
```
cd whide-v2
npm install
npm run serve
```

## Anforderungen

- MZ-Liste
	1. ~~Sortieren~~
	2. Annotieren
	3. Anklicken der Masse zeigt Intensitätsbilder
	4. Anklicken der Masse makiert die MZ-Werte in den Bookmarks
- Bookmarks
	1. Einzelne Bookmarks werden getriggert durch segmentation Image oder Color Display
	2. Drei Anzeigemodi: Horizontal, Vertikal und Auto (Horizontal bei einer Bookmark, vertikal ab zwei und aufwärts.
	3. Bookmarks als Histogramm
	4. Tooltips bei einzelnen MZ-Werten
	5. Bei Klick auf die Masse wird der MZ-Wert in MZ-List angezeigt
	6. Trcking Funktion: Solange Prototyp getrackt, ist er im hauptdisplay weiß markiert	
	7. %-Anteil des Prototyps wird in den Bookmarks angezeigt
	8. Zweiter Modus: Sortierte Anzeige der MZ-Werte nach Koeffizeintenim prototypen (nur im Vertikalen Modus)
- Color-Wheel/Color-Display
	1. Color-Wheel drehen
	2. Prototypen transformieren ("Bewegen") + Default Button
	3. Granularität änderen
	4. Metainfos (In die Options)
	5. Anklicken von Prototyp triggert Bookmarks bzw. fügt Prototyp diesen hinzu
- Hauptdisplay
	1. Kiclekn auf Pixel fürgt den Prototypen den Bookmarks hinzu + (Strg + g) aktiviert Trackingmode
	2. Zoom per Scroll
	3. Strg-Scroll ändert opacity der Segmentation map
	4. Hover makiert farbe der Prototypen in Color-Wheel und Färbt Pixel in Segmentaion Map ein
