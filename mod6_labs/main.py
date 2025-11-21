# main.py
"""Weather Application using Flet v0.28.3"""

import flet as ft
from mod6_labs.weather_service import WeatherService
from mod6_labs.config import Config
import asyncio
import httpx
import json
import os


class WeatherApp:
    """Main Weather Application class."""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.weather_service = WeatherService()
        self.search_history = []
        self.watchlist = []
        self.watchlist_file = "watchlist.json"
        self.load_watchlist()
        self.setup_page()
        self.build_ui()
    
    def setup_page(self):
        """Configure page settings."""
        self.page.title = Config.APP_TITLE
        
        # Add theme switcher
        self.page.theme_mode = ft.ThemeMode.SYSTEM  # Use system theme
        
        # Custom theme Colors
        self.page.theme = ft.Theme(
            color_scheme_seed=ft.Colors.BLUE,
        )
        
        self.page.padding = 20
        
        # Window properties are accessed via page.window object in Flet 0.28.3
        self.page.window.width = Config.APP_WIDTH
        self.page.window.height = Config.APP_HEIGHT
        self.page.window.resizable = False
        self.page.window.center()
    
    def build_ui(self):
        """Build the user interface."""
        # Title
        self.title = ft.Text(
            "Weather App",
            size=32,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.BLUE_700,
        )
        
        # Location button
        self.location_button = ft.IconButton(
            icon=ft.Icons.MY_LOCATION,
            tooltip="Get weather for my location",
            on_click=lambda e: self.page.run_task(self.get_location_weather),
        )
        
        # Theme toggle button
        self.theme_button = ft.IconButton(
            icon=ft.Icons.DARK_MODE,
            tooltip="Toggle theme",
            on_click=self.toggle_theme,
        )
        
        # Update the Column to include the theme button in the title row
        title_row = ft.Row(
            [
                self.title,
                ft.Row(
                    [
                        self.location_button,
                        self.theme_button,
                    ],
                    spacing=10,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        
        # City input field
        self.city_input = ft.TextField(
            label="Enter city name",
            hint_text="e.g., London, Tokyo, New York",
            border_color=ft.Colors.BLUE_400,
            prefix_icon=ft.Icons.LOCATION_CITY,
            autofocus=True,
            on_submit=self.on_search,
        )
        
        # Search history dropdown
        self.history_dropdown = self.build_history_dropdown()
        
        # Search button
        self.search_button = ft.ElevatedButton(
            "Get Weather",
            icon=ft.Icons.SEARCH,
            on_click=self.on_search,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE_700,
            ),
        )
        
        # Add to watchlist button
        add_watchlist_button = ft.ElevatedButton(
            "Add to Watchlist",
            icon=ft.Icons.ADD,
            on_click=lambda e: self.add_to_watchlist(self.city_input.value.strip()),
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.GREEN_700,
            ),
        )
        
        # View comparison button
        comparison_button = ft.ElevatedButton(
            "Compare Cities",
            icon=ft.Icons.COMPARE_ARROWS,
            on_click=lambda e: self.page.run_task(self.display_watchlist_weather),
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.PURPLE_700,
            ),
        )
        
        # Forecast button
        forecast_button = ft.ElevatedButton(
            "Get Forecast",
            icon=ft.Icons.CALENDAR_TODAY,
            on_click=lambda e: self.page.run_task(self.get_forecast, self.city_input.value.strip()),
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.ORANGE_700,
            ),
        )
        
        # Weather display container (initially hidden)
        self.weather_container = ft.Container(
            visible=False,
            bgcolor=ft.Colors.BLUE_50,
            border_radius=10,
            padding=20,
        )
        
        # Error message
        self.error_message = ft.Text(
            "",
            color=ft.Colors.RED_700,
            visible=False,
        )
        
        # Loading indicator
        self.loading = ft.ProgressRing(visible=False)
        
        # Watchlist section
        self.watchlist_column = ft.Column(
            [
                ft.Text("Watchlist", size=16, weight=ft.FontWeight.BOLD),
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
            ],
            spacing=10,
        )
        
        # Add all components to page
        self.page.add(
            ft.Column(
                [
                    title_row,
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    self.history_dropdown,
                    self.city_input,
                    ft.Row(
                        [self.search_button, add_watchlist_button, comparison_button, forecast_button],
                        spacing=10,
                    ),
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    self.loading,
                    self.error_message,
                    self.weather_container,
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    self.watchlist_column,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            )
        )
    
    def on_search(self, e):
        """Handle search button click or enter key press."""
        self.page.run_task(self.get_weather)
    
    async def get_weather(self):
        """Fetch and display weather data."""
        city = self.city_input.value.strip()
        
        # Validate input
        if not city:
            self.show_error("Please enter a city name")
            return
        
        # Show loading, hide previous results
        self.loading.visible = True
        self.error_message.visible = False
        self.weather_container.visible = False
        self.page.update()
        
        try:
            # Fetch weather data
            weather_data = await self.weather_service.get_weather(city)
            
            # Add to search history
            self.add_to_history(city)
            self.update_history_dropdown()
            
            # Display weather
            self.display_weather(weather_data)
            
        except Exception as e:
            self.show_error(str(e))
        
        finally:
            self.loading.visible = False
            self.page.update()
    
    def display_weather(self, data: dict):
        """Display weather information."""
        # Extract data
        city_name = data.get("name", "Unknown")
        country = data.get("sys", {}).get("country", "")
        temp = data.get("main", {}).get("temp", 0)
        feels_like = data.get("main", {}).get("feels_like", 0)
        humidity = data.get("main", {}).get("humidity", 0)
        description = data.get("weather", [{}])[0].get("description", "").title()
        icon_code = data.get("weather", [{}])[0].get("icon", "01d")
        wind_speed = data.get("wind", {}).get("speed", 0)
        
        # Check for extreme conditions and show alerts
        if temp > 35:
            alert = ft.Banner(
                bgcolor=ft.Colors.AMBER_100,
                leading=ft.Icon(ft.Icons.WARNING, color=ft.Colors.AMBER, size=40),
                content=ft.Text("⚠️ High temperature alert!"),
            )
            self.page.banner = alert
            self.page.banner.open = True
        elif temp < 0:
            alert = ft.Banner(
                bgcolor=ft.Colors.BLUE_100,
                leading=ft.Icon(ft.Icons.AC_UNIT, color=ft.Colors.BLUE, size=40),
                content=ft.Text("❄️ Freezing temperature alert!"),
            )
            self.page.banner = alert
            self.page.banner.open = True
        elif wind_speed > 20:
            alert = ft.Banner(
                bgcolor=ft.Colors.ORANGE_100,
                leading=ft.Icon(ft.Icons.AIR, color=ft.Colors.ORANGE, size=40),
                content=ft.Text("💨 Strong wind alert!"),
            )
            self.page.banner = alert
            self.page.banner.open = True
        
        # Build weather display
        self.weather_container.content = ft.Column(
            [
                # Location
                ft.Text(
                    f"{city_name}, {country}",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                ),
                
                # Weather icon and description
                ft.Row(
                    [
                        ft.Image(
                            src=f"https://openweathermap.org/img/wn/{icon_code}@2x.png",
                            width=100,
                            height=100,
                        ),
                        ft.Text(
                            description,
                            size=20,
                            italic=True,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                
                # Temperature
                ft.Text(
                    f"{temp:.1f}°C",
                    size=48,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_900,
                ),
                
                ft.Text(
                    f"Feels like {feels_like:.1f}°C",
                    size=16,
                    color=ft.Colors.GREY_700,
                ),
                
                ft.Divider(),
                
                # Additional info
                ft.Row(
                    [
                        self.create_info_card(
                            ft.Icons.WATER_DROP,
                            "Humidity",
                            f"{humidity}%"
                        ),
                        self.create_info_card(
                            ft.Icons.AIR,
                            "Wind Speed",
                            f"{wind_speed} m/s"
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )
        
        # Add animation to container
        self.weather_container.animate_opacity = 300
        self.weather_container.opacity = 0
        self.weather_container.visible = True
        self.error_message.visible = False
        self.page.update()
        
        # Fade in animation
        self.page.run_task(self.fade_in_weather)
    
    async def fade_in_weather(self):
        """Fade in the weather container."""
        await asyncio.sleep(0.1)
        self.weather_container.opacity = 1
        self.page.update()
    
    def create_info_card(self, icon, label, value):
        """Create an info card for weather details."""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(icon, size=30, color=ft.Colors.BLUE_700),
                    ft.Text(label, size=12, color=ft.Colors.GREY_600),
                    ft.Text(
                        value,
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_900,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
            ),
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            padding=15,
            width=150,
        )
    
    def show_error(self, message: str):
        """Display error message."""
        self.error_message.value = f"❌ {message}"
        self.error_message.visible = True
        self.weather_container.visible = False
        self.page.update()
    
    def toggle_theme(self, e):
        """Toggle between light and dark theme."""
        if self.page.theme_mode == ft.ThemeMode.LIGHT:
            self.page.theme_mode = ft.ThemeMode.DARK
            self.theme_button.icon = ft.Icons.LIGHT_MODE
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            self.theme_button.icon = ft.Icons.DARK_MODE
        self.page.update()
    
    def add_to_history(self, city: str):
        """Add city to search history."""
        if city not in self.search_history:
            self.search_history.insert(0, city)
            self.search_history = self.search_history[:5]  # Keep last 5
    
    def build_history_dropdown(self):
        """Build dropdown with search history."""
        return ft.Dropdown(
            label="Recent Searches",
            options=[ft.dropdown.Option(city) for city in self.search_history],
            on_change=self.load_from_history,
            width=300,
        )
    
    def update_history_dropdown(self):
        """Update the history dropdown options."""
        self.history_dropdown.options = [
            ft.dropdown.Option(city) for city in self.search_history
        ]
        self.page.update()
    
    def load_from_history(self, e):
        """Load weather for selected city from history."""
        if e.control.value:
            self.city_input.value = e.control.value
            self.page.run_task(self.get_weather)
    
    async def get_location_weather(self):
        """Get weather for current location."""
        # Show loading indicator
        self.loading.visible = True
        self.error_message.visible = False
        self.weather_container.visible = False
        self.page.update()
        
        try:
            # Use IP-based geolocation service
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get("https://ipapi.co/json/")
                data = response.json()
                lat, lon = data['latitude'], data['longitude']
                
                # Fetch weather by coordinates
                weather = await self.weather_service.get_weather_by_coordinates(
                    lat, lon
                )
                self.display_weather(weather)
        except Exception as e:
            self.show_error("Could not get your location")
        finally:
            self.loading.visible = False
            self.page.update()
    
    def load_watchlist(self):
        """Load watchlist from file."""
        try:
            if os.path.exists(self.watchlist_file):
                with open(self.watchlist_file, 'r') as f:
                    self.watchlist = json.load(f)
        except Exception as e:
            print(f"Error loading watchlist: {e}")
            self.watchlist = []
    
    def save_watchlist(self):
        """Save watchlist to file."""
        try:
            with open(self.watchlist_file, 'w') as f:
                json.dump(self.watchlist, f)
        except Exception as e:
            print(f"Error saving watchlist: {e}")
    
    def add_to_watchlist(self, city: str):
        """Add city to watchlist."""
        if city and city not in self.watchlist:
            self.watchlist.append(city)
            self.save_watchlist()
            self.update_watchlist_ui()
            return True
        return False
    
    def remove_from_watchlist(self, city: str):
        """Remove city from watchlist."""
        if city in self.watchlist:
            self.watchlist.remove(city)
            self.save_watchlist()
            self.update_watchlist_ui()
    
    def update_watchlist_ui(self):
        """Update watchlist display."""
        self.watchlist_column.controls.clear()
        
        if not self.watchlist:
            self.watchlist_column.controls.append(
                ft.Text("No cities in watchlist", color=ft.Colors.GREY_600)
            )
        else:
            for city in self.watchlist:
                self.watchlist_column.controls.append(
                    ft.Row(
                        [
                            ft.Text(city, size=16, expand=True),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                icon_color=ft.Colors.RED_700,
                                on_click=lambda e, c=city: self.remove_from_watchlist(c),
                            ),
                        ],
                        spacing=10,
                    )
                )
        
        self.page.update()
    
    async def display_watchlist_weather(self):
        """Fetch and display weather for all cities in watchlist."""
        if not self.watchlist:
            self.show_error("Watchlist is empty")
            return
        
        self.loading.visible = True
        self.error_message.visible = False
        self.page.update()
        
        try:
            comparison_cards = []
            
            for city in self.watchlist:
                try:
                    weather_data = await self.weather_service.get_weather(city)
                    comparison_cards.append(self.create_comparison_card(weather_data))
                except Exception as e:
                    comparison_cards.append(
                        ft.Container(
                            content=ft.Text(f"Error loading {city}", color=ft.Colors.RED_700),
                            bgcolor=ft.Colors.RED_50,
                            border_radius=10,
                            padding=15,
                        )
                    )
            
            # Display comparison
            self.weather_container.content = ft.Column(
                [
                    ft.Text(
                        "City Comparison",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Row(
                        comparison_cards,
                        scroll=ft.ScrollMode.AUTO,
                        spacing=10,
                    ),
                ],
                spacing=15,
            )
            
            self.weather_container.animate_opacity = 300
            self.weather_container.opacity = 0
            self.weather_container.visible = True
            self.page.update()
            
            # Fade in
            await self.fade_in_weather()
            
        except Exception as e:
            self.show_error(str(e))
        
        finally:
            self.loading.visible = False
            self.page.update()
    
    def create_comparison_card(self, data: dict):
        """Create a comparison card for a city."""
        city_name = data.get("name", "Unknown")
        country = data.get("sys", {}).get("country", "")
        temp = data.get("main", {}).get("temp", 0)
        humidity = data.get("main", {}).get("humidity", 0)
        description = data.get("weather", [{}])[0].get("description", "").title()
        icon_code = data.get("weather", [{}])[0].get("icon", "01d")
        wind_speed = data.get("wind", {}).get("speed", 0)
        
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        f"{city_name}, {country}",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Image(
                        src=f"https://openweathermap.org/img/wn/{icon_code}@2x.png",
                        width=60,
                        height=60,
                    ),
                    ft.Text(
                        f"{temp:.1f}°C",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_900,
                    ),
                    ft.Text(description, size=12, italic=True),
                    ft.Divider(height=10),
                    ft.Text(f"Humidity: {humidity}%", size=11),
                    ft.Text(f"Wind: {wind_speed} m/s", size=11),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
            ),
            bgcolor=ft.Colors.BLUE_50,
            border_radius=10,
            padding=15,
            width=180,
        )
    
    async def get_forecast(self, city: str):
        """Get 5-day weather forecast."""
        if not city:
            self.show_error("Please enter a city name")
            return
        
        self.loading.visible = True
        self.error_message.visible = False
        self.weather_container.visible = False
        self.page.update()
        
        try:
            forecast_data = await self.weather_service.get_forecast(city)
            self.display_forecast(forecast_data)
        except Exception as e:
            self.show_error(str(e))
        finally:
            self.loading.visible = False
            self.page.update()
    
    def display_forecast(self, data: dict):
        """Display 5-day forecast."""
        try:
            forecast_list = data.get("list", [])
            daily_forecasts = {}
            
            # Group forecasts by day
            for item in forecast_list:
                date = item.get("dt_txt", "").split()[0]  # Extract date YYYY-MM-DD
                
                if date not in daily_forecasts:
                    daily_forecasts[date] = {
                        "temps": [],
                        "descriptions": [],
                        "icons": [],
                        "humidity": [],
                    }
                
                daily_forecasts[date]["temps"].append(item.get("main", {}).get("temp", 0))
                daily_forecasts[date]["descriptions"].append(
                    item.get("weather", [{}])[0].get("description", "").title()
                )
                daily_forecasts[date]["icons"].append(
                    item.get("weather", [{}])[0].get("icon", "01d")
                )
                daily_forecasts[date]["humidity"].append(
                    item.get("main", {}).get("humidity", 0)
                )
            
            # Create forecast cards
            forecast_cards = []
            for i, (date, forecast_data) in enumerate(list(daily_forecasts.items())[:5]):
                temps = forecast_data["temps"]
                high_temp = max(temps)
                low_temp = min(temps)
                description = forecast_data["descriptions"][0] if forecast_data["descriptions"] else "N/A"
                icon_code = forecast_data["icons"][0] if forecast_data["icons"] else "01d"
                avg_humidity = sum(forecast_data["humidity"]) // len(forecast_data["humidity"])
                
                forecast_cards.append(
                    self.create_forecast_card(date, high_temp, low_temp, description, icon_code, avg_humidity)
                )
            
            # Display forecast
            self.weather_container.content = ft.Column(
                [
                    ft.Text(
                        "5-Day Forecast",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Column(
                        forecast_cards,
                        spacing=10,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                ],
                spacing=15,
            )
            
            self.weather_container.animate_opacity = 300
            self.weather_container.opacity = 0
            self.weather_container.visible = True
            self.error_message.visible = False
            self.page.update()
            
            # Fade in
            self.page.run_task(self.fade_in_weather)
            
        except Exception as e:
            self.show_error(f"Error displaying forecast: {str(e)}")
    
    def create_forecast_card(self, date: str, high: float, low: float, description: str, icon: str, humidity: int):
        """Create a forecast card for a single day."""
        return ft.Container(
            content=ft.Row(
                [
                    # Date
                    ft.Column(
                        [
                            ft.Text(date, size=14, weight=ft.FontWeight.BOLD),
                        ],
                        width=100,
                    ),
                    # Icon
                    ft.Image(
                        src=f"https://openweathermap.org/img/wn/{icon}@2x.png",
                        width=50,
                        height=50,
                    ),
                    # Description
                    ft.Column(
                        [
                            ft.Text(description, size=12, italic=True),
                            ft.Text(f"Humidity: {humidity}%", size=11, color=ft.Colors.GREY_700),
                        ],
                        expand=True,
                    ),
                    # Temperatures
                    ft.Column(
                        [
                            ft.Text(
                                f"H: {high:.1f}°C",
                                size=12,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.RED_700,
                            ),
                            ft.Text(
                                f"L: {low:.1f}°C",
                                size=12,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.BLUE_700,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        width=100,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=ft.Colors.BLUE_50,
            border_radius=10,
            padding=15,
        )


def main(page: ft.Page):
    """Main entry point."""
    WeatherApp(page)


if __name__ == "__main__":
    ft.app(target=main)