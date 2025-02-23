from __future__ import annotations
import urwid


palette = [
    ("background", "white", "black", "", "white", "black"),
    ("selected", "white, bold", "dark red", "", "white, bold", "#806"),
    ("notselected", "white, bold", "black"),
    ("hltred", "light red, bold", "black", "", "light red, bold", "black")
]


class MenuButton(urwid.Button):
    def __init__(self, caption, callback) -> None:
        super().__init__("", on_press=callback)
        self._w = urwid.AttrMap(
            urwid.SelectableIcon(["  * ", caption], 2),
            "notselected",
            "selected",
        )


class MenuView():
    def __init__(self, mainloop):

        self.mainloop = mainloop
        self.parent = None

    def build(self):
        """
            Its job is to define a new widget and set mainloop to this widget.
        """

        def _mark(_button):
            MarkView(self.mainloop, self).build()

        def _print(_button):
            raise NotImplementedError

        def _quit(_button):
            raise urwid.ExitMainLoop()

        def select_on_key(key):
            if key in {'q', 'Q'}:
                raise urwid.ExitMainLoop
            elif key in {'m', 'M'}:
                MarkView(self.mainloop, self).build()
            elif key in {'p', 'P'}:
                raise NotImplementedError

        buttons = [
            MenuButton("[M]ark Attendance", _mark),
            MenuButton("[P]rint rolls", _print),
            MenuButton("[Q]uit program", _quit),
        ]

        new_widget = urwid.Overlay(
            urwid.LineBox(
                urwid.ListBox(
                    urwid.SimpleFocusListWalker(
                        buttons,
                        wrap_around=False
                    )
                ),
                title='Menu',
                title_attr='notselected',
                tline=urwid.LineBox.Symbols.HEAVY.HORIZONTAL,
                bline=urwid.LineBox.Symbols.HEAVY.HORIZONTAL,
                lline=urwid.LineBox.Symbols.HEAVY.VERTICAL,
                rline=urwid.LineBox.Symbols.HEAVY.VERTICAL,
                tlcorner=urwid.LineBox.Symbols.HEAVY.TOP_LEFT,
                trcorner=urwid.LineBox.Symbols.HEAVY.TOP_RIGHT,
                blcorner=urwid.LineBox.Symbols.HEAVY.BOTTOM_LEFT,
                brcorner=urwid.LineBox.Symbols.HEAVY.BOTTOM_RIGHT,
            ),
            urwid.AttrMap(urwid.SolidFill(" "), "background"),
            align=urwid.CENTER,
            width=(urwid.RELATIVE, 20),
            valign=urwid.MIDDLE,
            height=(urwid.RELATIVE, 20),
            left=4,
            right=4,
            top=2,
            bottom=2,
            min_width=20,
            min_height=9,
        )

        if self.mainloop is None:
            self.mainloop = urwid.MainLoop(new_widget, palette, unhandled_input=select_on_key)
            self.mainloop.screen.set_terminal_properties(colors=256, bright_is_bold=False)
            self.mainloop.run()

        else:
            self.mainloop.widget = new_widget


class MarkView():
    def __init__(self, mainloop, parent):
        self.mainloop = mainloop
        self.parent = parent

    def back_to_parent(self, _button):
        self.parent.build()

    def build(self):
        # Update unhandled_input
        def select_by_key(key):
            if key in {'q', 'Q'}:
                raise urwid.ExitMainLoop()
            if key == 'backspace':
                self.parent.build()

        self.mainloop.unhandled_input = select_by_key

        # Return main loop widget for update
        new_widget = urwid.Frame(
            body=urwid.LineBox(
                urwid.Text("hello"),
                title="Mark attendance for which rehearsal?"
            ),
            footer=urwid.Text(
                [
                    ("background", "["),
                    ("hltred", "Q"),
                    ("background", "] to quit."),
                    ("background", "["),
                    ("hltred", "Backspace"),
                    ("background", "] to go back."),
                ]
            ),
        )

        self.mainloop.widget = new_widget


def main():
    MenuView(None).build()


if __name__ == '__main__':
    main()
