import os
import re
import json
import codecs
import os
from pathlib import Path
import itertools
import csv
from util.DBadaptor import DBHandler
from subprocess import call
import subprocess, sys
import argparse
import re
# from func_extract_clang import main
# from func_extract_clang import source_to_ast
from util.fileUtil import read_code_file, read_csv, read_txt
from util.extract_AST import build_tree



db_obj = DBHandler()


class CheckPotential:
    def __init__(self) -> None:
        self._method = ""
        self.REDAWN = 0
        self.mutId = 0

    def reset_flag(self):
        self.line_reg = []

    def get(self):
        return self._method

    def set(self, _input):
        self._method = _input

    def get_equal_index(self, components):
        for i, item in enumerate(components):
            if item == 'calloc':
                components[i] = 'malloc'
            if item == ',':
                components[i] = ' *'
        return components

    def REC2M(self):
        # parser = c_parser.CParser()
        for line in self._method:
            components = re.findall(
                r'([^=]+)((?<!=)=(?!=))(?:^|\W)(calloc)(?:$|\W)(.*)', self._method[line])
            if components:
                components = list(components[0])
                components = self.get_equal_index(components)
                self._method[line] = ''.join(components)
                self.del_flag = True

    def rangeCheck(self, line):
        for l in range(line, len(self._method)):
            #print(self._method[l])
            if re.findall(r'[;]', self._method[l]):
                return l


    def func_UMA(self, current_file):
        for line in self._method:
            if self._method[line] != '':
                self.mutId += 1
                check1 = re.findall(r'\bOP_REQUIRES_OK\b\s*\(([^\)]+)\)', self._method[line])
                check2 = re.findall(r'\bOP_REQUIRES\b\s*\(([^\)]+)\)', self._method[line])
                if check1 or check2:
                    stmt = []
                    end_line = self.rangeCheck(line)
                    for sub_line in range(line, end_line+1):
                        stmt.append(self._method[sub_line])
                    stmt = ''.join(stmt)
                    db_obj.insert_data(self.mutId,line, end_line, stmt, '', os.path.basename(current_file), "OP_REQUIRE", current_file, '')

    def apply(self, current_file, edges, nodes):
        self.func_UMA(current_file)

visited = set()        

def regex_parser(str):
    return re.findall(r'\bOP_REQUIRE\b\s*\(([^\)]+)\)', str)

def parse_ast(tree):
    print(tree['code'])
    if tree == None:
        return 1
    # if regex_parser(tree['code']):
    #     print(tree['code'])
    if not tree['has_child']:
        return 1
    if tree['id'] not in visited:
        visited.add(tree['id'])
    for neighbors in tree['children']:
        parse_ast(neighbors)

def parse_addr(f):
    for com in f.split('/'):
        if com == 'core':
            if com == 'kernels':
                return True
            else:
                return False

def main():
    db_obj.build_database()

    # target_path = args.target_path
    _obj = CheckPotential()

    sut = 'tensorflow'

    _files = read_txt(sut)
    cpg_dest_path = '/media/nimashiri/SSD/'+sut+'_cpg_path'
    for f in _files:
        fname = os.path.basename(f)
        if re.findall(r'(\bcore\/kernels\b)', f):
            print(f)
            cpg_path = os.path.join(cpg_dest_path, fname)

            edges_path = os.path.join(cpg_path, 'edges.csv')
            nodes_path = os.path.join(cpg_path, 'nodes.csv')

            edges = read_csv(edges_path)
            nodes = read_csv(nodes_path)

            # ast = build_tree(edges, nodes)

            #parse_ast(ast[0])

            #call(['./lib/remove.sh', current_file, sub_files])
            # source_to_ast(current_file, 'result.txt')
            data_dict = read_code_file(f)
            _obj.set(data_dict)
            _obj.apply(f, edges, nodes)
            #call("./remove-clang.sh")
            _obj.reset_flag()
    


if __name__ == '__main__':
    main()
    # parser = argparse.ArgumentParser(description='Analyze your project for potential mutations')
    # parser.add_argument('target_path', type=str, help='your target directory')
    # args = parser.parse_args()
    # # args = "/home/nimashiri/postgres-REL_13_1/src/"
    # main(args)