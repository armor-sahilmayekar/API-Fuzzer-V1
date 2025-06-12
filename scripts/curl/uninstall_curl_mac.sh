#!/bin/bash

# Uninstall curl
echo "Uninstalling curl via Homebrew..."
brew uninstall curl

# Backup .zshrc
ZSHRC="$HOME/.zshrc"
BACKUP="$ZSHRC.backup.$(date +%s)"
if [ -f "$ZSHRC" ]; then
    echo "Backing up $ZSHRC to $BACKUP"
    cp "$ZSHRC" "$BACKUP"
fi

# Remove curl-specific exports from .zshrc
echo "Cleaning up .zshrc entries related to Homebrew curl..."

sed -i '' '/\/opt\/homebrew\/opt\/curl\/bin/d' "$ZSHRC"
sed -i '' '/LDFLAGS="-L\/opt\/homebrew\/opt\/curl\/lib"/d' "$ZSHRC"
sed -i '' '/CPPFLAGS="-I\/opt\/homebrew\/opt\/curl\/include"/d' "$ZSHRC"
sed -i '' '/PKG_CONFIG_PATH="\/opt\/homebrew\/opt\/curl\/lib\/pkgconfig"/d' "$ZSHRC"

echo "Done. Restart your terminal or run 'source ~/.zshrc' to apply changes."