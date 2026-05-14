{
    'name': 'TSV Blog-Benachrichtigungen',
    'version': '18.0.1.0.0',
    'summary': 'Automatische E-Mail-Benachrichtigung für TSV-Mitglieder bei neuen Blogbeiträgen',
    'author': 'TSV Schwerin',
    'category': 'Website',
    'depends': ['website_blog', 'tsv_membership_form'],
    'data': [
        'views/templates.xml',
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
