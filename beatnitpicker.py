#!/usr/bin/python

import os, stat, time
import gst, gtk, gobject

from matplotlib.figure import Figure
from matplotlib.backends.backend_gtkagg import FigureCanvasGTKAgg as FigureCanvas
import scipy.io.wavfile as wavfile

interface = """
<ui>
    <menubar name="MenuBar">
        <menu action="File">
            <menuitem action="New"/>
            <menuitem action="Open"/>
            <menuitem action="Save"/>
            <menuitem action="Quit"/>
        </menu>
        <menu action="Edit">
            <menuitem action="Preferences"/>
        </menu>
        <menu action="Help">
            <menuitem action="About"/>
        </menu>
    </menubar>
</ui>
"""


class GUI(object):

    PLAY_IMAGE = gtk.image_new_from_stock(gtk.STOCK_MEDIA_PLAY, gtk.ICON_SIZE_BUTTON)
    PAUSE_IMAGE = gtk.image_new_from_stock(gtk.STOCK_MEDIA_PAUSE, gtk.ICON_SIZE_BUTTON)

    column_names = ['Name', 'Size', 'Mode', 'Last Changed']

    def about_box(self, widget):
        about = gtk.AboutDialog()
        about.set_program_name("BeatNitPycker")
        about.set_version("0.1")
        about.set_copyright("(c) Philippe \"xaccrocheur\" Coatmeur")
        about.set_comments("Simple sound sample auditor")
        about.set_website("https://github.com/xaccrocheur")
        about.set_logo(gtk.icon_theme_get_default().load_icon("gstreamer-properties", 128, 0))

        about.set_license("BeatNitPycker is free software; you can redistribute it and/or modify "
                                  "it under the terms of the GNU General Public License as published by "
                                  "the Free Software Foundation, version 2.\n\n"
                                  "This program is distributed in the hope that it will be useful, "
                                  "GNU General Public License for more details.\n\n"
                                  "You should have received a copy of the GNU General Public License "
                                  "along with this program; if not, write to the Free Software "
                                  "Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA")
        about.set_wrap_license(True);
        about.run()
        about.destroy()

    def audiofile_info(self, filename):
        # u = urllib2.urlopen(url)
        meta = filename.info()
        file_size = int(meta.getheaders('Content-Length')[0])
        estimated_bitrate = file_size/length_secs/1000*8

    def open_file(self, treeview, path, button, *args):
        audioFormats = [ ".wav", ".mp3", ".ogg", ".flac", ".MP3", ".FLAC", ".OGG", ".WAV" ]
        model = treeview.get_model()
        iter = model.get_iter(path)
        filename = os.path.join(self.dirname, model.get_value(iter, 0))
        filestat = os.stat(filename)
        if stat.S_ISDIR(filestat.st_mode):
            new_model = self.make_list(filename)
            treeview.set_model(new_model)
        elif filename.endswith(tuple(audioFormats)):
            self.the_method(self, filename)
        else:
            print "# Not an audio file"

    def onSelectionChanged(self, tree_selection) :
        (model, pathlist) = tree_selection.get_selected_rows()

        for path in pathlist :
            tree_iter = model.get_iter(path)
            value = model.get_value(tree_iter,0)
            # value =  tree_iter.set_property('text', model.get_value(iter, 0))
            print value

    def get_file_name(self, treeview, *args):
        # path, focus_column = treeview.get_cursor()
        # sel = treeview.get_selection()
        # (model, pathlist) = sel.get_selected_rows()
        # value = sel.select_path(path)
        # print value
        print "plop"

        # for path in pathlist :
            # sel = treeview.get_selection()
            # value = sel.select_path(path)
            # print value
            # tree_iter = model.get_iter(path)
            # value = model.get_value(tree_iter,0)
            # value =  tree_iter.set_property('text', model.get_value(iter, 0))
            # print value


        # (model, pathlist) = tree_selection.get_selected_rows()
        # model = treeview.get_model()
        # iter = model.get_iter(path)
        # filename = os.path.join(self.dirname, model.get_value(iter, 0))
        # filestat = os.stat(filename)
        # if stat.S_ISDIR(filestat.st_mode):
            # print "# Not a file"
        # else:
            # print filename

    def __init__(self, dname = None):
        self.window = gtk.Window()
        self.window.set_size_request(300, 600)
        self.window.connect("delete_event", self.on_destroy)
        self.window.set_icon(gtk.icon_theme_get_default().load_icon("gstreamer-properties", 128, 0))

        self.mydname = dname

    # lister

        cell_data_funcs = (None, self.file_size, self.file_mode,
                           self.file_last_changed)
        self.listmodel = self.make_list(dname)


        self.treeview = gtk.TreeView()
        self.tvcolumn = [None] * len(self.column_names)
        cellpb = gtk.CellRendererPixbuf()
        self.tvcolumn[0] = gtk.TreeViewColumn(self.column_names[0], cellpb)
        self.tvcolumn[0].set_cell_data_func(cellpb, self.file_pixbuf)
        cell = gtk.CellRendererText()
        self.tvcolumn[0].pack_start(cell, False)
        self.tvcolumn[0].set_cell_data_func(cell, self.file_name)
        self.tvcolumn[0].set_sort_column_id(0)
        self.treeview.append_column(self.tvcolumn[0])
        for n in range(1, len(self.column_names)):
            cell = gtk.CellRendererText()
            self.tvcolumn[n] = gtk.TreeViewColumn(self.column_names[n], cell)
            if n == 1:
                cell.set_property('xalign', 1.0)
            self.tvcolumn[n].set_cell_data_func(cell, cell_data_funcs[n])
            self.tvcolumn[n].set_sort_column_id(0)
            self.treeview.append_column(self.tvcolumn[n])
        self.treeview.set_model(self.listmodel)

        tree_selection = self.treeview.get_selection()
        tree_selection.set_mode(gtk.SELECTION_MULTIPLE)
        tree_selection.connect('changed', self.get_file_name)

        self.listmodel.set_sort_func(0, self.lister_compare, None)
        self.treeview.connect('row-activated', self.open_file)

        # player

        self.play_button = gtk.Button()
        self.slider = gtk.HScale()

        self.buttons_hbox = gtk.HBox()
        self.slider_hbox = gtk.HBox()

        self.buttons_hbox.pack_start(self.play_button, False)
        self.slider_hbox.pack_start(self.slider, True, True)

        self.selection = self.treeview.get_selection()
        self.model, self.selected = self.selection.get_selected_rows()

        self.play_button.set_image(self.PLAY_IMAGE)
        # self.play_button.connect('clicked', self.the_method, "/home/px/scripts/beatnitpycker/preview.mp3")

        self.slider.set_range(0, 100)
        self.slider.set_increments(1, 10)
        self.slider.connect('value-changed', self.on_slider_change)

        self.playbin = gst.element_factory_make('playbin2')
        # self.playbin.set_property('uri', 'file:////home/px/scripts/beatnitpycker/preview.mp3')

        self.bus = self.playbin.get_bus()
        self.bus.add_signal_watch()

        self.bus.connect("message::eos", self.on_finish)

        self.is_playing = False

        # end player

        vbox = gtk.VBox()

        # Plot image

        self.plot_hbox = gtk.HBox()
        self.pimage = gtk.Image()
        scroll_list = gtk.ScrolledWindow()

        scroll_list.add(self.treeview)

        self.plot_hbox.pack_start(self.pimage, True, True, 1)
        vbox.pack_start(self.plot_hbox, False, False, 1)
        vbox.pack_start(self.slider_hbox, False, False, 1)
        vbox.pack_start(self.buttons_hbox, False, False, 1)
        vbox.pack_start(scroll_list, True, True, 1)

        uimanager = gtk.UIManager()
        accelgroup = uimanager.get_accel_group()
        self.window.add_accel_group(accelgroup)

        self.actiongroup = gtk.ActionGroup("uimanager")

        self.actiongroup.add_actions([
            ("New", gtk.STOCK_NEW, "_New", None, "Create a New Document"),
            ("Open", gtk.STOCK_OPEN, "_Open", None, "Open an Existing Document"),
            ("Save", gtk.STOCK_SAVE, "_Save", None, "Save the Current Document"),
            ("Quit", gtk.STOCK_QUIT, "_Quit", None, "Quit the Application", lambda w: gtk.main_quit()),
            ("File", None, "_File"),
            ("Preferences", gtk.STOCK_PREFERENCES, "_Preferences", None, "Edit the Preferences"),
            ("Edit", None, "_Edit"),
            ("About", gtk.STOCK_ABOUT, "_About", None, "yow", self.about_box),
            ("Help", None, "_Help")
        ])

        uimanager.insert_action_group(self.actiongroup, 0)
        uimanager.add_ui_from_string(interface)

        menubar = uimanager.get_widget("/MenuBar")
        vbox.pack_start(menubar, False)

        self.window.add(vbox)
        self.window.show_all()
        self.treeview.grab_focus()
        return


    def the_method(self, button, filename):
        if not self.is_playing:
            self.playbin.set_state(gst.STATE_READY)
            self.playbin.set_property('uri', 'file:///' + filename)
            self.play_button.set_image(self.PAUSE_IMAGE)
            self.is_playing = True
            self.playbin.set_state(gst.STATE_PLAYING)
            gobject.timeout_add(100, self.update_slider)
            if filename.endswith(".wav") or filename.endswith(".WAV") :
                # Plotting
                rate, data = wavfile.read(open(filename, 'r'))
                f = Figure(figsize=(4.5,0.5))
                self.drawing_area = FigureCanvas(f)
                a = f.add_subplot(111, axisbg=(0.1843, 0.3098, 0.3098))
                a.plot(range(len(data)),data, color="OrangeRed",  linewidth=0.5, linestyle="-")
                a.axis('off')
                f.savefig(
                    os.path.expanduser('~') + '/.f.png',
                    height = 10,
                    width = 10,
                    type = 'jpg',
                    pointsize = 10,
                    family = "Helvetica",
                    sublines = 0,
                    toplines = 0,
                    leftlines = 0
                )
                self.pimage.set_from_file(os.path.expanduser('~') + '/.f.png')

        else:
            self.play_button.set_image(self.PLAY_IMAGE)
            self.is_playing = False
            self.playbin.set_state(gst.STATE_PAUSED)

    # Lister funcs

    def lister_compare(self, model, row1, row2, user_data):
        sort_column, _ = model.get_sort_column_id()
        value1 = model.get_value(row1, sort_column)
        value2 = model.get_value(row2, sort_column)
        if value1 < value2:
            return -1
        elif value1 == value2:
            return 0
        else:
            return 1

    def make_list(self, dname=None):
        if not dname:
            self.dirname = os.path.expanduser('~')
        else:
            self.dirname = os.path.abspath(dname)
        self.window.set_title("BeatNTPK : " + self.dirname)
        files = [f for f in os.listdir(self.dirname) if f[0] != '.']
        files.sort()
        files = ['..'] + files
        listmodel = gtk.ListStore(object)
        for f in files:
            listmodel.append([f])
        return listmodel

    def file_pixbuf(self, column, cell, model, iter):
        audioFormats = [ ".wav", ".mp3", ".ogg", ".flac", ".MP3", ".FLAC", ".OGG", ".WAV" ]
        filename = os.path.join(self.dirname, model.get_value(iter, 0))
        filestat = os.stat(filename)
        if stat.S_ISDIR(filestat.st_mode):
            pb = gtk.icon_theme_get_default().load_icon("folder", 24, 0)
        elif filename.endswith(tuple(audioFormats)):
            pb = gtk.icon_theme_get_default().load_icon("audio-volume-medium", 24, 0)
        else:
            pb = gtk.icon_theme_get_default().load_icon("edit-copy", 24, 0)
        cell.set_property('pixbuf', pb)
        return

    def file_name(self, column, cell, model, iter):
        cell.set_property('text', model.get_value(iter, 0))
        return

    def file_size(self, column, cell, model, iter):
        filename = os.path.join(self.dirname, model.get_value(iter, 0))
        filestat = os.stat(filename)
        cell.set_property('text', filestat.st_size)
        return

    def file_mode(self, column, cell, model, iter):
        filename = os.path.join(self.dirname, model.get_value(iter, 0))
        filestat = os.stat(filename)
        cell.set_property('text', oct(stat.S_IMODE(filestat.st_mode)))
        return

    def file_last_changed(self, column, cell, model, iter):
        filename = os.path.join(self.dirname, model.get_value(iter, 0))
        filestat = os.stat(filename)
        cell.set_property('text', time.ctime(filestat.st_mtime))
        return


    # player funcs

    def on_finish(self, bus, message):
        self.playbin.set_state(gst.STATE_PAUSED)
        self.play_button.set_image(self.PLAY_IMAGE)
        self.is_playing = False
        self.playbin.seek_simple(gst.FORMAT_TIME, gst.SEEK_FLAG_FLUSH, 0)
        self.slider.set_value(0)

    def on_destroy(self, *args):
        # NULL state allows the pipeline to release resources
        self.playbin.set_state(gst.STATE_NULL)
        self.is_playing = False
        # os.environ['HOME']
        try:
            with open(os.path.expanduser('~') + '/.f.png'):
                os.remove(os.path.expanduser('~') + '/.f.png')
        except IOError:
            pass

        gtk.main_quit()

    def on_slider_change(self, slider):
        seek_time_secs = slider.get_value()
        self.playbin.seek_simple(gst.FORMAT_TIME, gst.SEEK_FLAG_FLUSH | gst.SEEK_FLAG_KEY_UNIT, seek_time_secs * gst.SECOND)

    def update_slider(self):
        if not self.is_playing:
            return False # cancel timeout

        try:
            nanosecs, format = self.playbin.query_position(gst.FORMAT_TIME)
            duration_nanosecs, format = self.playbin.query_duration(gst.FORMAT_TIME)

            # block seek handler so we don't seek when we set_value()
            self.slider.handler_block_by_func(self.on_slider_change)

            self.slider.set_range(0, float(duration_nanosecs) / gst.SECOND)
            self.slider.set_value(float(nanosecs) / gst.SECOND)

            self.slider.handler_unblock_by_func(self.on_slider_change)

        except gst.QueryError:
            # pipeline must not be ready and does not know position
         pass

        return True # continue calling every 30 milliseconds


def main():
    gtk.main()

if __name__ == "__main__":
    GUI()
    main()
