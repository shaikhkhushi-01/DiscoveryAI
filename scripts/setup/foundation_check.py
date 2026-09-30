from pathlib import Path
import re
ROOT = Path(__file__).resolve().parents[2]
REQUIRED = ['backend/app/main.py','backend/app/core/config.py','backend/app/core/environment.py','backend/app/core/logging.py','frontend/app/page.tsx','docker-compose.yml','docker/backend/Dockerfile','docker/frontend/Dockerfile','backend/requirements.txt','.env.example','.env.development.example','.env.production.example','research/problem_statement.md','research/existing_research.md','research/novelty.md','research/requirements.md','research/architecture.md','research/architecture_decisions.md','research/technology_stack.md']
def main():
    missing=[p for p in REQUIRED if not (ROOT/p).exists()]
    if missing:
        print('FOUNDATION CHECK: FAIL'); [print(' - '+p) for p in missing]; return 1
    compose=(ROOT/'docker-compose.yml').read_text()
    services=('postgres','neo4j','qdrant','redis','backend','frontend')
    for s in services:
        if re.search(r'^  '+s+r':$',compose,re.MULTILINE) is None: return 1
    print('FOUNDATION CHECK: PASS'); print('Required files verified:',len(REQUIRED)); print('Docker services verified:',len(services)); return 0
if __name__=='__main__': raise SystemExit(main())
