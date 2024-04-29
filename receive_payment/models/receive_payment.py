from odoo import api, fields, models
from odoo.tools.translate import _


class ReceivePayment(models.Model):
    _name = "receive.payment"
    _descriptions = "Receive Payment"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "reference_no"

    reference_no = fields.Char(string='Serial No', required=True,
                               readonly=True, default=lambda self: _('New'))
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, readonly=True)
    responsible_person = fields.Many2one('res.users', string='Responsible Person',
                                         default=lambda self: self.env.user, readonly=True)
    sales_person = fields.Char(string="Sales Person")
    partner_id = fields.Many2one('res.partner', string='Customer Name', required=True)
    journal_id = fields.Many2one('account.journal', string='Deposit To', domain="[('type', 'in', ['bank', 'cash'])]",
                                 required=True, )
    deposit_branch = fields.Char(string='Deposit Branch', required=True)
    payment_mode = fields.Selection([
        ('cash', 'Cash'),
        ('cheque', 'Cheque'),
    ], default="cheque", string="Payment Mode", required=True, tracking=True)
    amount = fields.Float(string='Amount', tracking=True, required=True)
    money_receipt_no = fields.Char(string='Money Receipt No', tracking=True, required=True)
    money_receipt_date = fields.Date(string='Money Receipt Date', tracking=True, required=True)

    instrument_no = fields.Char(string='Cheque No', tracking=True)
    bank_id = fields.Many2one('res.bank', string='Bank Name')
    # name = fields.Many2one('res.bank', string='Bank Name')
    branch_name = fields.Char(string='Branch Name')
    maturity_date = fields.Date(string='Maturity Date')
    bank_deposit_date = fields.Date(string='Deposit Date', required=True)
    deposit_slip_no = fields.Char(string='Deposit Slip No', required=True)
    payment_id = fields.Many2one('account.payment', string='Payment Ref', readonly=True, copy=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('cancel', 'Cancelled')], string='Status', default='draft', invisible='1', tracking=True)
    remarks = fields.Text(string='Remarks')
    is_readonly = fields.Boolean(string='Is Readonly?', compute='_compute_is_readonly', store=True)
    active = fields.Boolean(string='Active', default=True, tracking=True)

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        # Add domain to filter records by the selected company
        if self.env.context.get('allowed_company_ids'):
            args += [('company_id', 'in', self.env.context['allowed_company_ids'])]

        return super(ReceivePayment, self).search(args, offset, limit, order, count)

    @api.model
    def create(self, vals):
        if vals.get('reference_no', _('New')) == _('New'):
            vals['reference_no'] = self.env['ir.sequence'].next_by_code(
                'receive.payment') or _('New')
        res = super(ReceivePayment, self).create(vals)
        return res

    def copy(self, default=None):
        if default is None:
            default = {}
            default.update({
                'reference_no': self.env['ir.sequence'].next_by_code('receive.payment') or _('New')
            })
        return super(ReceivePayment, self).copy(default)

    def button_reset_to_draft(self):
        self.write({
            'state': "draft"
        })

    def button_cancel(self):
        self.write({
            'state': "cancel"
        })

    def button_posted(self):
        customer_payment = self.generate_customer_payment()
        customer_payment.action_post()
        self.write({
            'state': 'posted',
            'payment_id': customer_payment.id,
        })

    def generate_customer_payment(self):
        customer_payment_vals = {
            'partner_type': 'customer',
            'partner_id': self.partner_id.id,
            'payment_type': 'inbound',
            'date': self.bank_deposit_date,
            'amount': self.amount,
            'journal_id': self.journal_id.id,
            'ref': self.money_receipt_no,
            # 'cheque_reference': self.instrument_no,
            # Set other required fields based on your business logic and requirements
        }
        customer_payment = self.env['account.payment'].create(customer_payment_vals)
        return customer_payment

    @api.depends('state')
    def _compute_is_readonly(self):
        for record in self:
            if record.state in 'posted':
                record.is_readonly = True
            else:
                record.is_readonly = False
