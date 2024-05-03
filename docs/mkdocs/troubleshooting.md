<style>body {text-align: justify}</style>

# Troubleshooting

## First steps

Before creating an issue, please check the following:

* Avoid duplicates - look through [open](https://github.com/Victor-IX/Blender-Launcher-V2/issues) and [closed](https://github.com/Victor-IX/Blender-Launcher-V2/issues?q=is%3Aissue+is%3Aclosed) issues sections and make sure your problem is not reported by another user

* Make sure you're using the latest build of Blender Launcher from [releases](https://github.com/Victor-IX/Blender-Launcher-V2/releases)

* If Blender 3D is closing right after running it from Blender Launcher, the problem is probably in the build itself or in [configuration files](https://docs.blender.org/manual/en/2.83/advanced/blender_directory_layout.html)

* For general questions go to [Blender Artists thread](https://blenderartists.org/t/blender-launcher-standalone-software-client) or our [Discord](https://discord.gg/3jrTZFJkTd)

## Catching Application Traceback

* Starting from version 1.14.0 Blender Launcher ships with separate debugging releases that used to provide deeper and more user friendly way of tracing an issue:

:   1. Download `Blender_Launcher_v%.%.%_%_x64_DEBUG.zip` for your system and reproduce the issue faced in a regular version
    1. If something goes wrong the popup window with detailed information will be shown
    1. Copy the text from the window using ++ctrl+c++

* Blender Launcher logs warnings and errors into `BL.log` by default. To retrieve additional useful debug information use `-debug` flag (compatible with debugging releases):

    === "Windows CMD"

        ```
        .\"Blender Launcher.exe" -debug
        ```

    === "Linux"

        ```
        ./Blender\ Launcher -debug
        ```

* On Linux it is possible to retrieve useful debug information using following command:

    ```
    gdb ./Blender\ Launcher
    run
    ```

## How to report a bug

To report a bug, use an [issue template](https://github.com/Victor-IX/Blender-Launcher-V2/issues/new?assignees=Victor-IX&labels=bug&template=bug_report.md&title=). Consider attaching a `BL.log` file if it exists near the `Blender Launcher` executable.

[:fontawesome-solid-bug: Submit an issue](https://github.com/Victor-IX/Blender-Launcher-V2/issues/new?assignees=Victor-IX&labels=bug&template=bug_report.md&title=){: .md-button .md-button--primary }
