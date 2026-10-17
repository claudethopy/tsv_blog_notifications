import logging
from odoo import models, fields

_logger = logging.getLogger(__name__)


class BlogNotificationQueue(models.Model):
    _name = 'tsv.blog.notification.queue'
    _description = 'Blog-Benachrichtigungs-Warteschlange'
    _order = 'id asc'

    blog_post_id = fields.Many2one('blog.post', string='Blogbeitrag', required=True, ondelete='cascade')
    partner_id = fields.Many2one('res.partner', string='Empfänger', required=True, ondelete='cascade')
    email = fields.Char(string='E-Mail', required=True)
    state = fields.Selection([
        ('pending', 'Ausstehend'),
        ('sent', 'Gesendet'),
        ('failed', 'Fehlgeschlagen'),
    ], default='pending', string='Status')
    sent_at = fields.Datetime(string='Gesendet am', readonly=True)
    error_message = fields.Char(string='Fehler', readonly=True)

    def _get_sender(self):
        position = self.env['tsv.position'].search(
            [('contact_id.email', '!=', False)], limit=1
        )
        if position and position.contact_id.email:
            return position.contact_id.email
        company = self.env['res.company'].sudo().search([], limit=1)
        return company.email or False

    def _send_batch(self):
        params = self.env['ir.config_parameter'].sudo()
        if params.get_param('tsv_blog_notifications.enabled', 'True') != 'True':
            return
        batch_size = int(params.get_param('tsv_blog_notifications.batch_size', '30'))
        base_url = params.get_param('web.base.url')

        pending = self.search([('state', '=', 'pending')], limit=batch_size)
        if not pending:
            return

        email_from = self._get_sender()

        for line in pending:
            post = line.blog_post_id
            partner = line.partner_id.sudo()
            try:
                token = partner._get_or_create_blog_token()
                body = self.env['ir.qweb']._render(
                    'tsv_blog_notifications.blog_notification_email_body',
                    {
                        'post': post,
                        'partner': partner,
                        'unsubscribe_blog_url': f'{base_url}/blog/abmelden/{token}/{post.blog_id.id}',
                        'unsubscribe_all_url': f'{base_url}/blog/abmelden/{token}',
                        'base_url': base_url,
                    },
                )
                mail = self.env['mail.mail'].sudo().create({
                    'subject': f'Neuer Beitrag: {post.name}',
                    'email_from': email_from,
                    'email_to': line.email,
                    'body_html': body,
                    'auto_delete': False,
                })
                mail.send(raise_exception=True)
                if mail.state == 'sent':
                    line.write({'state': 'sent', 'sent_at': fields.Datetime.now()})
                else:
                    line.write({'state': 'failed', 'error_message': mail.failure_reason or 'Unbekannter Fehler'})
                mail.sudo().unlink()
            except Exception as e:
                _logger.exception('Blog-Benachrichtigung fehlgeschlagen für %s', line.email)
                line.write({'state': 'failed', 'error_message': str(e)[:255]})
