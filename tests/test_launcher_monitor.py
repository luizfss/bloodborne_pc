"""The launcher's Monitor setting: the list it shows and the BB_DISPLAY it passes to the game."""
from paths import ROOT
import importlib.util
import sys
import unittest


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


sys.path.insert(0, str(ROOT / 'launcher'))
launcher = load('bb_launcher_monitor', 'launcher/bbport_launcher_win.py')
import bbport_lang  # noqa: E402


def monitor(device, name='', width=1920, height=1080, hz=60, primary=False):
    return {'device': device, 'name': name, 'width': width, 'height': height, 'hz': hz, 'primary': primary}


class MonitorEnvironmentTests(unittest.TestCase):
    def test_chosen_monitor_reaches_the_game(self):
        settings = {**launcher.APP_DEFAULTS, 'game_dir': 'x', 'monitor': r'\\.\DISPLAY2'}
        self.assertEqual(launcher.game_environment(settings)['BB_DISPLAY'], r'\\.\DISPLAY2')

    def test_primary_monitor_leaves_the_choice_to_the_game(self):
        settings = {**launcher.APP_DEFAULTS, 'game_dir': 'x'}
        env = launcher.game_environment(settings)
        self.assertNotIn('BB_DISPLAY', env)
        self.assertEqual(launcher.APP_DEFAULTS['monitor'], '')

    def test_settings_saved_before_the_setting_existed(self):
        settings = {key: value for key, value in launcher.APP_DEFAULTS.items() if key != 'monitor'}
        self.assertNotIn('BB_DISPLAY', launcher.game_environment({**settings, 'game_dir': 'x'}))


class MonitorLabelTests(unittest.TestCase):
    def setUp(self):
        launcher.LANG = 'en'

    def test_name_mode_and_primary_mark(self):
        labels = launcher.monitor_labels([monitor(r'\\.\DISPLAY1', 'DELL U2720Q', 2560, 1440, 144, True),
                                          monitor(r'\\.\DISPLAY2', 'LG TV', 3840, 2160, 60)])
        self.assertEqual(labels, ['DELL U2720Q — 2560 × 1440, 144 Hz · primary', 'LG TV — 3840 × 2160, 60 Hz'])

    def test_unnamed_monitor_uses_its_device_name(self):
        self.assertEqual(launcher.monitor_labels([monitor(r'\\.\DISPLAY3', width=0, height=0, hz=0)]), ['DISPLAY3'])

    def test_default_refresh_rate_is_not_shown(self):
        self.assertEqual(launcher.monitor_labels([monitor(r'\\.\DISPLAY1', 'Panel', hz=1)]), ['Panel — 1920 × 1080'])

    def test_two_of_one_model_are_told_apart(self):
        labels = launcher.monitor_labels([monitor(r'\\.\DISPLAY1', 'VG27A'), monitor(r'\\.\DISPLAY2', 'VG27A')])
        self.assertEqual(labels, ['VG27A — 1920 × 1080, 60 Hz (DISPLAY1)', 'VG27A — 1920 × 1080, 60 Hz (DISPLAY2)'])

    def test_translated_primary_mark(self):
        launcher.LANG = 'pt'
        self.assertTrue(launcher.monitor_labels([monitor(r'\\.\DISPLAY1', 'A', primary=True)])[0].endswith('principal'))

    def test_no_monitors_off_windows(self):
        if sys.platform != 'win32':
            self.assertEqual(launcher.list_monitors(), [])


class MonitorTranslationTests(unittest.TestCase):
    def test_every_language_has_every_text(self):
        for language, _name in bbport_lang.LANGUAGE_NAMES:
            if language in ('', 'en', 'ru'):  # English is the key; Russian sits in the launcher
                continue
            table = bbport_lang.table(language)
            for key in bbport_lang.MONITOR_KEYS:
                self.assertTrue(table.get(key), f'{language}: {key}')
            self.assertIn('{}', table['{} (not connected: the primary monitor is used)'], language)


if __name__ == '__main__':
    unittest.main()
