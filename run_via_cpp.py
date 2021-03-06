# -*- coding: utf-8 -*-
"""
@author: James C Pino

"""
import numpy as np
import re
import os
import subprocess
import jinja2


env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(
        searchpath=os.path.join(os.path.dirname(__file__), 'templates')
    )
)

template = env.get_template('cuda_attempt.cpp')

n_states = 3


def compile_cython_code(model_file):
    with open(model_file, 'r') as f:
        functions = map(lambda s: s.strip(), f)
    num_nodes = len(functions)

    function_output = ''

    for line in functions:
        # Replace function name
        index = 'vect[%d]' % (int(re.match('f(\d+)', line).group(1)) - 1)
        line = re.sub('f\d+', index, line)

        # Convert powers (^) to simple multiplications
        matches = re.findall('(x\d+)\^(\d+)', line)
        for m in matches:
            repl = m[0]
            for i in range(1, int(m[1])):
                repl += "*%s" % m[0]
            line = re.sub('x\d+\^\d+', repl, line, count=1)

        # Replace node names
        matches = np.array(re.findall('x(\d+)', line), dtype=int)
        for m in matches:
            line = re.sub('x\d+', 'x[%d]' % (m - 1), line, count=1)
        function_output += '    %s;\n' % line

    with open('test.cpp', 'w') as pyxfile:
        pyxfile.write(template.render(
            {
                'functions': function_output,
                'num_states': n_states,
                'n_nodes': num_nodes,
             },
        ))


# Model = 'Models/func_example.txt'
# Model = 'Models/core_iron_6variables_3states.txt'
Model = 'Models/final_continuous_model_21_nodes.txt'

print("Created c++ code")
compile_cython_code(Model)
args = ['c++',
        '-O3',
        '-std=c++11',
        'test.cpp',
        # '-pg',
        # '-g',
        # '-ggdb',
        '-o', 'run_boolean.exe']

print("Compiling")
subprocess.call(args)
print("Compiled")

print("Running")
subprocess.call(['./run_boolean.exe'])

