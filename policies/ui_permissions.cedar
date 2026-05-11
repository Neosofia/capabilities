permit (
    principal is ui::User,
    action == Action::"View",
    resource
) when {
    (resource == ui::Menu::"admin" || resource == ui::Menu::"debug") &&
    principal.roles.contains("admin")
};
