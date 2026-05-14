from odoo import http
from odoo.http import request


class BlogUnsubscribeController(http.Controller):

    @http.route([
        '/blog/abmelden/<string:token>',
        '/blog/abmelden/<string:token>/<int:blog_id>',
    ], auth='public', website=True, methods=['GET'])
    def blog_unsubscribe(self, token, blog_id=None, **kwargs):
        partner = request.env['res.partner'].sudo().search(
            [('blog_optout_token', '=', token)], limit=1
        )
        if not partner:
            return request.render('tsv_blog_notifications.blog_unsubscribe_invalid')

        if blog_id:
            blog = request.env['blog.blog'].sudo().browse(blog_id).exists()
            if not blog:
                return request.render('tsv_blog_notifications.blog_unsubscribe_invalid')
            partner.blog_optout_blog_ids = [(4, blog.id)]
            return request.render(
                'tsv_blog_notifications.blog_unsubscribe_done',
                {'mode': 'blog', 'blog_name': blog.name},
            )

        partner.blog_notification_optout = True
        return request.render(
            'tsv_blog_notifications.blog_unsubscribe_done',
            {'mode': 'all'},
        )
