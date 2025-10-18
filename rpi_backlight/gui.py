import sys
import os

from . import Backlight


def main():
    """Start the graphical user interface."""
    try:
        import gi

        gi.require_version("Gtk", "3.0")
        gi.require_version("GdkPixbuf", "2.0")
        from gi.repository import Gtk, GLib, GdkPixbuf
    except ImportError:
        print("Please install pygobject to use the rpi-backlight GUI!")
        sys.exit()

    if len(sys.argv) > 1:
        backlight = Backlight(backlight_sysfs_path=sys.argv[1])
    else:
        backlight = Backlight()

    def update_scale():
        if scale.get_value() != backlight.brightness:
            scale.set_value(backlight.brightness)
        return True

    def update_brightness(*_):
        backlight.brightness = int(scale.get_value())

    window = Gtk.Window(title="rpi-backlight GUI")
    icon_path = (
        "/usr/share/icons/Adwaita/symbolic/status/display-brightness-symbolic.svg"
    )

    # Try several ways to set the window/application icon. On some systems
    # the window manager ignores per-window icons or requires specific formats.
    try:
        if os.path.exists(icon_path):
            try:
                # Preferred: set icon from file (lets GTK pick a loader)
                window.set_icon_from_file(icon_path)
            except Exception:
                # Fall back to loading a GdkPixbuf and setting that explicitly
                try:
                    pixbuf = GdkPixbuf.Pixbuf.new_from_file(icon_path)
                    window.set_icon(pixbuf)
                except Exception:
                    # Another fallback: set default icon for all windows
                    try:
                        Gtk.Window.set_default_icon_from_file(icon_path)
                    except Exception:
                        pass
    except Exception:
        # Never crash the GUI because of icon problems
        pass

    scale = Gtk.Scale(
        orientation=Gtk.Orientation.HORIZONTAL,
        adjustment=Gtk.Adjustment(
            value=backlight.brightness, lower=0, upper=100, step_increment=1
        ),
    )

    scale.connect("value-changed", update_brightness)
    scale.set_size_request(350, 50)

    main_container = Gtk.Fixed()
    main_container.put(scale, 10, 10)

    window.connect("delete-event", Gtk.main_quit)
    window.connect("destroy", Gtk.main_quit)
    window.add(main_container)
    window.resize(400, 50)
    window.set_position(Gtk.WindowPosition.CENTER)
    window.show_all()

    GLib.timeout_add(100, update_scale)

    Gtk.main()
