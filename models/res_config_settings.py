from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    weather_api_key = fields.Char(
        string='OpenWeatherMap API Key',
        config_parameter='project_weather_coordination.weather_api_key',
        help="Insert here you weatherapi.com key."
    )