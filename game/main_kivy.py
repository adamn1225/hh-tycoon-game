from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout

class TruckGame(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.truck_x = 400
        self.truck_y = 300
        self.speed = 200  # pixels per second
        self.fuel = 100.0
        self.fuel_drain = 10.0  # per second when moving
        
        # Create fuel label
        self.fuel_label = Label(
            text=f'Fuel: {self.fuel:.1f}%',
            pos=(20, Window.height - 60),
            size_hint=(None, None),
            color=(1, 1, 1, 1)
        )
        self.add_widget(self.fuel_label)
        
        # Game over label
        self.game_over_label = Label(
            text='Out of fuel! Game Over',
            pos=(Window.width/2 - 100, Window.height/2),
            size_hint=(None, None),
            color=(1, 0, 0, 1)
        )
        
        # Bind keyboard events
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        if self._keyboard:
            self._keyboard.bind(on_key_down=self.on_key_down)
            self._keyboard.bind(on_key_up=self.on_key_up)
        
        # Movement state
        self.keys_pressed = set()
        
        # Start the game loop
        Clock.schedule_interval(self.update, 1.0/60.0)

    def _keyboard_closed(self):
        if self._keyboard:
            self._keyboard.unbind(on_key_down=self.on_key_down)
            self._keyboard.unbind(on_key_up=self.on_key_up)
            self._keyboard = None

    def on_key_down(self, keyboard, keycode, text, modifiers):
        # keycode is a tuple (scan_code, key_name)
        key_name = keycode[1]
        if key_name in ['left', 'right', 'up', 'down']:
            self.keys_pressed.add(key_name)
        return True

    def on_key_up(self, keyboard, keycode):
        # keycode is a tuple (scan_code, key_name)  
        key_name = keycode[1]
        if key_name in self.keys_pressed:
            self.keys_pressed.remove(key_name)
        return True

    def update(self, dt):
        moved = False
        
        if self.fuel > 0:
            # Handle movement
            if 'left' in self.keys_pressed:  # Left arrow
                self.truck_x -= self.speed * dt
                moved = True
            if 'right' in self.keys_pressed:  # Right arrow
                self.truck_x += self.speed * dt
                moved = True
            if 'up' in self.keys_pressed:  # Up arrow
                self.truck_y += self.speed * dt
                moved = True
            if 'down' in self.keys_pressed:  # Down arrow
                self.truck_y -= self.speed * dt
                moved = True
            
            # Drain fuel when moving
            if moved:
                self.fuel -= self.fuel_drain * dt
                if self.fuel < 0:
                    self.fuel = 0
        
        # Keep truck on screen
        self.truck_x = max(25, min(Window.width - 75, self.truck_x))
        self.truck_y = max(25, min(Window.height - 75, self.truck_y))
        
        # Update fuel display
        self.fuel_label.text = f'Fuel: {self.fuel:.1f}%'
        
        # Show game over if out of fuel
        if self.fuel <= 0 and self.game_over_label.parent is None:
            self.add_widget(self.game_over_label)
        elif self.fuel > 0 and self.game_over_label.parent is not None:
            self.remove_widget(self.game_over_label)
        
        # Redraw
        self.canvas.clear()
        with self.canvas:
            # Draw background
            Color(0.08, 0.08, 0.08, 1)
            Rectangle(pos=(0, 0), size=(Window.width, Window.height))
            
            # Draw fuel bar background
            Color(0.24, 0.24, 0.24, 1)
            Rectangle(pos=(20, Window.height - 40), size=(200, 20))
            
            # Draw fuel bar
            Color(0, 0.8, 0, 1)
            fuel_width = max(0, (self.fuel / 100.0) * 200)
            Rectangle(pos=(20, Window.height - 40), size=(fuel_width, 20))
            
            # Draw truck
            Color(0.8, 0, 0, 1)
            Rectangle(pos=(self.truck_x, self.truck_y), size=(50, 30))

class HeavyHaulApp(App):
    def build(self):
        game = TruckGame()
        return game

if __name__ == '__main__':
    HeavyHaulApp().run()
