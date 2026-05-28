from cedarpy import is_authorized

policies = """
permit(
    principal == ui::User::"user_123",
    action == Action::"View",
    resource == ui::Menu::"operator"
);
"""

req = {
    "principal": 'ui::User::"user_123"',
    "action": 'Action::"View"',
    "resource": 'ui::Menu::"operator"',
    "context": {}
}

principal_entity = {
    "uid": 'ui::User::"user_123"',
    "attrs": {
        "roles": [{"__extn": {"fn": "Set", "arg": ["operator"]}}]
    },
    "parents": []
}
entities = [principal_entity]

print(is_authorized(req, policies, entities))
