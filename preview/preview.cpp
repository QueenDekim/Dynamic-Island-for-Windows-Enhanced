// This executable compiles the EXACT Windhawk renderer, not an imitation.
// Scene fixtures below create in-memory SharedState snapshots; Renderer::Render
// paints them with the production Direct2D / DirectWrite drawing path.
#define DYNAMIC_ISLAND_PREVIEW 1
#include "../dist/mod.wh.cpp"
#include <filesystem>
#include <iostream>

static BitmapPixels SyntheticArt(int seed, int size=96) {
    BitmapPixels b;
    b.width=size; b.height=size; b.generation=seed+1;
    b.sampledAccent=D2D1::ColorF(0x9B8CE7);
    b.bgra.resize(size*size*4);
    for(int y=0;y<size;++y) for(int x=0;x<size;++x) {
        const int q=(y*size+x)*4;
        const double v=static_cast<double>(x+y)/(2*size);
        b.bgra[q]   = static_cast<BYTE>(95+95*v+seed*4);  // B
        b.bgra[q+1] = static_cast<BYTE>(65+60*v+seed*3);  // G
        b.bgra[q+2] = static_cast<BYTE>(70+75*v+seed*2);  // R
        b.bgra[q+3] = 255;
    }
    return b;
}

struct PreviewScene {
    const wchar_t* name;
    IslandKind kind;
    bool expanded=false;
    bool game=false;
    bool discord=false;
    bool privacy=false;
    bool light=false;
};

static const PreviewScene scenes[] = {
    {L"media-v2",IslandKind::Media,true},
    {L"compact-media",IslandKind::Media,false},
    {L"calendar",IslandKind::Idle,true},
    {L"weather-v2",IslandKind::Idle,true},
    {L"idle-v2",IslandKind::Idle,false},
    {L"gamebar-v2",IslandKind::Idle,false,true},
    {L"hardware-monitor",IslandKind::Idle,true},
    {L"discord-voice",IslandKind::Media,true,false,true},
    {L"discord-voice-compact",IslandKind::Media,false,false,true},
    {L"discord-signed-out",IslandKind::Idle,true,false,true},
    {L"discord-notification",IslandKind::Notification},
    {L"notification",IslandKind::Notification},
    {L"clipboard",IslandKind::Clipboard},
    {L"volume",IslandKind::Volume},
    {L"battery-low",IslandKind::BatteryLow},
    {L"caps-lock",IslandKind::CapsLock},
    {L"num-lock",IslandKind::CapsLock},
    {L"device",IslandKind::Device},
    {L"bluetooth",IslandKind::Bluetooth},
    {L"timer",IslandKind::Timer},
    {L"progress",IslandKind::Progress},
    {L"dnd",IslandKind::DoNotDisturb},
    {L"camera-detected-v2",IslandKind::Idle,false,false,false,true},
    {L"mic-detected-v2",IslandKind::Idle,false,false,false,true},
    {L"file-tray",IslandKind::Idle,true},
    {L"themes",IslandKind::Idle,false,false,false,false,true},
};

