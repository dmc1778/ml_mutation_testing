import shutil
import threading
from util.DBadaptor import DBHandler
from util.fileUtil import copy_files, read_code_file, read_csv, read_txt, write_to_disc, write_list_to_txt
from subprocess import call, check_call, run
import subprocess, multiprocessing
import re, os
from threading import Thread
import time
from multiprocessing import Pool
all_run = []

valid_tests = 'tensorflow_kernel_test_all_run'

def process(input_addr):
    i =+ 1
    print('Total number of executed unit tests: {}'.format(i))
    print("executed {}. thread".format(input_addr))
    try:
        command = 'python3 '+input_addr
        result = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        msg, err = result.communicate()
        if msg.decode('utf-8') != '':
            stat = parse_shell(msg.decode('utf-8'))
            if stat:
                print('Test Failed')
            else:
                # all_run.append(input_addr)
                write_list_to_txt(input_addr, valid_tests)
        else:
            stat = parse_shell(err)                
            if stat:
                print('Test Failed')
            else:
                # all_run.append(input_addr)
                write_list_to_txt(input_addr, valid_tests)
    except Exception as e:
        print("thread.\nMessage:{1}".format(e))
    

class KillableThread(Thread):
    def __init__(self, sleep_interval, input_addr):
        super().__init__()
        self._kill = threading.Event()
        self._interval = sleep_interval
        self.input_addr = input_addr

    def run(self):
        while True:
            process(self.input_addr)

            # If no kill signal is set, sleep for the interval,
            # If kill signal comes in while sleeping, immediately
            #  wake up and handle
            is_killed = self._kill.wait(self._interval)
            if is_killed:
                break

        print("Killing Thread")

    def kill(self):
        self._kill.set()

def getListOfFiles2(dirName):
    # create a list of file and sub directories 
    # names in the given directory 
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory 
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles2(fullPath)
        else:
            allFiles.append(fullPath)
    return allFiles

def getListOfFiles(dirName):
    # create a list of file and sub directories 
    # names in the given directory 
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory 
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
        else:
            allFiles.append(fullPath)
    # if lang == 'C':
    #     allFiles = filter(allFiles)
    # else:
    allFiles = filter(allFiles)
    return allFiles

def filter(target_files):
    filtered = []
    for f in target_files:
        if 'test' not in f:
            if f.endswith('.c') or f.endswith('.cc') or f.endswith('.cpp'):
                filtered.append(f)
    return filtered

def filter_test_files(test_files, target):
    file_name = os.path.basename(target)
    # parent_dir = os.path.dirname(target)
    # parent_dir = parent_dir.split('/')[-1]
    x = file_name.split('.')
    f = x[0]+'_'+'test'
    f = f +'.'+'py'
    root_test_path = '/media/nimashiri/SSD/tensorflow/tensorflow/python/kernel_tests'
    for root, dir, files in os.walk(root_test_path):
        matches = [match for match in files if f in match]
        if matches:
            return root+'/'+matches[0]
    
    for t in test_files:
        s = t.split('/')
    pass

db_obj = DBHandler()

def search_for_file(filename):
    src = ''
    all_files = getListOfFiles('/media/nimashiri/SSD/tensorflow_core_kernels/kernels')
    for item in all_files:
        if os.path.basename(item) == filename:
            return item
            
def parse_shell(data):
    encoding = 'utf-8'
    if not isinstance(data, str):
        output = data.decode(encoding)
        output = output.split('\n')
    else:
        output = data.split('\n')
    for line in output:
        if re.findall(r'(core dumped)', line) or re.findall(r'(FAILED|ERROR)', line):
            return True
    return False

class MutatePOSTGRE:
    def __init__(self, project_name, test_files):
        self.killed = 0
        self.alive = 0
        self.project_name = project_name
        self.test_files = test_files

        self.operators = {'REDAWN': False
                          }

        self.REDAWN_COUNTER_alive = 0
        self.REDAWN_COUNTER_killed = 0

    def reset_flag(self):
        self.operators = {'REDAWN': False}

    def determine_operator(self, opt):
        if 'OP_REQUIRE' in opt:
            self.operators['REDAWN'] = True
        filtered_operators = [k for k, v in self.operators.items() if v]
        return filtered_operators

    def runProcess(self, exe):
        p = subprocess.Popen(exe, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        while(True):
            retcode = p.poll()
            line = p.stdout.readline()
            yield line
            if retcode is not None:
                break



    def pre_run_test_files(self):
        # run('./scripts/compiletf.sh', shell=True)
        # run('./scripts/build_pip.sh', shell=True)
        # run('./scripts/pip_install_.sh', shell=True)

        out_file_name = 'tensorflow_kernel_test_all_run'
        with Pool(10) as p:
            p.map(process, self.test_files)
            

    def apply_REDAWN(self, filtered_operators, original_data_dict, item, operator):
            temp_data_dict = original_data_dict.copy()

            for l in range(item[1], item[2]+1):
                del temp_data_dict[l]
    
            write_to_disc(temp_data_dict, item[7])

            src = search_for_file(os.path.basename(item[7]))

            # run('./scripts/compiletf.sh', shell=True)
            # run('./scripts/build_pip.sh', shell=True)
            # run('./scripts/pip_install_.sh', shell=True)

            target_test = filter_test_files(self.test_files, item[7])

            if target_test:
            #     call(['python3 '+test_file], shell=True)
                if os.path.exists(target_test):
                    command = 'python3 '+target_test
                    kill_flag = False
                    result = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                    msg, err = result.communicate()
                    if msg.decode('utf-8') != '':
                        stat = parse_shell(msg.decode('utf-8'))
                    else:
                        stat = parse_shell(err)                
                        if stat:
                            print('Mutant Killed!')
                            kill_flag = True

                    # print("Mutation of ========> {original} =====to====> {mutated}".format(original=item[2], mutated=temp_mutant))
                
                    if kill_flag:
                        self.REDAWN_COUNTER_killed += 1
                        db_obj.updateMstatus(item[0], 'killed')
                    else:
                        self.REDAWN_COUNTER_alive += 1
                        db_obj.update(item[0], 1)
                        db_obj.updateMstatus(item[0], 'alive')
                    # write_to_disc(original_data_dict, item[7])
                    target = os.path.dirname(os.path.abspath(item[7]))
                    os.remove(item[7])
                    cmd = 'cp ' + src + ' ' + target
                    status = subprocess.call(cmd, shell=True) 
                

    def apply_mutate(self, filtered_operators, temp_data_dict, item, operator):
        for mkind in filtered_operators:
            if mkind == 'REDAWN' and operator == 'REDAWN':
                self.apply_REDAWN(filtered_operators,
                                  temp_data_dict, item, operator)

def main():

    project_name = 'tensorflow_kernel_test'

    # pre run test files to excluding failed ones
    if not os.path.isfile('tensorflow_kernel_test_all_run_files.txt'):
        _files = read_txt(project_name)

        mpost = MutatePOSTGRE(project_name, _files)

        mpost.pre_run_test_files()


    _files = read_txt(valid_tests)

    mpost = MutatePOSTGRE(project_name, _files)

    db_obj = DBHandler()

    ds_list = db_obj.filter_table()
    db_obj.delete_null()

    for item in ds_list:
        item = list(item)
        data_dict = read_code_file(item[7])
        print('File found for mutation. Please wait until the process finishs')
        filtered_operators = mpost.determine_operator(item[6])
        mpost.apply_mutate(filtered_operators, data_dict, item, 'REDAWN')
        mpost.reset_flag()


if __name__ == '__main__':
    main()