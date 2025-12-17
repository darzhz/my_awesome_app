import frappe
import json
import os


def upsert(doctype, filters, values):
    name = frappe.db.get_value(doctype, filters)

    if name:
        doc = frappe.get_doc(doctype, name)
        doc.update(values)

        # 🔑 critical flags
        doc.flags.ignore_permissions = True
        doc.flags.ignore_version = True

        # 🔥 bypass save()
        doc.db_update()
        return "updated"
    else:
        doc = frappe.get_doc({
            "doctype": doctype,
            **values
        })

        doc.flags.ignore_permissions = True
        doc.flags.ignore_version = True

        doc.insert()
        return "inserted"



def import_doctype_customizations(import_path: str):
    """
    Import customizations from JSON files and sync them into the site.
    """

    files = [f for f in os.listdir(import_path) if f.endswith(".json")]

    for file in files:
        with open(os.path.join(import_path, file)) as f:
            data = json.load(f)

        # --------------------
        # Custom Fields
        # --------------------
        for cf in data.get("custom_fields", []):
            result = upsert(
                "Custom Field",
                filters={
                    "dt": cf["dt"],
                    "fieldname": cf["fieldname"],
                },
                values=cf
            )
            print(
                f"- Custom Field {cf['dt']}.{cf['fieldname']} {result}"
            )

        # --------------------
        # Property Setters
        # --------------------
        for ps in data.get("property_setters", []):
            result = upsert(
                "Property Setter",
                filters={
                    "doc_type": ps["doc_type"],
                    "field_name": ps["field_name"],
                    "property": ps["property"],
                },
                values=ps
            )
            print(
                f"- Property Setter {ps['doc_type']}.{ps['field_name']} {result}"
            )

        # --------------------
        # Client Scripts
        # --------------------
        for cs in data.get("client_scripts", []):
            result = upsert(
                "Client Script",
                filters={"name": cs.get("name")},
                values=cs
            )
            print(f"- Client Script {cs.get('name')} {result}")

        # --------------------
        # Server Scripts
        # --------------------
        for ss in data.get("server_scripts", []):
            result = upsert(
                "Server Script",
                filters={"name": ss.get("name")},
                values=ss
            )
            print(f"- Server Script {ss.get('name')} {result}")
        # --------------------
        # Custom Perms
        # --------------------
        custom_perms = data.get("custom_perms", [])

        if custom_perms:
            parent_doctype = custom_perms[0]["parent"]

            # ❗ OVERRIDE behavior (same as Frappe)
            frappe.db.delete("Custom DocPerm", {"parent": parent_doctype})

            for perm in custom_perms:
                doc = frappe.get_doc({
                    "doctype": "Custom DocPerm",
                    **perm
                })

                doc.flags.ignore_permissions = True
                doc.flags.ignore_version = True

                # must be db_insert (not insert) to avoid validation noise
                doc.db_insert()

            print(f"- Custom DocPerm overridden for {parent_doctype}")

        frappe.db.commit()
        print(f"==> Imported customizations from {file}")

    print(f"---------  Customization import completed ({len(files)} files) -----------")