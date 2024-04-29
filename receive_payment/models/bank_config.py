from odoo import api, fields, models


class BankConfig(models.Model):
    _name = "bank.config"
    _description = "Bank Configuration"
    _rec_name = 'bank_name'

    bank_name = fields.Many2one('res.bank', string='Bank Name', required=True)
    active = fields.Boolean(string='Active', default=True)
