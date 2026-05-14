"""
toast.py - Notifications toast pour mobile
"""

from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, RoundedRectangle
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.core.window import Window


def show_toast(text, duration=2.5, bg_color=(0.13, 0.55, 0.13, 0.92)):
    """Affiche un toast en bas de l'ecran."""
    root = Window.children[0] if Window.children else None
    if root is None:
        return

    container = FloatLayout(size=Window.size, pos=(0, 0))

    lbl = Label(
        text=text,
        font_size=dp(13),
        color=(1, 1, 1, 1),
        bold=True,
        size_hint=(None, None),
        halign='center',
        valign='middle',
        padding=(dp(20), dp(10)),
    )
    lbl.texture_update()
    lbl.size = (lbl.texture_size[0] + dp(40), lbl.texture_size[1] + dp(20))
    lbl.pos = (
        (Window.width - lbl.width) / 2,
        dp(60),
    )
    lbl.text_size = lbl.size

    with lbl.canvas.before:
        c = Color(*bg_color)
        rr = RoundedRectangle(size=lbl.size, pos=lbl.pos, radius=[dp(20)])
    lbl.bind(
        size=lambda *a: setattr(rr, 'size', lbl.size),
        pos=lambda *a: setattr(rr, 'pos', lbl.pos),
    )

    container.add_widget(lbl)
    container.opacity = 0

    if hasattr(root, 'add_widget'):
        root.add_widget(container)
    else:
        Window.add_widget(container)

    anim_in = Animation(opacity=1, duration=0.25)

    def dismiss(dt):
        anim_out = Animation(opacity=0, duration=0.3)
        anim_out.bind(on_complete=lambda *a: _remove(container, root))
        anim_out.start(container)

    anim_in.bind(on_complete=lambda *a: Clock.schedule_once(dismiss, duration))
    anim_in.start(container)


def _remove(widget, parent):
    try:
        if hasattr(parent, 'remove_widget'):
            parent.remove_widget(widget)
        else:
            Window.remove_widget(widget)
    except Exception:
        pass
