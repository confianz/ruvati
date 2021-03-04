# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from itertools import groupby
from odoo import api, fields, models, exceptions, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_ship_collect = fields.Boolean(string="Ship Collect", copy=False)
#    carrier_id = fields.Many2one("delivery.carrier", string="Carrier", domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    shipper_number = fields.Char(string="Shipper No.")
    
    @api.onchange('partner_id')
    def ship_collect_onchange_partner(self):
        if self.partner_id and self.partner_id.is_ship_collect:
            self.is_ship_collect = self.partner_id.is_ship_collect
            self.carrier_id = self.partner_id.carrier_id
            self.shipper_number = self.partner_id.shipper_number
        else:
            self.carrier_id = self.partner_id.property_delivery_carrier_id.id
            self.is_ship_collect = False
            self.shipper_number = False

    @api.onchange('is_ship_collect')
    def onchange_ship_collect(self):
        if not self.is_ship_collect:
            self.shipper_number = False
        else:
            self.carrier_id = self.partner_id.carrier_id
            self.shipper_number = self.partner_id.shipper_number

    @api.model
    def create(self, vals):
        sec_warehouse = self.env['stock.warehouse'].search([('warehouse_type', '=', 'sub_warehouse')], limit=1)
        if vals.get('amazon_channel', False) and vals.get('amazon_channel') == 'fba':
            return super(SaleOrder, self).create(vals)
        vals.update({'warehouse_id': sec_warehouse and sec_warehouse.id or vals.get('warehouse_id', False)})
        return super(SaleOrder, self).create(vals)
        
#    def write(self, vals):
#        sec_warehouse = self.env['stock.warehouse'].search([('warehouse_type', '=', 'sub_warehouse')], limit=1)
#        if self.warehouse_id != sec_warehouse:
#            vals.update({'warehouse_id': sec_warehouse and sec_warehouse.id or self.warehouse_id.id})
#        return super(SaleOrder, self).write(vals)

SaleOrder()

