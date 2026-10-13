# Dynamic Island for Windows — Enhanced

Улучшенная сборка Dynamic Island for Windows с интеграциями браузерного медиаплеера и Discord. Исходник мода поддерживается отдельно от вспомогательных инструментов.

## Репозитории и структура

| Компонент                          | Git-репозиторий                                                                                          |
| ---------------------------------- | -------------------------------------------------------------------------------------------------------- |
| Основной мод, сборка и CI          | [Dynamic-Island-for-Windows-Enhanced](https://github.com/QueenDekim/Dynamic-Island-for-Windows-Enhanced) |
| Браузерное медиа                   | [Dynamic-Island-Browser-Media-Plugin](https://github.com/QueenDekim/Dynamic-Island-Browser-Media-Plugin) |
| Discord-интеграция и OAuth backend | [Dynamic-Island-Discord-Integration](https://github.com/QueenDekim/Dynamic-Island-Discord-Integration)   |

```text
src/mod.wh.cpp                   # исходник основного Windhawk-мода
integrations/browser-media/      # Git submodule: extension + Native Messaging + browser bridge
integrations/discord/            # Git submodule: RPC agent + Docker backend + WASAPI bridge
scripts/build.py                 # собирает один автономный C++ файл для редактора Windhawk
dist/mod.wh.cpp                  # результат генерации, не входит в Git
.github/workflows/verify.yml     # проверка сборки в CI
```

## Получение полного проекта

```powershell
git clone --recurse-submodules https://github.com/QueenDekim/Dynamic-Island-for-Windows-Enhanced.git
cd Dynamic-Island-for-Windows-Enhanced
python scripts/build.py
```

Если проект был клонирован без интеграций:

```powershell
git submodule update --init --recursive
python scripts/build.py
```

Готовый **автономный** исходник для Windhawk: **dist/mod.wh.cpp**. Генератор включает C++-мосты обоих submodule в один файл, поэтому Windhawk не нужны локальные include-пути или Git после сборки. В редакторе Windhawk откройте исходник установленного мода, замените содержимое на dist/mod.wh.cpp и скомпилируйте.

Не заменяйте работающий мод напрямую, если в редакторе остались незакоммиченные изменения — сначала сохраните резервную копию.

## Браузерное медиа

Установите расширение из integrations/browser-media/extension в браузер Chromium/Яндекс.Браузер, затем настройте Native Messaging согласно [инструкции компонента](integrations/browser-media/README.md). Это обеспечивает обложки, метаданные трека, таймлайн и управление воспроизведением.

## Discord

Запуск Windows-агента, настройка Discord Developer Portal, OAuth2 и Docker-сервера задокументированы в [Discord README](integrations/discord/README.md). OAuth backend может быть опубликован через HTTPS reverse proxy. Client ID, Client Secret и API-ключ **не должны находиться в Git**.

В Discord-вкладке есть вход/выход, сведения о голосовом канале и новые уведомления. В компактном острове при подключении к голосовому каналу показываются иконка сервера, таймер, микрофон и анимированные столбцы входящего звука.

Discord-индикатор использует **WASAPI Process Loopback для дерева Discord.exe**, а не общий звук Windows. Чувствительность для тихой речи увеличена нелинейным усилением RMS с шумовым порогом; столбцы реагируют одновременно. Аудио не передаётся на backend.

## Разработка

Вносите изменения в соответствующий submodule, коммитьте/публикуйте его **сначала**, затем обновляйте указатель submodule в основном проекте:

```powershell
cd integrations/discord
git add windhawk/discord_bridge.h windhawk/discord_process_loopback.h
git commit -m "Improve Discord audio"
git push

cd ../..
git add integrations/discord
git commit -m "Update Discord integration submodule"
git push

python scripts/build.py
```

Для редактирования интеграций в их исходных репозиториях на Dekim-PC используются C:\Projects\DynamicIslandBrowserMedia и C:\Projects\DynamicIslandDiscord; папки под integrations/ — независимые Git-рабочие копии.

## Проверки

- python scripts/build.py: собирает один исходник из 4 файлов (core + 3 C++ bridge headers).
- Windows + установленный Windhawk Compiler: clang++ -fsyntax-only dist/mod.wh.cpp с флагами редактора Windhawk.
- Тесты браузерной интеграции и Discord-агента находятся в отдельных submodule.
- Проверка уровней звука в реальном звонке необходима после компиляции мода; локальный smoke-тест WASAPI подтверждает создание изолированного захвата.
