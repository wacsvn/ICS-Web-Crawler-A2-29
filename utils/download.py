import requests
import cbor
import time

from utils.response import Response

def download(url, config, logger=None):
    host, port = config.cache_server
    try:
        resp = requests.get(
            f"http://{host}:{port}/",
            params=[("q", f"{url}"), ("u", f"{config.user_agent}")])

        try:
            if resp and resp.content:
                return Response(cbor.loads(resp.content))
        except (EOFError, ValueError) as e:
            pass

    except Exception as e:
        print("ERROR WHILE DOWNLOADING ***********__________***********************")
        print(url)
        print(e)

    logger.error(f"Spacetime Response error {resp} with url {url}.")
    return Response({
        "error": f"Spacetime Response error {resp} with url {url}.",
        "status": resp.status_code,
        "url": url})