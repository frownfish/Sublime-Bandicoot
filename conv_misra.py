import os
import re
import sublime_plugin

CPP = 'cpp'
H = 'h'
C = 'c'


class ConvertMisraTypesCommand(sublime_plugin.TextCommand):
    MISRA_TYPES = {'char': {'char': 'CHAR'},
                   'bool': {'boolean': 'BOOLEAN', 'bool': 'BOOL'},
                   'short': {'unsigned short': 'UINT16', 'short': 'INT16'},
                   'int': {'unsigned int': 'UINT32', 'int': 'INT32'},
                   'long': {'unsigned long long': 'UINT64', 'long long': 'INT64'},
                   'float': {'float': 'FLOAT4'},
                   'double': {'double': 'FLOAT8'}
                   }

    def run(self, edit):
        if len(self.view.file_name()) > 0:
            FILE_PATH = self.view.file_name()
            old_lines = []
            new_lines = []
            with open(FILE_PATH, 'r') as f:
                old_lines = f.readlines()
            for line in old_lines:
                line = self.replace_types(line)
                new_lines.append(line)
            with open(FILE_PATH, 'w') as f:
                f.writelines(new_lines)

    def is_enabled(self):
        return self.view.file_name() and len(self.view.file_name()) > 0

    def replace_types(self, line):
        for t in self.MISRA_TYPES:
            if line.find(t):
                for sub_t in self.MISRA_TYPES[t]:
                    line = re.sub(sub_t, self.MISRA_TYPES[t][sub_t], line)
        return line


class ConvertMisraPndDefsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        def replace_pnd_defs(line, prv_line, f_pat, r_pat, p_pat):
            m = f_pat.search(line)
            if m:
                if not p_pat.search(prv_line):
                    line = r_pat.format(m.group(1), m.group(2))
            return line

        if len(self.view.file_name()) > 0:
            FILE_PATH = self.view.file_name()
            FILE_TYPE = os.path.splitext(FILE_PATH)[1][1:]
            _PND_DEF_P = r'#define\s+([A-Z_0-9]+)\s+(\(?[\-0-9A-Fa-fxU]+\)?(?:\s+(?:<<|>>)\s+[\-0-9A-Fa-fxU]+\))?)'
            _PND_DEF_PRV_P = r'#else'
            PND_DEF_P = re.compile(_PND_DEF_P)
            PND_DEF_PRV_P = re.compile(_PND_DEF_PRV_P)
            PND_DEF_REPL_PAT = ''

            if FILE_TYPE in (C, H):
                PND_DEF_REPL_PAT = '#ifdef __cplusplus\n    const INT32 {0} = {1};\n#else\n    #define {0} {1}\n#endif\n'
            elif FILE_TYPE in (CPP,):
                PND_DEF_REPL_PAT = 'const INT32 {0} = {1};\n'

            old_lines = []
            new_lines = []
            with open(FILE_PATH, 'r') as f:
                old_lines = f.readlines()
            prv_line = ''
            for line in old_lines:
                _line = line
                line = replace_pnd_defs(line, prv_line, PND_DEF_P, PND_DEF_REPL_PAT, PND_DEF_PRV_P)
                new_lines.append(line)
                prv_line = _line
            with open(FILE_PATH, 'w') as f:
                f.writelines(new_lines)

    def is_enabled(self):
        return self.view.file_name() and len(self.view.file_name()) > 0
