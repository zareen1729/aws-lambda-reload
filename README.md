# AWS Lambda Reload

A lightweight CLI tool to rapidly update AWS Lambda functions and stream CloudWatch logs to your terminal. Fast iterate → test loop for serverless development.

## Features
- Instant code updates via AWS SDK (update-function-code)
- Live log streaming from CloudWatch
- Auto file watching and redeploy on change
- Multi-function support via config.yaml

## Quickstart
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python watcher.py
```

Edit `config.yaml` and start coding — any change redeploys automatically!
