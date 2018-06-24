# XtremeUpdater
*Note: XtremeUpdater is in alpha and is not stable at all. Dll backing and restoring should work, but please backup your dlls manually before using XtremeUpdater.*

*The stable file to run is `source.py` **not** `main.py` at the moment. `main.py` is not completed and it's experimental.*

Website is located at https://xtremeware.github.io/XtremeUpdater.
Support and chat at [discord](https://discord.gg/ZD6rxw9).

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