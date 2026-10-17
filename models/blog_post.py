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
        params = self.env['ir.config_parameter'].sudo()
        if params.get_param('tsv_blog_notifications.enabled', 'True') != 'True':
            return

        candidates = self.env['res.partner'].search([
            ('tsv_membership_state', '=', 'member'),
            ('blog_notification_optout', '=', False),
            ('email', '!=', False),
        ])
        partners = candidates.filtered(
            lambda p: self.blog_id.id not in p.blog_optout_blog_ids.ids
        )

        queue_vals = []
        for partner in partners:
            partner._get_or_create_blog_token()
            queue_vals.append({
                'blog_post_id': self.id,
                'partner_id': partner.id,
                'email': partner.email,
            })

        if queue_vals:
            self.env['tsv.blog.notification.queue'].create(queue_vals)
