# Your own app layer

Building every new feature as a firmware patch is expensive and risky. Better: bring a small runtime into the
(patched) vendor firmware **once**, which loads your own apps from files. After that, a new app no longer needs a
firmware build.

On the M78 this was done with a small JavaScript engine (MicroQuickJS, roughly ES5); apps arrive as a package via the
companion app and end up as a text file on the watch. The pattern transfers to other watches.

## Building blocks

| Block | Job | Note |
| --- | --- | --- |
| Engine | run scripts, limit memory | keep it small (M78: 64 KB RAM per app) |
| Entry point | "Apps" list on the watch, open/close an app | reuse an existing menu |
| Drawing/input | `draw()`, `tap(x, y)`, buttons | via the firmware's graphics routines |
| Transport | files from the companion app to the watch | reuse an existing route (M78: the e-book route) |
| Companion part | phone side of an app (internet, settings) | the watch has no internet; keys stay on the phone |
| Permissions | what an app may do | checked by the watch on every call |

## Package format (proposal, as proven on the M78)

```
my-app/
  app.json              id, name, version, permissions, companion
  app.js                program for the watch
  icon.png
  i18n/de.json, en.json
  CompanionActivity.js  optional: phone part
```

```json
{
  "id": "org.example.weather",
  "name": "Weather",
  "version": "1.0.0",
  "type": "app",
  "permissions": ["phone.message", "timer"],
  "companion": { "main": "CompanionActivity.js", "hosts": ["api.example.org"] }
}
```

## Rules that have proven themselves

- **Permissions as fixed bit numbers** that never change (old firmware + new packages stay compatible).
- **Internet only through the phone part**, only to the servers listed in `hosts`, HTTPS only, no redirects.
- **Short messages** watch ↔ phone (M78: 200 bytes); server responses stay on the phone.
- **The packer rejects anything unknown** (unknown fields, permissions, oversized packages) – typos show up at once.
- **Same input, same bytes:** build packages reproducibly.
- **Diagnostic permission** (`debug`: read-only memory access) – used to settle pin and button questions on the device.
- Apps run in the firmware task that starts them; **don't occupy the UI task permanently**, otherwise notifications,
  sync and updates stop working (M78 finding).

## Document the limits

Every watch has different limits (file size, RAM, texts per frame, icon size). They belong in the device profile under
`app_layer`, with an evidence level.
