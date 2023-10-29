import gettext
import locale
from controller import Controller
from pathlib import Path


if __name__ == '__main__':
    mytextdomain='main'
    locale.setlocale(locale.LC_ALL, '')
    LOCALE_DIR = Path(__file__).parent / "locale"
    print(LOCALE_DIR)
    locale.bindtextdomain('main', LOCALE_DIR)
    gettext.bindtextdomain('main', LOCALE_DIR)
    gettext.textdomain('main')

    controller = Controller()
    controller.run()
