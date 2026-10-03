#!/bin/bash
# Installerar Svampkartan som en vanlig Mac-app i ~/Applications.
# Kör från projektmappen:  bash install-mac.sh
set -e
SRC="$(cd "$(dirname "$0")" && pwd)"
DEST="$HOME/Applications/Svampkartan"
APP="$HOME/Applications/Svampkartan.app"

mkdir -p "$DEST" "$HOME/Applications"
rm -rf "$DEST/web"; mkdir -p "$DEST/web"
cp -R "$SRC/index.html" "$SRC/css" "$SRC/js" "$SRC/icons" "$DEST/web/"

# Bygg .app-paketet: en liten startfil som öppnar appen i standardwebbläsaren.
rm -rf "$APP"; mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"
cat > "$APP/Contents/MacOS/Svampkartan" <<LAUNCH
#!/bin/bash
open "$DEST/web/index.html"
LAUNCH
chmod +x "$APP/Contents/MacOS/Svampkartan"
cat > "$APP/Contents/Info.plist" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>CFBundleName</key><string>Svampkartan</string>
<key>CFBundleDisplayName</key><string>Svampkartan</string>
<key>CFBundleIdentifier</key><string>se.svampkartan.app</string>
<key>CFBundleExecutable</key><string>Svampkartan</string>
<key>CFBundleIconFile</key><string>icon</string>
<key>CFBundlePackageType</key><string>APPL</string>
<key>CFBundleVersion</key><string>1.0</string>
</dict></plist>
PLIST

# Ikon: bygg .icns av PNG-filerna med macOS egna verktyg.
SET="$(mktemp -d)/icon.iconset"; mkdir -p "$SET"
cp "$SRC/icons/icon-32.png"  "$SET/icon_16x16@2x.png"
cp "$SRC/icons/icon-32.png"  "$SET/icon_32x32.png"
cp "$SRC/icons/icon-64.png"  "$SET/icon_32x32@2x.png"
cp "$SRC/icons/icon-128.png" "$SET/icon_128x128.png"
cp "$SRC/icons/icon-256.png" "$SET/icon_128x128@2x.png"
cp "$SRC/icons/icon-256.png" "$SET/icon_256x256.png"
cp "$SRC/icons/icon-512.png" "$SET/icon_256x256@2x.png"
cp "$SRC/icons/icon-512.png" "$SET/icon_512x512.png"
sips -z 16 16 "$SRC/icons/icon-32.png" --out "$SET/icon_16x16.png" >/dev/null
iconutil -c icns "$SET" -o "$APP/Contents/Resources/icon.icns"

touch "$APP"
echo "Klart: $APP"
echo "Dubbelklicka på Svampkartan i ~/Applications, eller dra ut den på skrivbordet som genväg."
