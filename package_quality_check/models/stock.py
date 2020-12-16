# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        cr = self._cr
        if self.picking_type_id == self.picking_type_id.warehouse_id.pack_type_id:
            if not all(move.product_uom_qty == move.quantity_done for move in self.move_lines):
                raise ValidationError('Cannot validate the QC process without completing Quality Check for all products of this order')
            
            if self.state == 'done':
                raise ValidationError('This picking is already validated.')
            if all(move.product_uom_qty == move.quantity_done for move in self.move_lines):
                res = super(StockPicking, self).button_validate()
                cr.execute("select move_dest_id from stock_move_move_rel where move_orig_id = %s" % (self.move_lines[0].id))
                out_move_ids = [x[0] for x in cr.fetchall()]
                out_picking = self.env['stock.move'].browse(out_move_ids)[0].picking_id
                if out_picking:
                    out_picking.action_assign()
                    for line in out_picking.move_line_ids:
                        line.qty_done = line.product_uom_qty
                    if all(move.product_uom_qty == move.quantity_done for move in out_picking.move_lines):
                        out_picking.button_validate()
                return res
        return super(StockPicking, self).button_validate()


#    def action_done(self):
#        """ Overrides to generate a bacth process for outgoing Delivery picking for all done QC picking.
#        """
#        res = super(StockPicking, self).action_done()
#        cr = self._cr
#        for rec in self:
#            if rec.picking_type_id == rec.picking_type_id.warehouse_id.pack_type_id:
#                cr.execute("select move_dest_id from stock_move_move_rel where move_orig_id = %s" % (rec.move_lines[0].id))
#                pick_move_ids = [x[0] for x in cr.fetchall()]
#                out_picking = self.env['stock.move'].browse(pick_move_ids)[0].picking_id
#                if out_picking and out_picking.picking_type_id == rec.picking_type_id.warehouse_id.out_type_id and out_picking.origin == rec.origin:
#                    batch_out = self.env['stock.picking.batch'].search([('picking_type_id', '=', out_picking.picking_type_id.id), ('state', '=', 'draft')], limit=1)
#                    if batch_out and rec.id not in batch_out.picking_ids.ids:
#                        out_picking.batch_id = batch_out.id
#                    if not batch_out:
#                        batch_out = self.env['stock.picking.batch'].create({'picking_type_id': out_picking.picking_type_id.id})
#                        out_picking.batch_id = batch_out.id
#        return res

    def action_validate_qc(self):
        """ Validates the QC picking if its all moves are done, which in turn validates its out picking.
        """
        for rec in self:
            cr = self._cr
            if rec.picking_type_id == rec.picking_type_id.warehouse_id.pack_type_id:
                if all(move.product_uom_qty == move.quantity_done for move in rec.move_lines):
                    rec.button_validate()
        return True

StockPicking()

