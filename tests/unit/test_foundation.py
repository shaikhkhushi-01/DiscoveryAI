from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def test_required_foundation_files_exist():
    required=['backend/app/main.py','backend/app/core/config.py','backend/app/core/environment.py','backend/app/core/logging.py','frontend/app/page.tsx','docker-compose.yml','docker/backend/Dockerfile','docker/frontend/Dockerfile','backend/requirements.txt','.env.example','.env.development.example','.env.production.example']
    missing=[p for p in required if not (ROOT/p).exists()]
    assert not missing, f'Missing foundation files: {missing}'
def test_compose_contains_required_services():
    compose=(ROOT/'docker-compose.yml').read_text()
    for service in ('postgres','neo4j','qdrant','redis','backend','frontend'): assert f'  {service}:' in compose
