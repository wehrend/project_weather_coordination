# __manifest__.py
{
    'name': 'Weather-Driven Project Automation',
    'version': '1.0',
    'summary': 'Automatically block or unblock tasks based on the client\'s local weather forecast.',
    'category': 'Services/Project',
    'author': 'Sven Wehrend',
    'depends': ['project', 'base'],
    'data': [
        # 'data/ir_cron_data.xml',
        'views/project_task_views.xml',
    ],
    'installable': True,
    'application': False,
}