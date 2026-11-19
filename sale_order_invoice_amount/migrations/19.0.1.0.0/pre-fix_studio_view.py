import logging

from odoo.upgrade import util

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    # Vues héritées de sale.order qui référencent le champ disparu
    cr.execute("""
        SELECT v.id, imd.module, imd.name
          FROM ir_ui_view v
          JOIN ir_model_data imd
            ON imd.model = 'ir.ui.view' AND imd.res_id = v.id
         WHERE v.model = 'sale.order'
           AND v.inherit_id IS NOT NULL
           AND v.arch_db::text LIKE '%%invoiced_amount%%'
           AND imd.module = 'studio_customization'
    """)
    for view_id, module, name in cr.fetchall():
        _logger.info("Fixing studio view %s.%s", module, name)
        with util.edit_view(cr, view_id=view_id) as arch:
            for node in arch.xpath("//field[@name='invoiced_amount']"):
                parent = node.getparent()
                parent.remove(node)

    # Vue liste dédiée au champ disparu : suppression complète
    cr.execute("SELECT id FROM ir_ui_view WHERE name = 'sale.order.tree.invoiced_amount'")
    for (view_id,) in cr.fetchall():
        _logger.info("Removing view sale.order.tree.invoiced_amount (id %s)", view_id)
        util.remove_view(cr, view_id=view_id)
