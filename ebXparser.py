#!/usr/bin/env python

############################ July 2016  ##########################
###########################AKSHIT KHANNA##########################

import sys
import subprocess
import argparse
import os.path

class ebXparser:
    def __init__(self, _input_file):
        self.namespace_map   = {}
        self._ebx_file       = _input_file
        self.whitespaces     = ["\r","\t"," "]
        self._config_dir     = "/usr/local/sbin/ebXparser/configs"
        self._namespace_file = "general_options.conf"
        self._chunks         = []
        self._option_count   = 1
        self._ebx_format     = "general"

    def check_file(self):
        if(not os.path.isfile(self._ebx_file)):
            print("This file does not exist.")
            sys.exit()

    def check_pip(self):
        try:
            subprocess.check_output(["pip"],stderr=subprocess.STDOUT)
            return 1
        except subprocess.CalledProcessError, e:
            print ("Unable to find pip. Skipping yamllint installation")
            return 0

    def install_yamllint(self):
        if(subprocess.call("type " + "yamllint", shell=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0):
            return 1
            
        if(self.check_pip() == 1):
            try:
                subprocess.check_output(["sudo" , "pip", "install", "yamllint"],stderr=subprocess.STDOUT)
                return 1
            except subprocess.CalledProcessError, e:
                print ("Unable to install yamllint.. Moving on")
                return 0

    def validate_ebextensions(self):
        with open(self._ebx_file) as f:
                lines = f.readlines()
        self.header_check(lines[0])
        self.yaml_lint()
        _length = len(lines) - 1
        if ((_length % 3 ) == 0):
            self._ebx_format = "general"
            print "Recognized General Format"
            self._chunks = [lines[x:x+3] for x in xrange(1, len(lines), 3)]
        elif ((_length % 2 ) == 0):
            self._ebx_format = "shorthand"
            print "Recognized Shorthand Format"
            self._chunks = [lines[x:x+2] for x in xrange(1, len(lines), 2)]
        else:
            print("Invalid Syntax:: ", self.print_usage())
            sys.exit()

        #print self._chunks
        for _option_setting in self._chunks:
            if(self._ebx_format == "general"):
                _namespace_string   = _option_setting[0].strip()
                _option_name_string = _option_setting[1].strip()
                _value_string       = _option_setting[2].strip()
            else:
                _namespace_string   = "- namespace:  " + _option_setting[0].strip()
                if(_namespace_string.endswith(':')):
                    _namespace_string   = _namespace_string[:-1]
                    _option_string_list = _option_setting[1].split(':')
                    _option_name_string = "option_name:  " + _option_string_list[0].strip()
                    _value_string       = "value: " + _option_string_list[1].strip()
                else:
                    print "Line:", _option_setting[0].strip(), "::Invalid Format. Should end with :"
                    sys.exit()

            _namespace          = self.validate_namespace(_namespace_string)
            _default_value      = self.validate_option(_namespace, _option_name_string)
            _default_type       = self.check_value_type(_default_value.strip())
            _option_value       = self.return_value(_value_string)
            _result             = self.validate_option_value(_option_value, _default_type, _default_value, _option_name_string)

    def return_value(self, _value_string):
        try:
            _splits    = _value_string.split(':')
            _value     = _splits[1].strip()
            _pre_value = _splits[0].strip()

            if(_pre_value != "value"):
                print ("Final Line of an option setting should be 'value: '")
                print ("It is:: ",_pre_value)
                sys.exit()
            else:
                return _value
        except:
            print("Invalid Value String")
            sys.exit()

    def validate_option_value(self, _option_value, _default_type, _default_value, _option_name_string):
        self._option_count  = self._option_count + 1
        if(_default_type == "limits"):
            _limits = _default_value.split('-')
            if( len(_limits) > 1 ):
                _upper_limit = int(_limits[1].strip())
                _lower_limit = int(_limits[0].strip())
                try:
                    _value    = int(_option_value)
                    if( _value not in range(_lower_limit, (_upper_limit + 1))):
                        print "Line:", self._option_count, "::Invalid value for:: ", _option_name_string, " Values can be ", _default_value
                        sys.exit()
                    else:
                        print "Template Verified: ",_option_name_string
                except:
                    print "Line:", self._option_count , "::Option: ", _option_name_string, " accepts Integer values"
                    sys.exit()
            else:
                print "Seems like someone is upto no good. Option files have been messed with."

        elif(_default_type == "options"):
            _options = _default_value.split(',')
            if( len(_options) > 1 ):
                for option in _options:
                    option = option.strip()
                if( _option_value not in _options ):
                    print "Line:", self._option_count, "::Invalid value for:: ", _option_name_string, " Values can be ", _default_value
                    sys.exit()
                else:
                    print "Template Verified: ",_option_name_string
            else:
                print "Seems like someone is upto no good. Option files have been messed with."

        elif(_default_type == "integers"):
            _integers = _default_value.split('\\')
            if( len(_limits) > 1 ):
                for integer in _integers:
                    integer = int(integer)
                try:
                    _value    = int(_option_value)
                    if( _value not in _integers):
                        print "Line:", self._option_count, "::Invalid value for:: ", _option_name_string, " Values can be ", _default_value
                        sys.exit()
                    else:
                        print "Template Verified: ",_option_name_string
                except:
                    print "Line:", self._option_count, "::Option: ", _option_name_string, " accepts Integer values"
                    sys.exit()
            else:
                print "Seems like someone is upto no good. Option files have been messed with."

        elif(_default_type == "string"):
            try:
                _value = str(_option_value)
                print "Template Verified: ",_option_name_string
            except:
                print "Line:", self._option_count, "::Option: ", _option_name_string, " accepts only String values"
                sys.exit()

        else:
            print "Seems like someone is upto no good. Option files have been messed with."


    def check_value_type(self, _default_value):
        _values = _default_value.split(',')    #split by "," before "-" for values like "email-json" in "aws_elasticbeanstalk_sns_topics"
        if ( len(_values) > 1 ):
            return "options"
        else:
            _values = _default_value.split('-')
            if ( len(_values) > 1 ):
                return "limits"
            else:
                _values = _default_value.split('\\')
                if ( len(_values) > 1 ):
                    return "integers"
                else:
                    if (_default_value == "string"):
                        return "string"
                    else:
                        print ("Unable to parse default values")
                        sys.exit()


    def validate_option(self, _namespace, _option_string):
        try:
            self._option_count  = self._option_count + 1
            _split_string  = _option_string.strip().split(':')
            _option        = _split_string[1].strip()
            _pre_option    = _split_string[0].strip()

            if(_pre_option != "option_name"):
                print ("Second Line of an option setting should be 'option_name: '")
                print ("It is:: ",_pre_option)
                sys.exit()

            if(_option not in self.namespace_map[_namespace].keys()):
                print "Line:", self._option_count, "::Invalid Option:: ", _option, "for Namespace:: ", _namespace
                sys.exit()

            else:
                return self.namespace_map[_namespace][_option]

        except :
            print "Invalid Option Syntax \n", self.print_usage()
            sys.exit()

    def validate_namespace(self,_namespace_string):
        try:
            self._option_count  = self._option_count + 1
            _split_string  = _namespace_string.strip().split(':' , 1)
            _namespace     = _split_string[1].strip()
            _pre_namespace = _split_string[0].strip()

            if(_pre_namespace != "- namespace"):
                print ("First Line of an option setting should be '- namespace'")
                print ("It is:: ",_pre_namespace)
                sys.exit()

            elif(_namespace not in self.namespace_map.keys()):
                print "Line:", self._option_count, "::Invalid Namespace:: ", _namespace
                sys.exit()

            else:
                #print self.namespace_map[_namespace]
                return _namespace
        except:
            print "Invalid Namespace Syntax \n", self.print_usage()
            sys.exit()

    def yaml_lint(self):
        if(self.install_yamllint() == 1):
            try:
                subprocess.check_output(["yamllint", self._ebx_file],stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError, e:
                print e.output
                sys.exit()

    def print_usage(self):
        return ("Format of the config file should be: \n" + " option_settings:\n" + "  - namespace:\n" + "    option_name:\n" + "    value:\n" + "Or the shorthand version. http://docs.aws.amazon.com/elasticbeanstalk/latest/dg/ebextensions-optionsettings.html")

    def header_check(self, _header):
        self.whitespace_check(_header)
        if(_header.strip() != "option_settings:"):
            print "First Line should be 'option_settings:'"
            print "It is:: ",_header.strip()
            sys.exit()

    def whitespace_check(self, _string):
        for i in self.whitespaces:
                if i in _string:
                    print "Please remove any trailing spaces or tabs"
                    sys.exit()

    def is_string(self, _string):
        if(_string.strip() != "string"):
            return 1
        else:
            return 0

    def create_map(self):
        try:
            with open(self._config_dir + "/" + self._namespace_file) as f:
                for _namespace_line in f:
                    options = {}
                    try:
                        with open(self._config_dir + "/" + (_namespace_line.replace(":", "_").replace('\n',''))) as _option_file:
                            #print("File:: ",_namespace_line.replace(":", "_").replace('\n',''))
                            for _option_line in _option_file:
                                try:
                                    _option_name,_option_value  = _option_line.strip().split("|")
                                except:
                                    print("Invalid option file:: ",namespace_line.replace(":", "_").replace('\n',''))
                                options[_option_name.strip()]       = _option_value.strip()
                                self.namespace_map[_namespace_line.strip()] = options
                    except:
                        print("Unable to find file:: ",_namespace_line.replace(":", "_").replace('\n',''))

        except:
            print("Unable to find file:: ",self._namespace_file)
        #print self.namespace_map


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("ebextension_file", help="Enter the path of the ebextension config file")
    args = parser.parse_args()
    parserObject = ebXparser(args.ebextension_file)
    parserObject.check_file()
    parserObject.create_map()
    parserObject.validate_ebextensions()
