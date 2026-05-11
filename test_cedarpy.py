from cedarpy import is_authorized

policies = """
permit(
    principal == ui::User::"user_123",
    action == Action::"View",
    resource == ui::Menu::"admin"
);
"""

req = {
    "principal": 'ui::User::"user_123"',
    "action": 'Action::"View"',
    "resource": 'ui::Menu::"admin"',
    "context": {}
}

principal_entity = {
    "uid": 'ui::User::"user_123"',
    "attrs": {
        "roles": [{"__extn": {"fn": "Set", "arg": ["admin"]}}]
    },
    "parents": []
}
entities = [principal_entity]

print(is_authorized(req, policies, entities))