static void Seed(SharedState& state, Settings& settings,
                 const PreviewScene& scene, double now) {
    settings.sizeScale=1.0f;
    settings.textScale=1.0f;
    settings.pillOpacity=1.0f;
    settings.expandOnHover=scene.expanded;
    settings.discord=scene.discord;
    settings.weather=true;
    settings.hardwareMonitorModule=true;
    settings.fileTrayModule=std::wstring(scene.name)==L"file-tray";
    settings.showSeconds=false;
    g_idleTab=0;
    g_discordProcessRunning.store(scene.discord);
    g_discordVoiceActive.store(scene.discord && std::wstring(scene.name)!=L"discord-signed-out");
    g_autoGameOverlayActive.store(scene.game);
    state.media.available=true;
    state.media.playing=true;
    state.media.title=L"Where The Streets Have No Name";
    state.media.artist=L"U2";
    state.media.albumTitle=L"The Joshua Tree";
    state.media.sourceName=L"Yandex Music";
    state.media.art=SyntheticArt(1);
    state.media.artGeneration=state.media.art.generation;
    state.media.positionTicks=79LL*10000000LL;
    state.media.endTicks=144LL*10000000LL;
    state.media.lastUpdatedTicks=GetTickCount64();
    state.system.renderFps=144;
    state.system.cpuPercent=34;
    state.system.gpuPercent=61;
    state.system.memoryPercent=58;
    state.system.memoryUsedGB=17.2f;
    state.system.memoryTotalGB=32.0f;
    state.system.diskFreePercent=68;
    state.system.netUpMbps=1.4f;
    state.system.netDownMbps=5.8f;
    state.system.volumePercent=72;
    state.system.micActive=scene.privacy && std::wstring(scene.name).find(L"mic")!=std::wstring::npos;
    state.system.cameraActive=scene.privacy && std::wstring(scene.name).find(L"camera")!=std::wstring::npos;
    state.weather.hasData=true;
    state.weather.city=L"Amsterdam";
    state.weather.temperature=18;
    state.weather.weatherCode=116;
    state.weather.weatherDesc=L"Partly cloudy";
    state.weather.humidity=L"62%";
    state.weather.feelsLike=L"17";
    state.weather.windSpeed=L"14";
    state.weather.lastUpdated=now;
    state.discord.connected=scene.discord && std::wstring(scene.name)!=L"discord-signed-out";
    state.discord.authenticated=state.discord.connected;
    state.discord.agentAvailable=true;
    state.discord.memberCount=3;
    state.discord.guildName=L"Northwind";
    state.discord.channelName=L"General voice";
    state.discord.joinedUnix=static_cast<int64_t>(time(nullptr))-1400;
    state.discord.icon=SyntheticArt(2);
    state.discord.members.push_back({L"CAPTAIN MORIS",SyntheticArt(3)});
    state.discord.members.push_back({L"Sasha",SyntheticArt(4)});
    for(size_t i=0;i<state.discord.waveform.size();i++) state.discord.waveform[i]=0.18f+0.24f*fabs(sin(i*0.53f));
    state.discord.waveformWrite=14;
    for(size_t i=0;i<state.waveform.size();i++)state.waveform[i]=0.10f+0.38f*fabs(sin(i*0.53f));
    state.waveformWrite=32;
    state.notification.active=true;
    state.notification.app=L"Discord";
    state.notification.title=L"CAPTAIN MORIS";
    state.notification.body=L"Are you joining voice tonight?";
    state.notification.icon=SyntheticArt(3);
    state.notification.expiresAt=now+15;
    state.clipboard.active=true;
    state.clipboard.text=L"Example clipboard message";
    state.clipboard.appName=L"Explorer";
    state.clipboard.expiresAt=now+15;
    state.volume.active=true;
    state.volume.percent=72;
    state.volume.expiresAt=now+15;
    state.battery.active=true;
    state.battery.low=true;
    state.battery.percent=15;
    state.battery.expiresAt=now+15;
    state.capsLock.active=true;
    state.capsLock.capsOn=true;
    state.capsLock.isNumEvent=(std::wstring(scene.name)==L"num-lock");
    state.capsLock.numOn=true;
    state.capsLock.expiresAt=now+15;
    state.device.active=true;
    state.device.deviceName=L"USB Audio";
    state.device.expiresAt=now+15;
    state.bluetoothDevice.active=true;
    state.bluetoothDevice.deviceName=L"Bluetooth Headphones";
    state.bluetoothDevice.expiresAt=now+15;
    state.timer.active=true;
    state.timer.running=true;
    state.timer.totalSeconds=1500;
    state.timer.endsAt=now+760;
    state.progress.active=true;
    state.progress.percent=67;
    state.doNotDisturb.active=true;
    state.doNotDisturb.enabled=true;
    state.doNotDisturb.expiresAt=now+15;
    if(scene.game)settings.gameOverlay=true;
    if(scene.light) settings.w11Style=true;
    if(std::wstring(scene.name)==L"calendar")g_idleTab=1;
    if(std::wstring(scene.name)==L"weather-v2")g_idleTab=2;
    if(std::wstring(scene.name)==L"hardware-monitor")g_idleTab=3;
    if(std::wstring(scene.name)==L"discord-voice")g_idleTab=1;
    if(std::wstring(scene.name)==L"discord-signed-out")g_idleTab=4;
    if(std::wstring(scene.name)==L"file-tray") {
        g_idleTab=FileTrayTabIndex(settings);
        FileTrayItem document;
        document.name=L"deployment-notes.md";
        document.path=L"C:\\Preview\\deployment-notes.md";
        document.sizeBytes=49152;
        document.icon=SyntheticArt(3);
        state.fileTrayItems.push_back(std::move(document));
        FileTrayItem imageFile;
        imageFile.name=L"cover-art.png";
        imageFile.path=L"C:\\Preview\\cover-art.png";
        imageFile.sizeBytes=731904;
        imageFile.icon=SyntheticArt(4);
        state.fileTrayItems.push_back(std::move(imageFile));
    }
}

int main(int argc, char** argv) {
    if(argc<2) {std::cerr<<"usage: real_preview.exe OUTPUT_FOLDER\n";return 2;}
    std::filesystem::path folder=std::filesystem::path(argv[1]);
    std::filesystem::create_directories(folder);
    HRESULT hr=CoInitializeEx(nullptr,COINIT_APARTMENTTHREADED);
    if(FAILED(hr))return 3;
    // CI can run in a non-interactive Windows session. Renderer uses its
    // original GDI-backed D2D target; no visible window is ever created.
    Renderer renderer;
    if(!renderer.Initialize(nullptr)){std::cerr<<"Renderer init failed\n";return 5;}
    const double now=NowSeconds();
    int done=0;
    for(const auto& scene:scenes){
        Settings settings{};
        SharedState state{};
        Seed(state,settings,scene,now);
        Activity activity=ActivityForKind(scene.kind,settings,state);
        if(scene.expanded){
            activity.width=MediaLayout::kExpandedWidth;
            activity.height=MediaLayout::kExpandedHeight;
        }
        if(scene.game){
            activity.width=GameOverlayLayout::Width(settings.gameOverlayCompact,
                              settings.gameOverlayShowFps,4);
            activity.height=55.0f;
        }
        const bool ok=renderer.Render(state,settings,activity,std::nullopt,
                                       activity.width,activity.height,0,
                                       scene.expanded,scene.expanded,now);
        const std::wstring name=scene.name;
        const auto output=folder/(name+L".png");
        if(!ok){ std::wcerr<<L"RENDER_FAILED "<<name<<L"\n"; return 6; }
        if(!renderer.SavePreviewPng(output.wstring())){
            std::wcerr<<L"PNG_SAVE_FAILED "<<name<<L" last_error="<<GetLastError()<<L"\n";
            return 6;
        }
        ++done;
        std::wcout<<L"RENDERED "<<name<<L"\n";
    }
    renderer.Shutdown();
    CoUninitialize();
    std::cout<<"REAL_DIRECT2D_PREVIEWS="<<done<<'\n';
    return done == static_cast<int>(std::size(scenes))?0:7;
}
