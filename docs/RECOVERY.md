# Way back first

A Chinese watch rarely has a recovery mode and almost never an accessible data port (contactless charging). Firmware
that does not boot far enough to reach its Bluetooth update function leaves the watch unusable unless you open it.
That is why the way back is a phase of its own with its own gate.

## 1. Understand the update path (on the PC)

Split it into three steps and record **who** performs each:

| Step | Typical question | M78 (JieLi JL701N) |
| --- | --- | --- |
| Transfer | Who receives the file, where is it staged? | Running vendor firmware via Bluetooth, staging area in external NOR |
| Trigger | What starts the install (hand-over in RAM, flag in flash, reboot)? | Hand-over in RAM, then reboot; the trigger hangs off the UI task |
| Write | Who writes the new app into program memory? | Bootloader starts a loader taken from the update file; **no Bluetooth needed** |

This tells you which part survives a broken app. On the M78: transfer needs the running app, writing does not.

Also find out:

- **Banks:** Single bank = the old app is overwritten, no automatic fallback. Dual bank = switch only after
  verification (only if the bootloader supports it – prove it, don't assume it).
- **Checksums/signatures:** Which does the loader check? A container with a wrong checksum is often silently
  rejected – a good harmless first test of the route.
- **Bootloader fallback:** Is there one? (M78: no; the last resort would be UART on test points.)

## 2. Patterns for a safe way back

Safest first:

1. **Change nothing permanent.** Your code runs only in RAM/PSRAM and is started by the unmodified vendor firmware.
   Every reboot returns to the original firmware. (Done this way on the M78: own code from PSRAM, started by an own app.)
2. **Launcher with an emergency exit.** Your own start program runs only if a button is held during power-on.
   Without the button: normal firmware.
3. **Patched vendor firmware** in which Bluetooth update and boot stay **byte-identical** to the original (the
   verifier explicitly compares these regions).
4. **Your own firmware** only if an independent way back is confirmed *on the device* (e.g. a verified update file
   stored in external flash that can be installed without Bluetooth).

## 3. Rescue kit before the first test

Before the first modified build goes onto the watch, have ready (privately):

- the original firmware with hash and provenance record
- the last own version **confirmed on the device** (if any)
- plain-language instructions: which app, which button, how long to wait, what to do with a short connection window
- a note about the hardware reset (if any; it does not replace a way back)

## 4. Test procedure on the device

Use `templates/test-protocol.md`. Always:

1. Battery > 50 %, phone nearby, no other Bluetooth apps connected.
2. First run through the way back once (re-install the original), then the test build.
3. Record the result with a photo/video; add it to the ledger with a date.
4. On misbehaviour: mark the build withdrawn immediately, take the way back, only then look for causes.
