"""Ortak test fikstürleri: sentetik .sav üret → motoru çalıştır → demo koşu dizini."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from sav2q1.engine import runner
from sav2q1.tests.synth import make_synthetic

EXAMPLES = Path(__file__).resolve().parents[1] / "examples" / "demo"


@pytest.fixture(scope="session")
def demo_run(tmp_path_factory):
    rundir = tmp_path_factory.mktemp("run")
    sav = rundir / "data.sav"
    make_synthetic(str(sav))

    shutil.copytree(EXAMPLES / "sections", rundir / "sections")
    for f in ["manuscript.json", "evidence_store.json",
              "evidence_store_badquote.json", "analysis_plan.json"]:
        shutil.copy(EXAMPLES / f, rundir / f)

    runner.main(["run", "--sav", str(sav),
                 "--plan", str(rundir / "analysis_plan.json"),
                 "--rundir", str(rundir)])
    return rundir
