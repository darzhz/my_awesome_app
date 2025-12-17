import frappe
import json
import os

CUSTOMIZATION_TYPES = {
    "custom_fields": "Custom Field",
    "property_setters": "Property Setter",
    "custom_scripts": "Custom Script",
}

def export_doctype_customizations(
    doctypes: list[str] | None = None,
    export_path: str | None = None,
):
    """
    Export customizations (Custom Fields, Property Setters, Custom Scripts)
    for given doctypes into JSON files.
    """

    export_path = export_path or frappe.get_app_path(
       "my_awesome_app", "customizations"
    )

    os.makedirs(export_path, exist_ok=True)

    if not doctypes:
        doctypes = frappe.get_all(
            "DocType",
            filters={"custom": 0},
            pluck="name",
        )

    for doctype in doctypes:
        data = {}

        # Custom Fields
        data["custom_fields"] = frappe.get_all(
            "Custom Field",
            filters={"dt": doctype},
            fields="*",
            order_by="idx",
        )

        # Property Setters
        data["property_setters"] = frappe.get_all(
            "Property Setter",
            filters={"doc_type": doctype},
            fields="*",
        )

        # Custom Scripts
        data["client_scripts"] = frappe.get_all(
            "Client Script",
            filters={"dt": ["in", doctypes]} if doctypes else {},
            fields=["*"],
        )

        data["server_scripts"] = frappe.get_all(
            "Server Script",
            filters={"reference_doctype": ["in", doctypes]} if doctypes else {},
            fields=["*"],
        )

        data["custom_perms"] = frappe.get_all(
			"Custom DocPerm", fields="*", filters={"parent": doctype}, order_by="name"
		)


        # Skip empty exports
        if not any(data.values()):
            continue

        file_path = os.path.join(export_path, f"{doctype}.json")
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2, default=str)

        print(f"Exported customizations for {doctype}")

    print("Customization export completed :)")
    