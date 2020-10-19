#!/usr/bin/env python
import os
from time import sleep
import glob
import argparse
import subprocess
import requests
import sys

# Enter your API key and Rescale CLI Install path Below

RESCALE_API_KEY = 'fc5b688553ce8badb628f8c1dca209d8781e837c'
RESCALE_CLI_PATH = '/usr/local/bin/rescale-cli'

#Enter Coretype
coretype_code = 'ferrite'
cores = 32
project= 'ZMewo'
# job command
COMMAND = 'ls-dyna -i *.k -p single'

# command using script
#COMMAND = './run.sh'

# change this if submitting to different platform
PLATFORM_URL = 'https://platform.rescale.com'

input_files = []
envVars = []
coretype_code = 'ferrite'
cores = 32
name = 'Test Job'
project= 'ZMewo'



# These should for the most part remain constant, so kept in this script
CLUSTERS_ENDPOINT = PLATFORM_URL + '/api/v2/clusters/'
CORETYPES_ENDPOINT = PLATFORM_URL + '/api/v2/coretypes/'
FILES_ENDPOINT = PLATFORM_URL + '/api/v2/files/contents/'
JOBS_ENDPOINT = PLATFORM_URL + '/api/v2/jobs/'
HEADERS = {
    'Authorization': 'Token {0}'.format(RESCALE_API_KEY)
}


def upload_files(files):
    fids = []
    if files == '*':
        files = glob.glob("*")
        files = filter(lambda x: not x.startswith("analysis_params"), files)
    for f in files:
        print 'Uploading: {}'.format(f)
        try:
            res = requests.post(
                FILES_ENDPOINT,
                headers=HEADERS,
                files={'file': open(f, 'rb')}
            ).json()
            fids.append(res['id'])
        except:
            print '   ERROR uploading: {}'.format(f)
    return fids
    print fids.content


def upload_input_files(files):
    file_ids = upload_files(files)
    input_files = []
    for fid in file_ids:
        input_files.append({'id': fid})
    if len(file_ids):
        return input_files
    return {}


def upload_single_file(filename):
    if len(filename) > 0:
        file_id = upload_files([filename])
        return {'id': file_id[0]}
    return {}


def create_job(files,
               cores,
               name=None):
#    print 'Creating {total}-core {analysis} job with {slots} slots'.format(
    #analysis=analysisname
   # data = get_analysis_code(analysisname)
#    analysis_data = data['analysis']

    # upload files and get id structs
    input_files = upload_input_files(files)

    # create job with all the "base" fields
    payload = {  
    'isLowPriority': False,
    'jobanalyses': [
    {
      'envVars': {
        'LSTC_LICENSE_SERVER': '31011@lsdyna'
      },
      'analysis': {
        'code': 'ls_dyna',
        'version': '9.1.0'
      },
      'hardware': {
        'coresPerSlot': 36,
        'coreType': 'ferrite',
        'walltime': 48
      },
      'command': './runs.sh',
      'inputFiles': input_files
    },
    {
      'envVars': {
        'LM_LICENSE_FILE': '26000@lear'
      },
      'analysis': {
        'code': 'femzip',
        'version': 'l-10.68'
      },
      'hardware': {
        'coresPerSlot': 36,
        'coreType': 'ferrite',
        'walltime': 48
      },
      'inputFiles': input_files
    }
  ],
  'projectId': 'ZMewo',
  'name': 'Job',
},

    response = requests.post(
        JOBS_ENDPOINT,
        headers=HEADERS,
        json={  
    'isLowPriority': False,
    'jobanalyses': [
    {
      'envVars': {
        'LSTC_LICENSE_SERVER': '31011@lsdyna'
      },
      'analysis': {
        'code': 'ls_dyna',
        'version': '9.1.0'
      },
      'hardware': {
        'coresPerSlot': 36,
        'coreType': 'ferrite',
        'walltime': 48
      },
      'command': './runs.sh',
      'inputFiles': input_files
    },
    {
      'envVars': {
        'LM_LICENSE_FILE': '26000@lear'
      },
      'analysis': {
        'code': 'femzip',
        'version': 'l-10.68'
      },
      'hardware': {
        'coresPerSlot': 36,
        'coreType': 'ferrite',
        'walltime': 48
      },
      'command': './runs.sh',
      'inputFiles': input_files
    }
  ],
  'projectId': 'ZMewo',
  'name': 'Job',
},
).json()

    try:
        val = response['id']
        return val
    except KeyError:
        print 'Error occured while creating job'
        print response
        return None


def start_job(job_id):
    start_url = JOBS_ENDPOINT + job_id + '/submit/'
    r = requests.post(
        start_url,
        headers=HEADERS
    )


def watch_job(job_id):
    status_url = JOBS_ENDPOINT + job_id + '/statuses/'
    not_finished = True
    interval = 120
    while not_finished:
        try:
            res = requests.get(
                status_url,
                headers=HEADERS
            )
            statuses = [
                s['status'] for s in res.json()['results']
            ]
            print 'Current Status for job {}: {}'.format(job_id, statuses[0])
            is_completed = any(s == 'Completed' for s in statuses)
            if not is_completed:
                print 'Not finished yet, re-checking in {} seconds'.format(interval)
                sleep(interval)
            else:
                not_finished = False
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            not_finished = False
            pass

def cli_download(job_id):
    # NOTE: if the job has already be snyc'd once running the sync
    #       command again will not result the rest of the
    #       files being downloaded, therefore this should only
    #       be called when the job is complete
    print 'Attempting to download results with CLI for job {}'.format(job_id)
    cmd = ' '.join([RESCALE_CLI_PATH,
                    'sync -p',
                    RESCALE_API_KEY,
                    '-j',
                    job_id])

    subprocess.call(cmd, shell=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--cores',
                        '-nc',
                        help='Number of cores per slot (Default is 1)',
                        type=int,
                        default=1)

    parser.add_argument('--files',
                        '-f',
                        help='Input file(s). The default is to upload all files' +
                             ' in the current working directory',
                        type=str,
                        nargs='+',
                        default='*')
                        
    parser.add_argument('--submit',
                        '-submit',
                        help='When set to "True" job will be submitted,' +
                             ' default it to only create job (Default is False)',
                        type=bool,
                        default=True)
    parser.add_argument('--download',
                        '-dl',
                        help='When set to "True" results will be downloaded (Default is False)',
                        type=bool,
                        default=True)
    parser.add_argument('--name',
                        '-N',
                        help='Name of job',
                        type=str,
                        default='Untited Job')
    parser.add_argument('--jobid',
                        '-id',
                        help='When a job ID is provided, a new job is not created.' +
                             ' It can be submitted or downloaded with flags',
                        type=str,
                        default='')
                        
    args = parser.parse_args()
    
#if a job ID is provided, don't create the job
    if args.jobid == '':
        print 'Creating new job'
        job_id = create_job(
            cores=args.cores,
            files=args.files,
            name=args.name
        )
        if job_id is None:
            sys.exit()
    else:
        job_id = args.jobid

    if args.submit:
    	#start_job(job_id)
        start_url = JOBS_ENDPOINT + job_id + '/submit/'
    	r = requests.post(
        start_url,
        headers=HEADERS
    	)
    	print r.content        
    	print 'Submitting job: {}'.format(job_id)
    else:
        if args.jobid == '':
            print 'Job {} has been created, but will not be submitted'.format(job_id)

    if args.download:
        print 'Downloading results when complete for job: {}'.format(job_id)
        watch_job(job_id)
        
cli_download(job_id)
