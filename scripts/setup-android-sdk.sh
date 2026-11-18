#!/usr/bin/env bash
# Install the Android command-line tools and the SDK packages this project needs.
#
# Codespaces images do not ship an Android SDK. This script is idempotent: it
# skips work that is already done, so it is safe to run from postCreateCommand
# on every rebuild.
set -euo pipefail

SDK_ROOT="${ANDROID_SDK_ROOT:-${ANDROID_HOME:-$HOME/android-sdk}}"
CMDLINE_VERSION="11076708"   # commandline-tools 12.0
PLATFORM="35"
BUILD_TOOLS="35.0.0"

if [ -d "$SDK_ROOT/cmdline-tools/latest/bin" ]; then
  echo "cmdline-tools already installed at $SDK_ROOT"
else
  echo "Installing Android command-line tools into $SDK_ROOT"
  mkdir -p "$SDK_ROOT/cmdline-tools"
  tmp_zip="$(mktemp -d)/commandlinetools.zip"
  curl -fsSL -o "$tmp_zip" \
    "https://dl.google.com/android/repository/commandlinetools-linux-${CMDLINE_VERSION}_latest.zip"
  unzip -q "$tmp_zip" -d "$SDK_ROOT/cmdline-tools"
  rm -rf "$SDK_ROOT/cmdline-tools/latest"
  mv "$SDK_ROOT/cmdline-tools/cmdline-tools" "$SDK_ROOT/cmdline-tools/latest"
  rm -f "$tmp_zip"
fi

export ANDROID_SDK_ROOT="$SDK_ROOT"
export ANDROID_HOME="$SDK_ROOT"
export PATH="$SDK_ROOT/cmdline-tools/latest/bin:$SDK_ROOT/platform-tools:$PATH"

yes | sdkmanager --licenses >/dev/null 2>&1 || true
sdkmanager --install \
  "platform-tools" \
  "platforms;android-${PLATFORM}" \
  "build-tools;${BUILD_TOOLS}" \
  "cmdline-tools;latest" >/dev/null

# local.properties is gitignored; write it for the local machine only.
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
printf 'sdk.dir=%s\n' "$SDK_ROOT" > "$repo_root/android/local.properties"

profile_line="export ANDROID_SDK_ROOT=\"$SDK_ROOT\""
if ! grep -qxF "$profile_line" "$HOME/.bashrc" 2>/dev/null; then
  {
    echo ""
    echo "# Android SDK (Sahaaya Drishti)"
    echo "$profile_line"
    echo "export ANDROID_HOME=\"$SDK_ROOT\""
    echo "export PATH=\"$SDK_ROOT/cmdline-tools/latest/bin:$SDK_ROOT/platform-tools:\$PATH\""
  } >> "$HOME/.bashrc"
fi

echo "Android SDK ready: $SDK_ROOT"
sdkmanager --list_installed | head -n 20
