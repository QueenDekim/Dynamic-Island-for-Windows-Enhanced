// Deterministic, offline checks for the foreground game heuristics.
#include <windows.h>
#include <tlhelp32.h>
#include <algorithm>
#include <initializer_list>
#include <string>
#include <cwctype>
#include <cstdio>
#include "../src/game_detection.h"
int main() {
    auto check = [](bool condition, const char* label) {
        if (!condition) { fprintf(stderr, "FAIL: %s\n", label); return false; }
        printf("PASS: %s\n", label);
        return true;
    };
    bool ok = true;
    ok &= check(DIKnownGameLocation(L"c:\\program files (x86)\\steam\\steamapps\\common\\elden ring\\game\\eldenring.exe"), "Steam game installation");
    ok &= check(DIKnownGameLocation(L"d:\\epic games\\mygame\\mygame.exe"), "Epic Games directory");
    ok &= check(DIKnownGameLocation(L"c:\\users\\guest\\appdata\\roaming\\.minecraft\\versions\\minecraft.exe"), "Minecraft installation");
    ok &= check(!DIKnownGameLocation(L"c:\\windows\\system32\\notepad.exe"), "Notepad is not a game installation");
    ok &= check(DIKnownGameWindowClass(L"unitywndclass"), "Unity engine window");
    ok &= check(DIKnownGameWindowClass(L"glfw30"), "GLFW game window");
    ok &= check(!DIKnownGameWindowClass(L"chrome_widgetwin_1"), "Browser class excluded from engine detection");
    ok &= check(DIExcludedForegroundExecutable(L"chrome.exe"), "Chrome excluded");
    ok &= check(DIExcludedForegroundExecutable(L"yandex.exe"), "Yandex excluded");
    ok &= check(DIExcludedForegroundExecutable(L"discord.exe"), "Discord excluded");
    ok &= check(DIExcludedForegroundExecutable(L"steam.exe"), "Steam launcher excluded");
    ok &= check(DIExcludedForegroundExecutable(L"powerpnt.exe"), "PowerPoint excluded");
    ok &= check(DIExcludedForegroundExecutable(L"robloxstudiobeta.exe"), "Game editor excluded");
    ok &= check(!DIExcludedForegroundExecutable(L"eldenring.exe"), "Game executable allowed");
    ok &= check(!DIIsForegroundGame(GetForegroundWindow(), true), "Island foreground must never identify itself as game");
    return ok ? 0 : 1;
}
