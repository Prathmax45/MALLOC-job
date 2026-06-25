import requests
import json

try:
    resp = requests.post("http://127.0.0.1:8000/api/target-stats", json={
        "resumeText": "C++ and CUDA",
        "targetRole": "gpu_software",
        "targetCompany": "nvidia"
    })
    print(resp.status_code)
    print(resp.json())
except Exception as e:
    print(e)
