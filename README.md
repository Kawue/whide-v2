# Whide v2
Whide is an interactive visualization tool to explore a segmentation map, created by the Hierarchical Hyperbolic Self Organizing Map (H2SOM) algorithm.


## Data Creation
The following part provides instructions to calculate a H2SOM segmentation map for any specified data set.

### Docker Version
Docker is not compatible with Windows 7, 8 and 10 Home. For details about a workaround see instructions below.

Start Docker, navigate into the msi-community-detection directory and call:
`docker build -t whide/h2som .`

### Usage
To start the script call:
`docker run --rm whide/h2som`
For information about the required command line parameter use `-h`.
The resulting data files can be can be used within WHIDE.


# Whide start similar to grine -> Ask Daniel





## Docker on Windows 7, 8 and 10 Home
1. Visit https://docs.docker.com/toolbox/toolbox_install_windows/. Follow the given instructions and install all required software to install the Docker Toolbox on Windows.
2. Control if virtualization is enabled on your system. Task Manager -> Performance tab -> CPU -> Virtualization. If it is enabled continue with Step X.
3. If virtualization is disabled, it needs to be enabled in your BIOS. Navigate into your systems BIOS and look for Virtualization Technology (VT). Enable VT, save settings and reboot. This option is most likely part of the Advanced or Security tab. This step can deviate based on your Windows and Mainboard Manufacturer.
4. Open your CMD as administrator and call `docker-machine create default --virtualbox-no-vtx-check`. A restart may be required.
5. In your OracleVM VirtualBox selected the appropriate machine (probably the one labeled "default") -> Settings -> Network -> Adapter 1 -> Advanced -> Port Forwarding. Click on "+" to add a new rule and set Host Port to 8080 and Guest Port to 8080. Be sure to leave Host IP and Guest IP empty. Also, add another rule for the Port 5000 in the same way. A restart of your VirtualBox may be needed.
6. Now you should be ready to use the Docker QuickStart Shell to call the Docker commands provided to start this tool.






# Jonas altes blablabla
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
	2. ~~Annotieren~~
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
