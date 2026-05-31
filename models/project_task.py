# models/project_task.py
import requests
import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)

class ProjectTask(models.Model):
    _inherit = 'project.task'

    weather_status = fields.Char(string='Weather prognosis (tommorrow)', readonly=True, copy=False)
    is_weather_blocked = fields.Boolean(string='Blocked by weather', default=False, readonly=True, copy=False)

    @api.model
    def check_weather_and_update_tasks(self):
        """
        Checks the weather forecast for tomorrow at the customer's location.
        Blocks or unlocks the task based on the chance of rain.
        """
        active_tasks = self.search([
            ('is_closed', '=', False),
            ('partner_id', '!=', False),
            ('partner_id.city', '!=', False)
        ])

1       # temposrary use this key
        api_key = "95ec4ad84ef6491bb3b165529262504" 
        
        url_template = "https://api.weatherapi.com/v1/forecast.json?key={key}&q={city}&days=2&lang=de"

        for task in active_tasks:
            partner = task.partner_id
            city = partner.city

            try:
                response = requests.get(url_template.format(key=api_key, city=city), timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # WeatherAPI liefert ein Array 'forecastday'. Index 1 ist der morgige Tag.
                    forecast_days = data.get('forecast', {}).get('forecastday', [])
                    
                    if len(forecast_days) < 2:
                        continue
                        
                    tomorrow = forecast_days[1]
                    tomorrow_day = tomorrow.get('day', {})
                    
                    # Hier ziehen wir uns clevere Metriken für die Logik:
                    condition_text = tomorrow_day.get('condition', {}).get('text', 'Unbekannt')
                    will_it_rain = tomorrow_day.get('daily_will_it_rain', 0)  # 1 = Ja, 0 = Nein
                    will_it_snow = tomorrow_day.get('daily_will_it_snow', 0)  # 1 = Ja, 0 = Nein
                    avg_temp = tomorrow_day.get('avgtemp_c', 20.0)
                    
                    status_text = f"{condition_text} ({avg_temp}°C)"
                    
                    # Schwellenwert-Logik: Blockieren, wenn es morgen regnet/schneit ODER die Temp unter 0 Grad fällt
                    if will_it_rain == 1 or will_it_snow == 1 or avg_temp < 0:
                        task.write({
                            'weather_status': status_text,
                            'is_weather_blocked': True,
                            'kanban_state': 'blocked'  # Roter Punkt im Odoo-Kanban
                        })
                        # Nachricht im Odoo-Chatter hinterlassen
                        task.message_post(body=(
                           f" Automatic bad weather warning for tomorrow: "
                           f"The task has been blocked. Forecast for {city}: {condition_text}. "
                           f"Risk of rain or danger of frost ({avg_temp}°C)."
                        ))
                    else:
                        if task.is_weather_blocked:
                            task.write({
                                'weather_status': status_text,
                                'is_weather_blocked': False,
                                'kanban_state': 'normal'  # Grüner/Grauer Punkt (Bereit)
                            })
                            task.message_post(body=(
                                f" Weather all-clear for tomorrow: "
                                f"The forecast for {city} is good ({condition_text}, {avg_temp}°C). "
                                f"The task has been released again."
                            ))
                        else:
                            task.write({'weather_status': status_text})

                else:
                    _logger.warning(f"WeatherAPI error {response.status_code} for city / region {city}")

            except Exception as e:
                _logger.error(f"Error on Weather app for task {task.id}: {str(e)}")