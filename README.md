# XtremeUpdater
*Note: XtremeUpdater is in alpha and is not stable at all. Dll backing and restoring should work, but please backup your dlls manually before using XtremeUpdater.*

Website is located at https://xtremeware.github.io/XtremeUpdater.
Support and chat at [discord](https://discord.gg/ZD6rxw9).

**Known issues**
  - *Refresh button* does not work
  - Images in *Game Collection* may sometimes fail to show up

## v0.55
**New features**
  - Added option to remove cached images from the *Game Collection*

**Tweaks**
  - Images in the *Game Collection* now cache in `.cache/img/`.

**Bugfixes**
  - Fixed bug which caused some images in the *Game Collection* to fail to load.

## v0.54
**Bugfixes**
  - Fixed bug causing games located on other that the system drive to not start up and load to *Updater* correctly.

## v0.53
**New features**
  - Added support for multiple drives

**Tweaks**
  - App now has an icon in the window manager (Python icon on the taskbar still remains, of course)
  - Selecting and deselecting dlls now has a little animation

**Bugfixes**
  - Fixed bug causing to allow unavailable dll selection
  - Fixed bug causing the app to crash upon selecting directory offline

## v0.52
*Code cleanup*

**Bugfixes**
 - Fixed bug causing freeze when selecting directory without any dlls.
 - Fixed bug which caused refresh button to crash the app

## v0.51
*Note: Added support for kivy 1.10.1*

 **New features**
  - You can now start games from the *Game Collection*
  
  *Note: Some Steam games may not start correctly due to missing initialization of the Steam Client.*

## v0.5
*Note: We are removing `source.py` and all of it's deps in this update and everything is now ported to [kivy](https://github.com/kivy/kivy) gui.*

  **New features**
   - Mouse highlight
   - *Game Collection*

  **Removed features**
   - Available dlls cache

  **Tweaks**
   - Made few tweaks to buttons
   - Added texture to the head
   - App title is now bold
   - Changed app title colors
   - Path input font is now bold

  **Bugfixes**
   - Fixed bug which caused *dll list* to not display during 2nd or more directory selection
   - Fixed bug which caused *select all* button to stay enabled after updating completion
   - Fixed bug which caused to load available dlls twice

## v0.4
**Tweaks**
   - Dlls now do not backup and overwrite when they are not of a newer version

**Bugfixes**
   - Fixed error when updating dlls in some cases

## v0.3
  **New features**
   - *Select all* button to the *dll view*
   - *Restore* support
   - *Tweaks*
   - *Refresh* button in case sync fails

   **Tweaks**
   - Tweaked *Update* and *Restore* buttons' behavior
   - Changed scrollbar color so it's now visible when scrolling over selected dlls
   - Moved *info* text a bit up
   - Redesigned texture for navigation buttons; depth
   - Increased window size from *800x450* to *1000x550*

  **New system tweaks**
   - Delete tempdir

   **Bugfixes**
   - *Update* and *Restore* buttons are no longer visible when updating dlls

## v0.2
 **New features**
  - Added dll updater

## v0.1
**Bugfixes**
- Fixed syncing error loop when syncing with GitHub
- When sync error is raised, _Games_ tab will now reset to its default state after 2 seconds