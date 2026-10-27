{
    'name': 'TSV Blog-Benachrichtigungen',
    'version': '18.0.1.3.0',
    'summary': 'Automatische E-Mail-Benachrichtigung für TSV-Mitglieder bei neuen Blogbeiträgen',
    'author': 'TSV Schwerin',
    'category': 'Website',
    'depends': ['website_blog', 'tsv_membership_form', 'tsv_main'],
    'data': [
        'security/ir.model.access.csv',
        'data/cron.xml',
        'views/templates.xml',
        'views/res_partner_views.xml',
        'views/blog_notification_queue_views.xml',
        'views/settings_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
