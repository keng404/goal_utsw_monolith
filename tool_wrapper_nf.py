#!/usr/bin/python3
import argparse
import os
import json
import shlex
import subprocess
import glob
import re

def execute_command(cmd):
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return process.communicate()

def log_command(cmd, log_object):
	out,err = execute_command(cmd) 
	log_object.write(out.decode('utf8','ignore'))
	log_object.write(err.decode('utf8','ignore'))

def get_fastqs(doi):
	fastqs = []
	for name in glob.glob(doi + '/*.fastq.gz'):
		fastqs.append(name)
	fastqs.sort()	
	return fastqs

def strip_names(fois):
	if 'R1.fastq' in os.path.basename(fois):
		return re.sub('.R1.fastq.gz$','',os.path.basename(fois))
	else:
		return re.sub('.R2.fastq.gz$','',os.path.basename(fois))

def get_sample_id(foi):
	ids = list(set([ strip_names(f) for f in foi ]))
	return ids[0]

def create_design_table(fastqs,case_identifier,output_path):
	sample_id = get_sample_id(fastqs)
	header = ['SampleID','CaseID','TumorID','FqR1','FqR2']
	data = [sample_id, case_identifier,sample_id, os.path.basename(fastqs[0]), os.path.basename(fastqs[1])]
	f = open(output_path,"w")
	header_str = "\t".join(header)
	f.write(header_str + "\n")
	data_str = "\t".join(data)
	f.write(data_str + "\n")
	f.close()


def run_nf(inputs,reference,viral_reference,bed_regions,capture_directory,PON,markdups_method,version,output_path,design_table):
	work_dir = '/scratch'
	os.makedirs(work_dir, exist_ok=True,mode=0o777)
	full_cmd = ""
	output_design_path = ""
	########### untar ref file	to allow for ICA to run pipeline
	initial_ref_dir = os.path.dirname(reference) + "/" + os.path.basename(reference).split(".")[0]
	untar_ref_file = ['tar','-xvf',reference,'-C',os.path.dirname(reference)]
	untar_ref_file_str = " ".join(untar_ref_file)
	untar_ref_file_cmd= shlex.split(untar_ref_file_str)
	print("Running:\t" + untar_ref_file_str)
	out,err = execute_command(untar_ref_file_cmd)
	reference  = initial_ref_dir
	#######################################################	
		## create design.txt file for tumor-only pipeline
	if design_table is None or os.path.isfile(design_table) is False:
		output_design_path = capture_directory + "/design.txt"
		fastqs = get_fastqs(inputs)
		create_design_table(fastqs,'Fam1',output_design_path)
	if design_table is None:	
		design_table = output_design_path
	#######################################################
	#'-work-dir',work_dir
#	full_cmd = ['/usr/local/bin/nextflow' ,'run' ,'/usr/local/bin/goalConsensus.nf','--input',inputs,'-work-dir',work_dir,'--genome',reference,'--virus_genome',viral_reference,'--capture',bed_regions,'--capturedir',capture_directory,'--pon',PON,'--markdups',markdups_method,'--version',version,'--output',output_path,'-with-dag','pipeline.png','--caseid','Fam1']
	full_cmd = ['/usr/local/bin/nextflow' ,'run' ,'/usr/local/bin/goalConsensus.nf','--input',inputs,'--genome',reference,'--virus_genome',viral_reference,'--capture',bed_regions,'--capturedir',capture_directory,'--pon',PON,'--markdups',markdups_method,'--version',version,'--output',output_path,'-with-dag','pipeline.png','--design',design_table]
			
	full_cmd_str = " ".join(full_cmd)
	full_cmd = shlex.split(full_cmd_str)
	print(full_cmd)
	print("Running:\t" + full_cmd_str)
	out,err = execute_command(full_cmd)
	run_log = open("run.log","w",encoding='utf-8', errors='ignore')
	run_log.writelines("%s\n" % full_cmd_str)
	run_log.write(err.decode("utf8",'ignore'))
	run_log.write(out.decode("utf8",'ignore'))
	####### Clean up cache and working directories
	cleanup_cmd_str = '/usr/local/bin/nextflow clean -f'
	cleanup_cmd = shlex.split(cleanup_cmd_str)
	print("Running:\t" + cleanup_cmd_str)
	log_command(cleanup_cmd,run_log)
	if 'work-dir'  in full_cmd:
		## explicity remove cache and working directories
		cleanup_cmd1 = shlex.split('rm -rf '  + work_dir)
		print("Running:\t" + ' '.join(cleanup_cmd1))
		log_command(cleanup_cmd1,run_log)
	## explicity remove cache and working directories
	cleanup_cmd3 = shlex.split('rm -rf ' + work_dir + "/" + '.nextflow')
	print("Running:\t" + ' '.join(cleanup_cmd3))
	log_command(cleanup_cmd3,run_log)
	cleanup_cmd3 = shlex.split('rm -rf ' + '.nextflow')
	print("Running:\t" + ' '.join(cleanup_cmd3))
	log_command(cleanup_cmd3,run_log)
	run_log.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--fastq_files',nargs = '*', default = [],type = str, help="FASTQ files to run through pipelines")
    parser.add_argument('--ref',type = str,help="reference genome")
    parser.add_argument('--virus_ref',type = str, help="virus reference")
    parser.add_argument('--bed',type = str, help="BED file of  regions of interest")
    parser.add_argument('--capture_dir',type = str, help="directory that contains reference files related to a capture kit")
    parser.add_argument('--pon',type = str, help="pon reference")
    parser.add_argument('--markdups',default = 'picard',type = str, help="default method for marking duplicates")
    parser.add_argument('--version',default = 'v4', type = str, help="version")
    parser.add_argument('--design', type = str, help="design_file")
    parser.add_argument('--output_directory',default='./analysis',type = str, help = "output directory that will contain results")
    args, extras = parser.parse_known_args()
    input_dir = list(set([os.path.dirname(x) for x in args.fastq_files]))[0]
    print(str([input_dir,args.ref,args.virus_ref,args.bed,os.path.dirname(args.bed),args.pon,args.markdups,args.version,args.output_directory,args.design]))
    run_nf(input_dir,args.ref,args.virus_ref,args.bed,os.path.dirname(args.bed),args.pon,args.markdups,args.version,args.output_directory,args.design)


if __name__ == '__main__':
    main()