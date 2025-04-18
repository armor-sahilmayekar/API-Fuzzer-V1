# Remove Homebrew-installed `curl` on macOS

This script uninstalls the Homebrew-installed version of `curl` on macOS and reverts any related environment variable changes from your `~/.zshrc` file.

## Why?

Homebrew installs `curl` as **keg-only** because macOS already provides it by default. If you've installed `curl` via Homebrew and no longer need it—or if it caused issues with your system—this script will cleanly remove it and restore your shell environment.

## What It Does

- Uninstalls `curl` using Homebrew
- Removes these lines from `~/.zshrc`:
  - Homebrew `curl` `PATH` addition
  - `LDFLAGS`, `CPPFLAGS`, and `PKG_CONFIG_PATH` for Homebrew `curl`
- Creates a timestamped backup of your `.zshrc` before editing

## Usage

1. **Download the script**

   Save the contents of [`remove_curl.sh`](remove_curl.sh) to your local machine.

2. **Make the script executable**

   ```bash
   chmod +x uninstall_curl_mac.sh
   ```

3. **Run the script**

   ```bash
   ./uninstall_curl_mac.sh
   ```

4. **Apply the changes**

   After the script runs, restart your terminal or manually reload your `.zshrc`:

   ```bash
   source ~/.zshrc
   ```

## Notes

- This script only targets `~/.zshrc` (Zsh). If you're using a different shell (e.g., Bash), you'll need to adapt the script accordingly.
- A backup of your `.zshrc` will be created in the same directory with a timestamp.


