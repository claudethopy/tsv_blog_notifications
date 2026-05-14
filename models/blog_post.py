from odoo import models


class BlogPost(models.Model):
    _inherit = 'blog.post'

    def write(self, vals):
        was_published = {p.id: p.is_published for p in self}
        result = super().write(vals)
        if vals.get('is_published'):
            for post in self:
                if not was_published.get(post.id):
                    post._notify_members()
        return result

    def _notify_members(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        candidates = self.env['res.partner'].search([
            ('tsv_membership_state', '=', 'member'),
            ('blog_notification_optout', '=', False),
            ('email', '!=', False),
        ])
        partners = candidates.filtered(
            lambda p: self.blog_id.id not in p.blog_optout_blog_ids.ids
        )

        for partner in partners:
            token = partner._get_or_create_blog_token()
            body = self.env['ir.qweb']._render(
                'tsv_blog_notifications.blog_notification_email_body',
                {
                    'post': self,
                    'partner': partner,
                    'unsubscribe_blog_url': f'{base_url}/blog/abmelden/{token}/{self.blog_id.id}',
                    'unsubscribe_all_url': f'{base_url}/blog/abmelden/{token}',
                    'base_url': base_url,
                },
            )
            self.env['mail.mail'].sudo().create({
                'subject': f'Neuer Beitrag: {self.name}',
                'email_to': partner.email,
                'body_html': body,
                'auto_delete': True,
            }).send()
