###
### VocolaUtils.py - Code used by Vocola's generated Python code
###
### This file is copyright (c) 2002-2010 by Rick Mohr.  It may be redistributed 
### in any way as long as this copyright notice remains.
###

import natlink
from   types import *
import string
import re
import sys


#
# Massage recognition results to make a single entry for each
# <dgndictation> result.
#
def combineDictationWords(fullResults):
    i = 0
    inDictation = 0
    while i < len(fullResults):
        if fullResults[i][1] == "dgndictation":
            # This word came from a "recognize anything" rule.
            # Convert to written form if necessary, e.g. "@\at-sign" --> "@"
            word = fullResults[i][0]
            backslashPosition = string.find(word, "\\")
            if backslashPosition > 0:
                word = word[:backslashPosition]
            if inDictation:
                fullResults[i-1] = [fullResults[i-1][0] + " " + word,
                                    "dgndictation"]
                del fullResults[i]
            else:
                fullResults[i] = [word, "dgndictation"]
                i = i + 1
            inDictation = 1
        else:
            i = i + 1
            inDictation = 0
    return fullResults



##
## Runtime error handling:
## 

class VocolaRuntimeError(Exception):
    pass

def to_long(string):
    try:
        return long(string)
    except ValueError:
        raise VocolaRuntimeError("unable to convert '"
                                 + string.replace("'", "''")
                                 + "' into an integer")


import traceback

def handle_error(command, exception):
    print 
    print >> sys.stderr, "While executing the following Vocola command:"
    print >> sys.stderr, "    " + command
    print >> sys.stderr, "the following error occurred:"
    print >> sys.stderr, "    " + type(exception).__name__ + ": " + str(exception)
    #traceback.print_exc()
    #raise exception



##
## Dragon built-ins: 
##
 
def call_Dragon(function_name, argument_types, arguments):
    def quoteAsVisualBasicString(argument):
        q = argument
        q = string.replace(q, '"', '""')
        q = string.replace(q, "\n", '" + chr$(10) + "')
        q = string.replace(q, "\r", '" + chr$(13) + "')
        return '"' + q + '"'

    script = ""
    for argument in arguments:
        argument_type = argument_types[0]
        argument_types = argument_types[1:]

        if argument_type == 'i':
            argument = str(to_long(argument))
        elif argument_type == 's':
            argument = quoteAsVisualBasicString(str(argument))
        else:
            # there is a vcl2py.pl bug if this happens:
            raise VocolaRuntimeError("Vocola compiler error: unknown data type " +
                                     " specifier '" + argument_type +
                                   "' supplied for a Dragon procedure argument")

        if script != '':
            script += ','
        script += ' ' + argument

    script = function_name + script
    #print '[' + script + ']'
    try:
        if function_name == "SendDragonKeys":
            natlink.playString(arguments[0])
        else:
            natlink.execScript(script)
    except Exception, e:
        m = "when Vocola called Dragon to execute:\n" \
            + '        ' + script + '\n' \
            + '    Dragon reported the following error:\n' \
            + '        ' + type(e).__name__ + ": " + str(e)
        raise VocolaRuntimeError, m



##
## Unimacro built-in:
##

# attempt to import Unimacro, suppressing errors, and noting success status:
unimacro_available = False
try:
    import actions
    unimacro_available = True
except ImportError:
    pass

def call_Unimacro(argumentString):
    if unimacro_available:
        #print '[' + argumentString + ']'
        try:
            actions.doAction(self.argumentString)
        except Exception, e:
            m = "when Vocola called Unimacro to execute:\n" \
                + '        ' + script + '\n' \
                + '    Unimacro reported the following error:\n' \
                + '        ' + type(e).__name__ + ": " + str(e)
        raise VocolaRuntimeError, m
    else:
        m = "Unimacro call failed because Unimacro is unavailable"
        raise VocolaRuntimeError(m)



##
## EvalTemplate built-in function:
##

def eval_template(template, *arguments):
    variables = {}
    
    waiting = list(arguments)
    def get_argument():
        if len(waiting) == 0:
            raise VocolaRuntimeError(
                "insufficient number of arguments passed to Eval[Template]")
        return waiting.pop(0)
            
    def get_variable(value):
        argument_number = len(arguments)-len(waiting)
        name = "v" + str(argument_number)
        variables[name] = value
        return name
    
    # is string the canonical representation of a long?
    def isCanonicalNumber(string):
        try:
            return str(long(string)) == string
        except ValueError:
            return 0
    
    def handle_descriptor(m):
        descriptor = m.group()
        if descriptor == "%%":
            return "%"
        elif descriptor == "%s":
            return get_variable(str(get_argument()))
        elif descriptor == "%i":
            return get_variable(to_long(get_argument()))
        elif descriptor == "%a":
            a = get_argument()
            if isCanonicalNumber(a):
                return get_variable(long(a))
            else:
                return get_variable(str(a))
        else:
            return descriptor
    
    expression = re.sub(r'%.', handle_descriptor, template)
    try:
        return eval('str(' + expression + ')', variables.copy())
    except Exception, e:
        m = "when Eval[Template] called Python to evaluate:\n" \
            + '        str(' + expression + ')\n' \
            + '    under the following bindings:\n'
        for v in variables:
            m += '        ' + str(v) + ' -> ' + repr(variables[v]) + '\n'
        m += '    Python reported the following error:\n' \
            + '        ' + type(e).__name__ + ": " + str(e)
        raise VocolaRuntimeError, m
