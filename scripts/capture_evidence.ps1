$ErrorActionPreference = 'Stop'
$evidence = 'review_packets/evidence'
New-Item -ItemType Directory -Force -Path $evidence | Out-Null

python main.py | Tee-Object -FilePath "$evidence/terminal_execution.txt"
Copy-Item artifacts/replay_evidence.json "$evidence/replay_evidence.json" -Force
python -m pytest -q | Tee-Object -FilePath "$evidence/pytest_execution.txt"
python -m coverage run -m pytest -q
python -m coverage report | Tee-Object -FilePath "$evidence/coverage_report.txt"
python benchmark.py | Tee-Object -FilePath "$evidence/benchmark_output.txt"
Get-ChildItem -Recurse -File -Exclude '*.pyc' -ErrorAction SilentlyContinue |
    ForEach-Object { $_.FullName } |
    Tee-Object -FilePath "$evidence/project_structure.txt"
