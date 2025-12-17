import click
import frappe
from frappe.commands import pass_context

APP_NAME = "my_awesome_app"


def _init_site(ctx):
    site = "darsh-test.alfaedge.in"
    frappe.init(site=site)
    frappe.connect()
    frappe.set_user("Administrator")

def export_docs(ctx):
    _init_site(ctx)

    doctypes = frappe.db.sql_list(
        """
        SELECT dt.name
        FROM `tabDocType` dt
        JOIN `tabModule Def` md ON md.name = dt.module
        WHERE md.app_name = %s
        """,
        (APP_NAME,),
    )

    if not doctypes:
        print("⚠️ No doctypes found")
        return

    from frappe.modules.utils import export_doc

    for doctype in doctypes:
        try:
            export_doc("DocType", doctype)
            print(f"✅ Exported {doctype}")
        except Exception:
            frappe.log_error(frappe.get_traceback(), f"Export failed for {doctype}")
            print(f"❌ Failed {doctype}")

    print(f"\n🎉 Exported {len(doctypes)} doctypes")


@click.command("export-customizations")
@click.option("--doctypes", default="", help="Comma separated doctypes")
@click.option("--path", default=frappe.get_app_path(APP_NAME, "customizations"), help="Export path")
@pass_context
def export_customizations(ctx, doctypes, path):
    _init_site(ctx)

    from my_awesome_app.utils.export_customizations import (
        export_doctype_customizations,
    )

    export_doctype_customizations(
        doctypes=doctypes.split(",") if doctypes else None,
        export_path=path or None,
    )

    frappe.destroy()


@click.command("import-customizations")
@click.option("--path", default=frappe.get_app_path(APP_NAME, "customizations"), help="Import path")
@pass_context
def import_customizations(ctx, path):
    _init_site(ctx)

    from my_awesome_app.utils.import_customizations import (
        import_doctype_customizations,
    )

    import_doctype_customizations(path)

    frappe.destroy()


@click.command("export-all-docs")
@pass_context
def export_all_docs(ctx):
    """
    Export ALL DocTypes belonging to my_awesome_app
    """
    export_docs(ctx)

#Quick Export command to export doctypes and customizations

@click.command("quick-export")
@pass_context
def quick_export(ctx):

    from my_awesome_app.utils.export_customizations import (
        export_doctype_customizations,
    )
    _init_site(ctx)
    export_docs(ctx)
    export_doctype_customizations(
        doctypes=None,
        export_path=frappe.get_app_path(APP_NAME, "customizations"),
    )

# REQUIRED for your bench version
commands = [
    export_customizations,
    import_customizations,
	export_all_docs,
	quick_export,
]