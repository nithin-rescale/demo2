import requests
import json

api_token='Token 4ddf42e101c862ba14e1cc8939d17f5f16f1cb57'


# upload input files credentials
file_upload1=requests.post(
    'https://platform.rescale.com/api/v2/files/contents/',
    data=None,
    files={'file': open('drc_set_a.rules')},
    headers={'Authorization': api_token}
)
file_content1=json.loads(file_upload1.text)

# obtain file ID after uploading for later use-create jobs
file_ID1=file_content1["id"]


# upload input files aedtz
file_upload2=requests.post(
    'https://platform.rescale.com/api/v2/files/contents/',
    data=None,
    files={'file': open('fullchip.oas', 'rb')},
    headers={'Authorization': api_token}
)
file_content2=json.loads(file_upload2.text)

# obtain file ID after uploading for later use-create jobs
file_ID2=file_content2["id"]


# upload input files submit sh
file_upload3=requests.post(
    'https://platform.rescale.com/api/v2/files/contents/',
    data=None,
    files={'file': open('layer.inc')},
    headers={'Authorization': api_token}
)
file_content3=json.loads(file_upload3.text)

# obtain file ID after uploading for later use-create jobs
file_ID3=file_content3["id"]



payload = {
   "name":"DRC API run",
   "jobanalyses":[
      {
        "envVars": {},

        "analysis": {
          "code": "mentor_calibredrc",
          "name": "Mentor Graphics Calibre DRC",
          "version": "2019.3_37.23",
          "versionName": "2019.3_37.23"
        },
        "command": "rundrc -drc -hier -turbo -hyper drc_set_a.rules | tee drc.log",
         "hardware":{
            "coresPerSlot":4,
            "slots":1,
            "coreType":"emerald",
            "walltime":10
         },
         "inputFiles":[
          {"id":file_ID1},
          {"id":file_ID2},
          {"id":file_ID3}
         ],
         "useRescaleLicense":False,
         "envVars": {
          "LM_LICENSE_FILE": "1717@mentor"
      },     
         "templateTasks":[]             
      }
   ]
}


# job created but not submitted
job_setup=requests.post(
    'https://platform.rescale.com/api/v2/jobs/',
    json=payload,
    headers={'Authorization': api_token}
)

# print job_setup.content
job_content=json.loads(job_setup.text)
job_ID=job_content["id"]
#print job_ID

#submit the job
requests.post(
    'https://platform.rescale.com/api/v2/jobs/%s/submit/'%job_ID,
    headers={'Authorization': api_token}
)