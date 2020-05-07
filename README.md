# ST-ToggleLoggings

This plugin simply provides a shortcut for turning on/off all Sublime Text's logging functionalities.
Just like you call all `sublime.log_*(...)` methods in the console.

## Installation

This plugin is not published on Package Control.

To install this plugin, you have better to: Add a custom Package Control repository.

1. Go to `Preferences` » `Package Settings` » `Package Control` » `Settings - User`.
1. Add custom repository and package name mapping as the following.

   ```javascript
   "package_name_map":
   {
     "ST-ToggleLoggings": "ToggleLoggings",
   },
   "repositories":
   [
     "https://github.com/jfcherng-sublime/ST-ToggleLoggings.git",
   ],
   ```

1. Restart Sublime Text.
1. You should be able to install this package with Package Control with the name of `ToggleLoggings`.

## Usage

- From the main menu: `Tools` -> `Sublime Text Loggings`
- From the command palette: `Toggle All Sublime Text Loggings`
