#!/usr/bin/env python3
import time, boto3

def _get_latest_log_stream(client, log_group):
    resp = client.describe_log_streams(logGroupName=log_group, orderBy='LastEventTime', descending=True, limit=1)
    streams = resp.get('logStreams', [])
    return streams[0]['logStreamName'] if streams else None

def stream_logs_for_function(fn_cfg, follow=True):
    name = fn_cfg['name']
    region = fn_cfg.get('region', 'us-west-2')
    client = boto3.client('logs', region_name=region)
    log_group = f"/aws/lambda/{name}"
    print(f"[logs] Checking log group {log_group}...")
    stream = _get_latest_log_stream(client, log_group)
    if not stream:
        print('[logs] No logs yet.')
        return
    print(f"[logs] Streaming logs for {name}...")
    while follow:
        try:
            events = client.get_log_events(logGroupName=log_group, logStreamName=stream, startFromHead=False)
            for ev in events.get('events', []):
                print(ev.get('message', ''), end='')
            time.sleep(2)
        except KeyboardInterrupt:
            break
