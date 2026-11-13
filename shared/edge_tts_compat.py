"""Process-local Edge TTS endpoint workaround; no site-packages modifications."""
import asyncio
import importlib
import time

REQUEST_INTERVAL = 30
_last_finished = None


def configure_endpoint():
    constants = importlib.import_module('edge_tts.constants')
    communicate = importlib.import_module('edge_tts.communicate')
    communicate.WSS_URL = (
        'wss://api.msedgeservices.com/tts/cognitiveservices/websocket/v1'
        f'?Ocp-Apim-Subscription-Key={constants.TRUSTED_CLIENT_TOKEN}'
    )


async def stream_to_file(text, voice, partial):
    """Caller invokes serially; preserve status on non-429 errors."""
    global _last_finished
    import edge_tts
    configure_endpoint()
    for attempt in range(3):
        if _last_finished is not None:
            await asyncio.sleep(max(0, REQUEST_INTERVAL-(time.monotonic()-_last_finished)))
        boundaries = []
        try:
            async def receive():
                with partial.open('wb') as handle:
                    async for item in edge_tts.Communicate(
                        text, voice['name'], rate=voice['rate'], pitch=voice['pitch'],
                        boundary='WordBoundary'
                    ).stream():
                        if item['type']=='audio':handle.write(item['data'])
                        elif item['type']=='WordBoundary':boundaries.append(item)
            await asyncio.wait_for(receive(), timeout=45)
            _last_finished=time.monotonic()
            return boundaries
        except BaseException as exc:
            _last_finished=time.monotonic()
            partial.unlink(missing_ok=True)
            if not isinstance(exc, Exception) or getattr(exc, 'status', None)!=429 or attempt==2:
                raise
            headers = getattr(exc, 'headers', None) or {}
            retry_after = headers.get('Retry-After', '0')
            try:server_wait=max(0, float(retry_after))
            except (ValueError,TypeError):
                from email.utils import parsedate_to_datetime
                try:server_wait=max(0, parsedate_to_datetime(retry_after).timestamp()-time.time())
                except (ValueError,TypeError,OverflowError):server_wait=0
            wait=max(30*(attempt+1), server_wait)
            print(f'Edge TTS HTTP 429：{wait:g}秒后重试（{attempt+2}/3）',flush=True)
            await asyncio.sleep(wait)
