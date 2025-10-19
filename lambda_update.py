#!/usr/bin/env python3
import os, time, zipfile, boto3, tempfile
from pathlib import Path

def zip_directory(folder_path, zip_path):
    folder_path = Path(folder_path)
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, start=folder_path)
                z.write(file_path, arcname)

def update_lambda_for_function(fn_cfg):
    name = fn_cfg['name']
    region = fn_cfg.get('region', 'us-west-2')
    path = fn_cfg['path']
    tmp_dir = fn_cfg.get('zip_tmp_path', tempfile.gettempdir())
    os.makedirs(tmp_dir, exist_ok=True)
    zip_name = os.path.join(tmp_dir, f"lambda_update_{name}_{int(time.time())}.zip")
    print(f"[update] Zipping {path} -> {zip_name}")
    zip_directory(path, zip_name)
    print(f"[update] Uploading to Lambda ({name}) in {region}...")
    client = boto3.client('lambda', region_name=region)
    with open(zip_name, 'rb') as f:
        bytez = f.read()
        client.update_function_code(FunctionName=name, ZipFile=bytez)
    print(f"[update] Update complete for {name}")
    os.remove(zip_name)
