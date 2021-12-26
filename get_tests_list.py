
import os
from util.fileUtil import getListOfFiles, write_list_to_txt, read_txt

def main():
        # the path of project under test. If you want to analyze a different project for potential mutations
    # provide a different address

    # the name of the project
    sut = 'tensorflow'

    target_path = '/media/nimashiri/SSD/'+sut+'/tensorflow/python/kernel_tests'

    out_file_name = 'tensorflow_kernel_test'

    # we need list of all files from project under test to check for potential mutatioons
    # please note that we only extract C and CC files since this tool solely designed to 
    # analyze programs or projects written in C or CC. 
    if not os.path.isfile('./'+out_file_name+'_files.txt'):
        # get list of all files
        _files = getListOfFiles(target_path)
        # output the list to disk
        write_list_to_txt(_files, out_file_name)
        
    
    # read list of all files from disk
    _files = read_txt(sut)

if __name__ == '__main__':
    main()