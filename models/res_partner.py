import secrets
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    blog_notification_optout = fields.Boolean(
        string='Keine Blog-Benachrichtigungen',
        default=False,
    )
    blog_optout_blog_ids = fields.Many2many(
        'blog.blog',
        'res_partner_blog_optout_rel',
        'partner_id',
        'blog_id',
        string='Abgemeldete Blogs',
    )
    blog_optout_token = fields.Char(copy=False)

    def _get_or_create_blog_token(self):
        self.ensure_one()
        if not self.blog_optout_token:
            self.sudo().blog_optout_token = secrets.token_urlsafe(32)
        return self.blog_optout_token
