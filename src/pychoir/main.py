from __future__ import annotations
import urwid


palette = [
    ("background", "white", "black", "", "white", "black"),
    ("selected", "white, bold", "dark red", "", "white, bold", "#806"),
    ("notselected", "white, bold", "black"),
    ("hidden", "black", "black"),
]


class MenuButton(urwid.Button):
    def __init__(self, caption, callback) -> None:
        super().__init__("", on_press=callback)
        self._w = urwid.AttrMap(
            urwid.SelectableIcon(["  * ", caption], 2),
            "notselected",
            "selected",
        )


class MarkView():
    def __init__(self, mainloop, parent):
        self.mainloop = mainloop
        self.parent = parent

    def back_to_parent(self, _button):
        self.mainloop.widget = self.parent.build()

    def build(self):
        body = [urwid.Text("Mark"), urwid.Divider()]
        for c in {'a', 'b', 'c'}:
            button = urwid.Button(c)
            urwid.connect_signal(button, "click", self.back_to_parent)
            body.append(urwid.AttrMap(button, None, focus_map="selected"))
        return urwid.ListBox(
            urwid.SimpleFocusListWalker(
                body,
                wrap_around=False
            )
        )


class MenuView():
    def __init__(self):
        widget = self.build()

        def select_on_key(key):
            if key in {'q', 'Q'}:
                raise urwid.ExitMainLoop
            elif key in {'m', 'M'}:
                self.mainloop.widget = MarkView(self.mainloop, self).build()
            elif key in {'p', 'P'}:
                raise NotImplementedError

        self.mainloop = urwid.MainLoop(widget, palette, unhandled_input=select_on_key)
        self.mainloop.screen.set_terminal_properties(colors=256, bright_is_bold=False)
        self.mainloop.run()

    def build(self):

        def make_mark_view(_button):
            self.mainloop.widget = MarkView(self.mainloop, self).build()

        operations = [
            "[M]ark attendnace",
            "[P]rint rolls",
            "[Q]uit program",
        ]

        # body = [urwid.Text(("notselected", "Menu")), urwid.Divider()]
        body = []
        for o in operations:
            button = MenuButton(o, make_mark_view)
            # urwid.connect_signal(button, "click", make_mark_view)
            body.append(urwid.AttrMap(button, None, focus_map="reversed"))
        return urwid.Overlay(
            urwid.LineBox(
                urwid.ListBox(
                    urwid.SimpleFocusListWalker(
                        body,
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


def main():
    MenuView()


if __name__ == '__main__':
    main()
