from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    blog_notifications_enabled = fields.Boolean(
        string='Blog-Benachrichtigungen aktiviert',
        config_parameter='tsv_blog_notifications.enabled',
    )
    blog_notifications_batch_size = fields.Integer(
        string='E-Mails pro Sendevorgang',
        config_parameter='tsv_blog_notifications.batch_size',
        default=30,
    )
