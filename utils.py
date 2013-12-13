import sublime_plugin


class SplitOnCommand(sublime_plugin.TextCommand):
    def run(self, edit, **kwargs):
        selections = list(self.view.sel())
        selections.reverse()
        split_char = kwargs.get('split_char', '')
        if split_char:
            le = '\n'
            edit = self.view.begin_edit()
            for s in selections:
                line = self.view.line(s)
                pad = ' ' * (s.begin() - line.begin())
                text = self.view.substr(s)
                sects = [x.strip() for x in text.split(split_char)]
                sects[1:] = [pad + x for x in sects[1:]]
                new_text = (split_char+le).join(sects)
                self.view.replace(edit, s, new_text)
        self.view.end_edit(edit)
