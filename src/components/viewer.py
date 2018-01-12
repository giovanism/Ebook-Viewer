#!/usr/bin/env python3

# Easy eBook Viewer by Michal Daniel

# Easy eBook Viewer is free software; you can redistribute it and/or modify it under the terms
# of the GNU General Public Licence as published by the Free Software Foundation.

# Easy eBook Viewer is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public Licence for more details.

# You should have received a copy of the GNU General Public Licence along with
# Easy eBook Viewer; if not, write to the Free Software Foundation, Inc., 51 Franklin Street,
# Fifth Floor, Boston, MA 02110-1301, USA.

import gi

gi.require_version('Gtk', '3.0')
gi.require_version('WebKit2', '4.0')
from gi.repository import WebKit2, Gdk


class Viewer(WebKit2.WebView):
    def __init__(self, window):
        """
        Provides Webkit WebView element to display ebook content
        :param window: Main application window reference, serves as communication hub
        """
        WebKit2.WebView.__init__(self)

        window.props.app_paintable = True

        settings = self.get_settings()

        # Sets WebView settings for ebook display
        # No java script etc.
        
        settings.set_enable_javascript(False)
        settings.set_enable_plugins(False)
        settings.set_enable_page_cache(False)
        settings.set_enable_java(False)
        settings.set_enable_webgl(False)
        settings.set_enable_html5_local_storage(False)

        self.connect('context-menu', self.callback)

        self.__window = window

    def load_current_chapter(self):
        """
        Loads current chapter as pointed by content porvider
        """
        file_uri = self.__window.content_provider.get_chapter_file(self.__window.content_provider.current_chapter)
        # > Using WebView.load_html_string since WebView.load_uri files for some html files
        # > while load_html_string works just fine
        # > It's a bug that needs to be resolved upstream
        # Now WebView.load_uri works just fine in WebKit2

        try:
            self.load_uri("file://" + file_uri)
            print("Loaded: " + file_uri)
        except IOError:
            print("Could not read: ", file_uri)

    def set_style_night(self, is_night):
        """
        Sets style to night or day CSS
        """
        user_content_manager = self.get_user_content_manager()
        style_sheet_path = "/usr/share/easy-ebook-viewer/css/night.css" if is_night else "/usr/share/easy-ebook-viewer/css/day.css"
        with open(style_sheet_path) as style_sheet_stream:
            style_sheet = WebKit2.UserStyleSheet(
                style_sheet_stream.read(),
                WebKit2.UserContentInjectedFrames.ALL_FRAMES,
                WebKit2.UserStyleLevel.USER,
                None, None
            )
        self.set_background_color(
            Gdk.RGBA(0, 0, 0, 1) if is_night else Gdk.RGBA(1, 1, 1, 1)
        )
        user_content_manager.add_style_sheet(style_sheet)
        # TODO: Need to change current set_background_color hack, and instead
        # Allow transparency so we can use GTK theme as background
        # Can be overridden by CSS background property, needs to be rgba(0,0,0,0)
        # TODO: Prefix location of night.css so it can be set during install

    def callback(self, web_view, context_menu, event, hit_result_event):
        # Return True to disable default menu: contains copy and reload options
        # Reload messes with custom styling, doesn't reload CSS
        # App is using own "copy" right click hack
        # It will allow in future to add more options on right clicki
        self.__window.show_menu(event)
        return True
