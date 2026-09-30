from app.models import Organization, Project, Role, User

def test_day_13_models_are_registered():
    assert Role.__tablename__ == "roles"
    assert User.__tablename__ == "users"
    assert Organization.__tablename__ == "organizations"
    assert Project.__tablename__ == "projects"

def test_day_13_relationship_foreign_keys():
    assert User.__table__.c.role_id.foreign_keys
    assert User.__table__.c.organization_id.foreign_keys
    assert Project.__table__.c.organization_id.foreign_keys
    assert Project.__table__.c.owner_id.foreign_keys
