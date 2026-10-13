// Foreground game detection. Conservative about desktop utilities, browsers,
// video players and launchers. Runs on the render thread at most once/second.
// This is an opt-in heuristic, not a Windows game classification API.
#pragma once

static std::wstring DIToLower(std::wstring value) {
    std::transform(value.begin(), value.end(), value.begin(),
                   [](wchar_t ch) { return static_cast<wchar_t>(towlower(ch)); });
    return value;
}

static bool DIContainsAny(const std::wstring& text,
                          std::initializer_list<const wchar_t*> needles) {
    for (const wchar_t* needle : needles)
        if (text.find(needle) != std::wstring::npos) return true;
    return false;
}

static bool DIExcludedForegroundExecutable(const std::wstring& file) {
    return DIContainsAny(file, {
        L"chrome.exe", L"chromium.exe", L"browser.exe", L"yandex.exe",
        L"msedge.exe", L"firefox.exe", L"opera.exe", L"brave.exe",
        L"vivaldi.exe", L"arc.exe", L"steam.exe", L"steamwebhelper.exe",
        L"epicgameslauncher.exe", L"goggalaxy.exe", L"discord.exe",
        L"explorer.exe", L"applicationframehost.exe", L"searchhost.exe",
        L"startmenuexperiencehost.exe", L"systemsettings.exe", L"windhawk.exe",
        L"obs64.exe", L"obs32.exe", L"vlc.exe", L"mpv.exe",
        L"potplayer64.exe", L"potplayer.exe", L"wmplayer.exe",
        L"powerpnt.exe", L"soffice.bin", L"code.exe", L"devenv.exe",
        L"robloxstudiobeta.exe", L"unrealeditor.exe", L"unity.exe",
        L"blender.exe", L"taskmgr.exe", L"notepad.exe", L"cmd.exe",
        L"powershell.exe", L"pwsh.exe", L"conhost.exe", L"windowsterminal.exe"
    });
}

static bool DIKnownGameLocation(const std::wstring& path) {
    return DIContainsAny(path, {
        L"\\steamapps\\common\\", L"\\epic games\\", L"\\gog games\\",
        L"\\riot games\\", L"\\ea games\\", L"\\ubisoft games\\",
        L"\\roblox\\versions\\", L"\\.minecraft\\",
        L"\\minecraft\\", L"\\prismlauncher\\instances\\",
        L"\\modrinthapp\\profiles\\", L"\\curseforge\\minecraft\\",
        L"\\xboxgames\\", L"\\battle.net\\games\\"
    });
}

static bool DIKnownGameWindowClass(const std::wstring& lowerClass) {
    return DIContainsAny(lowerClass, {
        L"unitywndclass", L"unrealwindow", L"glfw30", L"sdl_app",
        L"godot", L"lwjgl"
    });
}

static bool DIKnownGameModule(DWORD pid) {
    HANDLE snapshot = CreateToolhelp32Snapshot(
        TH32CS_SNAPMODULE | TH32CS_SNAPMODULE32, pid);
    if (snapshot == INVALID_HANDLE_VALUE) return false;
    MODULEENTRY32W module{};
    module.dwSize = sizeof(module);
    bool found = false;
    if (Module32FirstW(snapshot, &module)) {
        do {
            const std::wstring name = DIToLower(module.szModule);
            if (name == L"unityplayer.dll" || name == L"gameassembly.dll" ||
                name == L"steam_api64.dll" || name == L"steam_api.dll" ||
                name == L"eossdk-win64-shipping.dll" ||
                name == L"eossdk-win32-shipping.dll") {
                found = true;
                break;
            }
        } while (Module32NextW(snapshot, &module));
    }
    CloseHandle(snapshot);
    return found;
}

static bool DIWindowsRecordedGamePath(const std::wstring& fullPath) {
    // Game Bar stores full executable paths for recognized games. Most ordinary
    // apps have no matching entry, but exclude-list is checked first regardless.
    HKEY children = nullptr;
    if (RegOpenKeyExW(HKEY_CURRENT_USER,
                      L"System\\GameConfigStore\\Children", 0,
                      KEY_READ, &children) != ERROR_SUCCESS)
        return false;
    bool found = false;
    for (DWORD i = 0; i < 2048; ++i) {
        wchar_t keyName[100]{};
        DWORD nameSize = ARRAYSIZE(keyName);
        const LONG result = RegEnumKeyExW(children, i, keyName, &nameSize,
                                          nullptr, nullptr, nullptr, nullptr);
        if (result == ERROR_NO_MORE_ITEMS) break;
        if (result != ERROR_SUCCESS) continue;
        HKEY child = nullptr;
        if (RegOpenKeyExW(children, keyName, 0, KEY_QUERY_VALUE,
                          &child) != ERROR_SUCCESS) continue;
        wchar_t value[32768]{};
        DWORD kind = 0;
        DWORD bytes = sizeof(value);
        if (RegQueryValueExW(child, L"MatchedExeFullPath", nullptr, &kind,
                             reinterpret_cast<BYTE*>(value), &bytes) == ERROR_SUCCESS &&
            (kind == REG_SZ || kind == REG_EXPAND_SZ) && bytes >= sizeof(wchar_t)) {
            value[ARRAYSIZE(value) - 1] = 0;
            if (DIToLower(value) == fullPath) found = true;
        }
        RegCloseKey(child);
        if (found) break;
    }
    RegCloseKey(children);
    return found;
}

static bool DIIsForegroundGame(HWND island, bool fullscreen) {
    HWND window = GetForegroundWindow();
    if (!window || window == island || window == GetDesktopWindow() ||
        window == GetShellWindow() || !IsWindowVisible(window))
        return false;
    DWORD pid = 0;
    GetWindowThreadProcessId(window, &pid);
    if (!pid || pid == GetCurrentProcessId()) return false;

    wchar_t path[32768]{};
    HANDLE process = OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, FALSE, pid);
    DWORD length = ARRAYSIZE(path);
    const bool havePath = process && QueryFullProcessImageNameW(
        process, 0, path, &length);
    if (process) CloseHandle(process);
    const std::wstring fullPath = havePath ? DIToLower(path) : L"";
    const auto slash = fullPath.find_last_of(L"\\/");
    const std::wstring file = slash == std::wstring::npos
        ? fullPath : fullPath.substr(slash + 1);
    if (DIExcludedForegroundExecutable(file)) return false;

    wchar_t className[256]{};
    GetClassNameW(window, className, ARRAYSIZE(className));
    const std::wstring windowClass = DIToLower(className);

    // Cache expensive module/registry scans per foreground window and PID;
    // re-evaluate fullscreen/foreground independently on every poll.
    static HWND lastWindow = nullptr;
    static DWORD lastPid = 0;
    static ULONGLONG lastScan = 0;
    static bool detected = false;
    const ULONGLONG now = GetTickCount64();
    if (window != lastWindow || pid != lastPid || now - lastScan >= 12000) {
        lastWindow = window;
        lastPid = pid;
        lastScan = now;
        detected = DIKnownGameLocation(fullPath) ||
                   DIKnownGameWindowClass(windowClass) ||
                   DIKnownGameModule(pid) ||
                   (havePath && DIWindowsRecordedGamePath(fullPath));
    }

    // Unknown fullscreen executables are likely games, but explicitly
    // excluded browsers, launchers, media apps and shells never qualify.
    return detected || (fullscreen && havePath);
}
