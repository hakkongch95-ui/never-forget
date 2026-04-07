import core.database as db
import core.scheduler as scheduler
from ui.app_window import AppWindow


def main():
    db.init_db()
    scheduler.start()

    app = AppWindow()
    try:
        app.mainloop()
    finally:
        scheduler.stop()


if __name__ == "__main__":
    main()
