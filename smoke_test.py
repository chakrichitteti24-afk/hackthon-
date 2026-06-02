import urllib.request, urllib.error, json, sys, time

base = 'http://127.0.0.1:8001'

def safe_print(*args):
    text = ' '.join(str(a) for a in args)
    enc = sys.stdout.encoding or 'utf-8'
    try:
        print(text.encode(enc, errors='replace').decode(enc))
    except Exception:
        print(text.encode('ascii', errors='replace').decode('ascii'))


def get(path):
    url = base + path
    req = urllib.request.Request(url, method='GET')
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            body = r.read().decode('utf-8')
            safe_print('GET', path, r.status)
            safe_print(body[:2000])
            return True
    except Exception as e:
        safe_print('GET_ERR', path, repr(e))
        return False


def post(path, data):
    url = base + path
    b = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(url, data=b, headers={'Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            body = r.read().decode('utf-8')
            safe_print('POST', path, r.status)
            safe_print(body[:4000])
            return True
    except Exception as e:
        safe_print('POST_ERR', path, repr(e))
        return False


def wait_for_service(timeout=15, interval=0.6):
    start = time.time()
    while time.time() - start < timeout:
        try:
            req = urllib.request.Request(base + '/health', method='GET')
            with urllib.request.urlopen(req, timeout=3) as r:
                print('SERVICE_UP', r.status)
                return True
        except Exception:
            time.sleep(interval)
    print('SERVICE_DOWN')
    return False


if __name__ == "__main__":
    ok = wait_for_service()
    get('/analytics')
    payload = {"user_id":"smoke_user","message":"I need help with billing and price increases and my subscription","agent_type":None}
    post('/chat', payload)
    # small sleep to let session update
    time.sleep(0.6)
    get('/session/smoke_user')
    sys.exit(0 if ok else 2)
