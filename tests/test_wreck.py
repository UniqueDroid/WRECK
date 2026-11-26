"""Selbsttests ohne Herstellerdateien: alle Eingaben werden hier synthetisch erzeugt."""
import io
import json
import struct
import subprocess
import sys
import tempfile
import unittest
import zipfile
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from wreck import analyze, cli, guard, workspace  # noqa: E402
from wreck.formats import jl_watchface  # noqa: E402


def run(*argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = cli.main(list(argv))
    return rc, buf.getvalue()


class AnalyzeTests(unittest.TestCase):
    def test_display_init(self):
        blob = b"\x00" * 40 + bytes.fromhex("11 2a 00 00 01 6f 2b 00 00 01 bf 3a 55 29") + b"\x00" * 40
        found = analyze.find_display_init(blob)
        self.assertEqual((found[0]["width"], found[0]["height"]), (368, 448))

    def test_images_and_chip(self):
        jpg = b"\xff\xd8\xff\xe0" + b"x" * 50 + b"\xff\xd9"
        data = b"\x00" * 100 + jpg + b"JL701N" + b"\x00" * 10
        self.assertEqual(analyze.find_images(data)[0]["size"], len(jpg))
        self.assertTrue(any("BR28" in c["family"] for c in analyze.chip_hints(data)))

    def test_strings_gbk(self):
        data = b"\x00\x00" + "老化测试".encode("gbk") + b"\x00hello world\x00"
        encs = {s["enc"] for s in analyze.strings(data, 6)}
        self.assertIn("gbk", encs)
        self.assertIn("ascii", encs)

    def test_entropy_classes(self):
        emap = analyze.entropy_map(b"\xff" * 4096 + bytes(range(256)) * 16, 4096)
        self.assertEqual(emap[0]["class"], "leer (0xFF)")

    def test_apk_inventory(self):
        with tempfile.TemporaryDirectory() as t:
            apk = Path(t) / "a.apk"
            with zipfile.ZipFile(apk, "w") as z:
                z.writestr("AndroidManifest.xml", b"")
                z.writestr("classes.dex", b"dex\n035\x00Lcom/jieli/ota/X;https://example.org/api 6e400001-b5a3-f393-e0a9-e50e24dcca9e")
                z.writestr("assets/fw.ufw", b"")
            r = analyze.apk_inventory(apk)
            self.assertEqual(r["sdk_packages"][0]["prefix"], "com/jieli/")
            self.assertIn("example.org", r["hosts"])
            self.assertEqual(r["ble_uuids"][0]["confidence"], "sicher")
            self.assertIn("assets/fw.ufw", r["firmware_like_files"])


class WatchfaceTests(unittest.TestCase):
    def make(self):
        el = struct.pack("<BBHHBBHHHBBIBBBB", 0x32, 0, 100, 200, 10, 2, 0, 30, 40, 0, 0, 28, 32, 1, 0, 0)
        return bytes([1, 0]) + b"JL" + el + b"\x00" * 64

    def test_parse(self):
        r = jl_watchface.parse(self.make())
        self.assertEqual(r["items"][0]["type_name"], "Stunde")
        self.assertEqual((r["items"][0]["x"], r["items"][0]["width"]), (100, 30))
        self.assertFalse(r["warnings"])

    def test_reject(self):
        with self.assertRaises(jl_watchface.FormatError):
            jl_watchface.parse(b"\x01\x00XX")


class GuardTests(unittest.TestCase):
    def test_blocks_vendor_material(self):
        with tempfile.TemporaryDirectory() as t:
            r = Path(t)
            (r / "fw.bin").write_bytes(b"\x00")
            (r / "k.txt").write_text("-----BEGIN " + "PRIVATE KEY-----\nabc\n")
            (r / "x.txt").write_text(".class public L" + "com/a/B;\n")
            (r / "ok.md").write_text("Nur eigene Worte.\n")
            (r / "private").mkdir()
            (r / "private" / "dump.bin").write_bytes(b"\x00")
            reasons = {f["file"]: f["reason"] for f in guard.check(r, use_git=False)}
            self.assertIn("fw.bin", reasons)
            self.assertIn("k.txt", reasons)
            self.assertIn("x.txt", reasons)
            self.assertNotIn("ok.md", reasons)
            self.assertNotIn("private/dump.bin", reasons)

    def test_allowlist(self):
        with tempfile.TemporaryDirectory() as t:
            r = Path(t)
            (r / "own.bin").write_bytes(b"\x00")
            (r / ".wreckallow").write_text("own.bin  # selbst erzeugtes Testmuster\n")
            self.assertEqual(guard.check(r, use_git=False), [])

    def test_repository_is_clean(self):
        self.assertEqual(guard.check(ROOT), [])


class WorkspaceTests(unittest.TestCase):
    def test_flow(self):
        with tempfile.TemporaryDirectory() as t:
            r = Path(t)
            rc, _ = run("--root", t, "init", "Test Uhr X1")
            self.assertEqual(rc, 0)
            dev = r / "devices" / "test-uhr-x1"
            self.assertTrue((r / "private" / "test-uhr-x1" / "inbox").is_dir())
            rc, out = run("--root", t, "--json", "next", "test-uhr-x1")
            self.assertEqual(json.loads(out)["phase"], "0-recht")
            ack = dev / "LEGAL-ACK.md"
            ack.write_text(ack.read_text().replace("ja/nein", "ja").replace("bestaetigt: nein", "bestaetigt: ja"))
            rc, out = run("--root", t, "--json", "next", "test-uhr-x1")
            self.assertEqual(json.loads(out)["phase"], "1-erkennen")
            run("--root", t, "fact", "test-uhr-x1", "chip", "JL701N", "--status", "vermutet", "--evidence", "Strings")
            run("--root", t, "fact", "test-uhr-x1", "companion_app", "DeeFit Pro", "--status", "vermutet")
            rc, out = run("--root", t, "--json", "next", "test-uhr-x1")
            res = json.loads(out)
            self.assertEqual(res["phase"], "2-beschaffen")
            self.assertFalse(res["write_to_device_allowed"])
            f = r / "private" / "test-uhr-x1" / "inbox" / "a.bin"
            f.write_bytes(b"abc")
            run("--root", t, "provenance", "test-uhr-x1", str(f), "--origin", "eigene Uhr", "--how", "Test")
            rc, out = run("--root", t, "--json", "next", "test-uhr-x1")
            self.assertEqual(json.loads(out)["phase"], "3-rueckweg")
            self.assertEqual(len((dev / "ledger.jsonl").read_text().splitlines()), 1)
            rc, _ = run("--root", t, "check", "test-uhr-x1")
            self.assertEqual(rc, 0)

    def test_validation(self):
        p = workspace.empty_profile("x", "X")
        p["facts"]["chip"].update(status="am-geraet-bestaetigt", value="JL701N")
        self.assertTrue(any("Beleg" in e for e in workspace.validate_profile(p)))

    def test_shipped_profiles_valid(self):
        for prof in (ROOT / "devices").glob("*/profile.json"):
            errs = workspace.validate_profile(json.loads(prof.read_text(encoding="utf-8")))
            self.assertEqual(errs, [], prof)


class CliTests(unittest.TestCase):
    def test_module_entry(self):
        out = subprocess.run([sys.executable, "-m", "wreck", "--version"], cwd=ROOT, capture_output=True, text=True)
        self.assertIn("wreck", out.stdout)


if __name__ == "__main__":
    unittest.main()
