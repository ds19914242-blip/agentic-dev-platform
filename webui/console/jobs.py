"""console.jobs — background job machinery for the Agentic Console.

Extracted verbatim from server.py (Phase 2a). Owns the in-memory job registry
(JOBS), the in-flight dedup map (INFLIGHT), the Job class, start_job (runs a
target in a daemon thread with a heartbeat and dedup), and _forward (adapts a
synchronous action's returned log into job emits).

server.py re-binds these names to the SAME objects, so every existing call site
(start_job / _forward / JOBS / INFLIGHT) keeps working unchanged. The SSE stream
endpoint stays in server.py because it is bound to the HTTP handler, but it reads
this module's JOBS via the re-export.

Behaviour is byte-for-byte identical to the originals.
"""
import threading
import time
import uuid
from datetime import datetime

# --- registry ---------------------------------------------------------------
JOBS = {}
INFLIGHT = {}
JOBS_LOCK = threading.Lock()


class Job:
    def __init__(self, kind, key):
        self.id = uuid.uuid4().hex[:12]
        self.kind = kind
        self.key = key
        self.log = []
        self.done = False
        self.result = None
        self._lock = threading.Lock()

    def emit(self, msg, level=""):
        with self._lock:
            self.log.append({"ts": datetime.now().strftime("%H:%M:%S"), "msg": msg, "level": level})

    def snapshot(self, frm):
        with self._lock:
            return self.log[frm:], self.done, self.result


def start_job(kind, key, target):
    """Start target(job) in a thread. Returns (job, started_new)."""
    with JOBS_LOCK:
        existing = INFLIGHT.get(key)
        if existing and existing in JOBS and not JOBS[existing].done:
            return JOBS[existing], False
        job = Job(kind, key)
        JOBS[job.id] = job
        INFLIGHT[key] = job.id

    def run():
        stop = threading.Event()

        def heartbeat():
            t0 = time.time()
            while not stop.wait(3):
                job.emit(f"…still working ({int(time.time() - t0)}s)")

        hb = threading.Thread(target=heartbeat, daemon=True)
        job.emit(f"{kind}: dispatched")
        hb.start()
        try:
            job.result = target(job) or {"ok": True}
        except Exception as exc:
            job.emit(f"error: {exc}", "err")
            job.result = {"ok": False, "error": str(exc)}
        finally:
            stop.set()
            with JOBS_LOCK:
                if INFLIGHT.get(key) == job.id:
                    del INFLIGHT[key]
            job.emit("done", "ok")
            job.done = True

    threading.Thread(target=run, daemon=True).start()
    return job, True


def _forward(fn, *args):
    """Wrap a synchronous webui action so its returned log streams to the job."""
    def target(job):
        r = fn(*args) or {}
        for l in r.get("log", []):
            job.emit(l.get("msg", ""), l.get("level", ""))
        return {k: v for k, v in r.items() if k != "log"}
    return target
