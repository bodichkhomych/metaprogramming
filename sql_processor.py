import os
import sys
import sql_parser
import json

class SqlProcessor:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("not need")

    option_space_after_comma = "true"
    option_collapse_statements = "false"

    help_text = (
        "SQL code formating\n"
        "Desc:\n"
        "    command-line args to format/verify .sql files\n"
        "Usage: python3 sql_processor.py -b --config=config_templates/second_template.json -p input\n"
        "    -(p|d|f) - required argument. Specifies the execution policy:"
        "         p - dirs recursively "
        "         d - dirs (no recursion) "
        "         f - file "
        "    --config|-c)=path - optional, specifies formatting template\n"
        "    --beautify, -b - formats the input files\n"
        "    --verify, -v - verifies the input files\n"
        "\n")

    @staticmethod
    def process_files(action, files):
        # start inspection
        import inspect
        print('Ui. Function called: ', inspect.stack()[0][3])
        # end inspection

        success_cnt, errors_cnt = 0, 0
        for file in files:
            try:
                with open(file, "r", encoding='utf-8') as fin:
                    sqlcode = fin.read()

                config = {
                    'coma': SqlProcessor.option_space_after_comma,
                    'collapse': SqlProcessor.option_collapse_statements
                }
                parser = sql_parser.Parser(sqlcode, config)
                tokens = parser.run()
            except Exception as ex:
                print("Exception received when formatting file={}, ex={}".format(file, ex))
                errors_cnt += 1
                output = ''
            else:
                success_cnt += 1

            output = ''

            head, tail = os.path.split(file)
            if action == '-b':
                config = {
                    'coma': SqlProcessor.option_space_after_comma,
                    'collapse': SqlProcessor.option_collapse_statements
                }
                parser = sql_parser.Parser(sqlcode, config)
                output = parser.format()

                print('real output')
                print(output)

                result_file = os.path.join(head, 'formatted_' + tail)
                with open(result_file, "w", encoding='utf-8') as fout:
                    fout.write(output)
            # else:
            #     result_file = os.path.join(head, 'verified_' + os.path.splitext(tail)[0] + '.log')

        print('Processed %d files successfully, %d files with errors' % (success_cnt, errors_cnt))
        
    def report_error(err):
        print("Error: {}, use --help for more details!".format(err))
        sys.exit()

    def handle_parameters():
        # start inspection
        import inspect
        print('Ui. Function called: ', inspect.stack()[0][3])
        # end inspection

        params = set(sys.argv)

        if len(sys.argv) != len(params) or len(params) < 2:
            SqlProcessor.report_error('incorrect parameters amount of the script')

        elif '-h' in params or '--help' in params:
            # name, action{--help, -h}
            if len(params) != 2:
                SqlProcessor.report_error(
                    "option '%s' isn't supported by the script" % sys.argv[1])

            print(SqlProcessor.help_text)

        else:
            # name, action{--beautify, -b, --verify, -v},
            # {--config, -c}=path, option{-(p|d|f)}, in_path
            if len(params) > 5:
                SqlProcessor.report_error(
                    "incorrect amount(%d) of the script arguments" % len(params))

            action = [c for c in ('-b', '--beautify', '--verify', '-v') if c in params]
            if len(action) > 1:
                SqlProcessor.report_error("incorrect usage of action flags %s" % action)
            else:
                action = action[0] if action else '-b'

            config = [c for c in params if c.startswith('--config=') or c.startswith('-c=')]
            if len(config) > 1:
                SqlProcessor.report_error("incorrect config file options")
            elif len(config) == 1:
                config = config[0].split('=', 1)[1]
                try:
                    SqlProcessor.loadConfig(config)
                except Exception as ex:
                    SqlProcessor.report_error("error encountered when loading config file, %s" % ex)

            option = [c for c in ('-p', '-d', '-f') if c in params]
            if len(option) > 1 or len(option) == 0:
                SqlProcessor.report_error("incorrect usage of option flags %s" % option)
            else:
                option = option[0]

            files = SqlProcessor.prepare_formatting_files(option, sys.argv[-1])

            print('going to process files: ', files)
            print('action: ', action)

            SqlProcessor.process_files(action, files)

    @staticmethod
    def prepare_formatting_files(option, path):
        # start inspection
        import inspect
        print('Ui. Function called: ', inspect.stack()[0][3])
        # end inspection

        res = []
        if option == '-p':
            if not os.path.isdir(path):
                SqlProcessor.report_error("given path=%s isn't a directory" % path)
            else:
                for root, dirs, files in os.walk(path):
                    for file in files:
                        if (file.endswith('.sql') and not file.startswith('formatted_')
                                and not file.startswith('verified_')):
                            res.append(os.path.join(root, file))

        elif option == '-d':
            if not os.path.isdir(path):
                SqlProcessor.report_error("given path=%s isn't a directory" % path)
            else:
                for file in os.listdir(path):
                    if os.path.isfile(os.path.join(path, file)) and (
                            file.endswith('.sql') and not file.startswith('formatted_')
                            and not file.startswith('verified_')):
                        res.append(os.path.join(path, file))

        elif option == '-f':
            if not path.endswith('.sql'):
                SqlProcessor.report_error("incorrect format of the file=%s" % path)
            elif not os.path.isfile(path):
                SqlProcessor.report_error("given path=%s isn't a file" % path)
            else:
                res = [path]

        return res

    def loadConfig(path):
        with open(path, 'r') as fin:
            print('path', path)
            print('is file', os.path.isfile(path))
            config_dict = json.loads(fin.read())


            if config_dict['MySQLCodeStyleSettings']['option']['@name'] == 'COLLAPSE_STATEMENTS':
                SqlProcessor.option_collapse_statements = config_dict['MySQLCodeStyleSettings']['option']['@value']
                print('set self.option_collapse_statements: ', SqlProcessor.option_collapse_statements)

            if config_dict['MySQLCodeStyleSettings']['option']['@name'] == 'SPACE_AFTER_COMMA':
                SqlProcessor.option_space_after_comma = config_dict['MySQLCodeStyleSettings']['option']['@value']
                print('set self.option_space_after_comma: ', SqlProcessor.option_space_after_comma)

SqlProcessor.handle_parameters()