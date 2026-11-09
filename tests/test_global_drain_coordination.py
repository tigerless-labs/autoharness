"""Independent projects must retain both successful edits to a shared skill."""
import threading
from contextlib import contextmanager
from pathlib import Path

from autoharness import config
from autoharness.hook import promoter
from autoharness.lib import intent_queue, lock, sidecar, skill_store

BODY = ("---\nname: shared\ndescription: Use when formatting a date as ISO.\n---\n"
        "# Shared\nFirst setting: alpha.\nSecond setting: beta.\n")


def test_global_patches_from_different_projects_both_survive(tmp_path, monkeypatch):
    global_root = tmp_path / "global"
    roots = [{"global": global_root, "project": tmp_path / name} for name in ("one", "two")]
    skill_store.write_body("global", "shared", BODY, global_root)
    sidecar.create("global", "shared", 0, global_root)
    for index, (old, new) in enumerate((("alpha", "gamma"), ("beta", "delta"))):
        intent_queue.append(f"run{index}", {
            "action": "patch", "name": "shared", "old_string": old, "new_string": new,
            "reason": "independent setting change", "evidence": "local synthetic observation",
        }, roots[index]["project"])
    first_shaped, release = threading.Event(), threading.Event()
    real_shape, real_lock = promoter._shape, lock.file_lock
    results, errors = {}, []

    def shape(*args):
        body = real_shape(*args)
        if threading.current_thread().name == "global-drain-0":
            first_shaped.set()
            assert release.wait(5), "second actor never reached a safe scheduling point"
        else:
            release.set()  # baseline: both actors have read the old body
        return body

    @contextmanager
    def observed_lock(path):
        if (threading.current_thread().name == "global-drain-1"
                and Path(path).parent.resolve() == (global_root / "autoharness").resolve()):
            release.set()  # coordinated actor waits for the first actor's real file lock
        with real_lock(path):
            yield

    def drain(index):
        try:
            results[index] = promoter.drain(f"run{index}", roots=roots[index])
        except Exception as error:
            errors.append(error)

    monkeypatch.setattr(promoter, "_shape", shape)
    monkeypatch.setattr(lock, "file_lock", observed_lock)
    workers = [threading.Thread(target=drain, args=(index,), name=f"global-drain-{index}")
               for index in range(2)]
    workers[0].start()
    try:
        assert first_shaped.wait(5)
        workers[1].start()
        for worker in workers:
            worker.join(5)
    finally:
        release.set()
        for worker in workers:
            if worker.ident is not None:
                worker.join(5)
    assert all(not worker.is_alive() for worker in workers)
    assert not errors
    assert all(results[index][0]["ok"] for index in range(2))
    assert skill_store.read_body("global", "shared", global_root) == BODY.replace("alpha", "gamma").replace("beta", "delta")
    assert sidecar.read("global", "shared", global_root)["patch"] == 2


def test_disabled_global_promotion_does_not_create_global_lock_state(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DISABLE_GLOBAL", True)
    global_root, project_root = tmp_path / "global", tmp_path / "project"
    intent_queue.append("disabled", {
        "action": "create", "name": "shared", "level": "global", "body": BODY,
        "reason": "local fixture", "evidence": "local observation",
    }, project_root)
    verdicts = promoter.drain("disabled", roots={"global": global_root, "project": project_root})
    assert not verdicts[0]["ok"]
    assert verdicts[0]["findings"][0][0] == "routing"
    assert not global_root.exists()
