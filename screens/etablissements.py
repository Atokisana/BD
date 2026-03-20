"""
screens/etablissements.py - Établissements universitaires d'Antsiranana
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp


ETABLISSEMENTS = [
    {
        "nom": "ENSET",
        "complet": "École Normale Supérieure pour l'Enseignement Technique",
        "mission": "Former des enseignants techniques et des ingénieurs pédagogiques.",
        "mentions": ["Génie Civil", "Génie Électrique", "Génie Informatique", "Génie Mécanique"],
        "parcours": ["Licence", "Master"],
        "description": "L'ENSET est l'établissement phare pour la formation technique et pédagogique. Elle forme les futurs enseignants des lycées techniques ainsi que des ingénieurs.",
        "color": "#1565C0"
    },
    {
        "nom": "ESP",
        "complet": "École Supérieure Polytechnique",
        "mission": "Former des ingénieurs polytechniciens spécialisés.",
        "mentions": ["Génie Civil", "Génie Électrique", "Génie Informatique"],
        "parcours": ["Licence professionnelle", "Master Ingénierie"],
        "description": "L'ESP forme des ingénieurs capables de répondre aux besoins du secteur industriel et technologique de la région Nord de Madagascar.",
        "color": "#4527A0"
    },
    {
        "nom": "AGRO",
        "complet": "École Supérieure des Sciences Agronomiques",
        "mission": "Former des agronomes et spécialistes du développement rural.",
        "mentions": ["Agronomie", "Zootechnie", "Foresterie", "Aquaculture"],
        "parcours": ["Licence", "Master", "Doctorat"],
        "description": "L'ESSA-Antsiranana est dédiée à la formation agronomique adaptée aux spécificités de la région Nord, riche en ressources naturelles.",
        "color": "#2E7D32"
    },
    {
        "nom": "SCIENCES",
        "complet": "Faculté des Sciences",
        "mission": "Enseignement des sciences fondamentales et appliquées.",
        "mentions": ["Mathématiques", "Physique", "Chimie", "Biologie", "Informatique"],
        "parcours": ["Licence", "Master", "Doctorat"],
        "description": "La Faculté des Sciences dispense un enseignement rigoureux en sciences fondamentales, préparant les étudiants à la recherche et à l'enseignement.",
        "color": "#00695C"
    },
    {
        "nom": "FLSH",
        "complet": "Faculté des Lettres et Sciences Humaines",
        "mission": "Formation en lettres, langues, sciences sociales et humaines.",
        "mentions": ["Lettres Modernes", "Histoire-Géographie", "Anglais", "Sociologie"],
        "parcours": ["Licence", "Master", "Doctorat"],
        "description": "La FLSH est le pilier des sciences humaines à Antsiranana, valorisant les langues, l'histoire et la culture malgache.",
        "color": "#BF360C"
    },
    {
        "nom": "DEGSP",
        "complet": "Département d'Économie, Gestion et Sciences Politiques",
        "mission": "Former des économistes, gestionnaires et politologues.",
        "mentions": ["Économie", "Gestion", "Finance", "Sciences Politiques"],
        "parcours": ["Licence", "Master"],
        "description": "Le DEGSP répond aux besoins du secteur économique régional en formant des cadres compétents en gestion et en développement économique.",
        "color": "#F57F17"
    },
    {
        "nom": "ISAE",
        "complet": "Institut Supérieur d'Architecture et d'Environnement",
        "mission": "Former des architectes et urbanistes responsables.",
        "mentions": ["Architecture", "Urbanisme", "Environnement"],
        "parcours": ["Licence", "Master Architecture"],
        "description": "L'ISAE forme des professionnels de l'architecture et de l'urbanisme, intégrant les enjeux environnementaux contemporains.",
        "color": "#6A1B9A"
    },
    {
        "nom": "IST",
        "complet": "Institut Supérieur de Technologie",
        "mission": "Formation professionnelle en technologies appliquées.",
        "mentions": ["Informatique", "Réseaux", "Maintenance industrielle", "Électronique"],
        "parcours": ["BTS", "Licence Professionnelle"],
        "description": "L'IST offre une formation professionnalisante orientée vers l'insertion directe dans le monde du travail technique.",
        "color": "#006064"
    },
    {
        "nom": "ISISFA",
        "complet": "Institut Supérieur d'Informatique, Sciences Fondamentales et Appliquées",
        "mission": "Former des informaticiens et scientifiques de haut niveau.",
        "mentions": ["Informatique", "Mathématiques Appliquées", "Intelligence Artificielle"],
        "parcours": ["Licence", "Master Informatique"],
        "description": "L'ISISFA est spécialisé dans l'informatique et les sciences fondamentales, avec une orientation vers les technologies émergentes.",
        "color": "#1565C0"
    },
]


class EtablissementsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        with self.canvas.before:
            Color(0.05, 0.07, 0.22, 1)
            self.bg = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=lambda *a: setattr(self.bg, 'size', self.size),
                  pos=lambda *a: setattr(self.bg, 'pos', self.pos))

        main = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(8))

        # Header
        header = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        back_btn = Button(text="◀", size_hint=(None, 1), width=dp(40),
                          background_color=(0.2, 0.3, 0.7, 1), background_normal='')
        back_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'accueil'))
        header.add_widget(back_btn)
        header.add_widget(Label(text="[b][Etab] ÉTABLISSEMENTS UNIVERSITAIRES[/b]",
                                 markup=True, font_size=dp(13), color=(1, 0.85, 0.1, 1)))
        main.add_widget(header)

        subtitle = Label(
            text="Universités et instituts d'Antsiranana",
            font_size=dp(11), color=(0.6, 0.8, 1, 0.8),
            size_hint_y=None, height=dp(22)
        )
        main.add_widget(subtitle)

        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', spacing=dp(10),
                             size_hint_y=None, padding=(0, dp(5)))
        content.bind(minimum_height=content.setter('height'))

        for etab in ETABLISSEMENTS:
            card = EtabCard(etab)
            content.add_widget(card)

        scroll.add_widget(content)
        main.add_widget(scroll)
        self.add_widget(main)


class EtabCard(BoxLayout):
    def __init__(self, etab, **kwargs):
        super().__init__(orientation='vertical', size_hint_y=None,
                          spacing=dp(4), **kwargs)
        color_hex = etab['color']
        r, g, b = [int(color_hex.lstrip('#')[i:i+2], 16)/255 for i in (0, 2, 4)]

        # En-tête coloré
        header = BoxLayout(size_hint_y=None, height=dp(58), padding=(dp(12), dp(5)))
        with header.canvas.before:
            Color(r, g, b, 0.9)
            h_rect = Rectangle(size=header.size, pos=header.pos)
        header.bind(size=lambda *a: setattr(h_rect, 'size', header.size),
                    pos=lambda *a: setattr(h_rect, 'pos', header.pos))

        info_box = BoxLayout(orientation='vertical')
        info_box.add_widget(Label(text=f"[b]{etab['nom']}[/b]", markup=True,
                                   font_size=dp(15), color=(1, 1, 1, 1),
                                   halign='left', text_size=(dp(270), None)))
        info_box.add_widget(Label(text=etab['complet'], font_size=dp(10),
                                   color=(0.85, 0.95, 1, 0.9), halign='left',
                                   text_size=(dp(270), None)))
        header.add_widget(info_box)
        self.add_widget(header)

        # Corps
        body = BoxLayout(orientation='vertical', size_hint_y=None,
                          padding=(dp(12), dp(8)), spacing=dp(4))
        with body.canvas.before:
            Color(r * 0.3, g * 0.3, b * 0.3 + 0.1, 0.85)
            b_rect = Rectangle(size=body.size, pos=body.pos)
        body.bind(size=lambda *a: setattr(b_rect, 'size', body.size),
                  pos=lambda *a: setattr(b_rect, 'pos', body.pos))

        def add_row(icon, text, text_color=(0.85, 0.9, 1, 0.9)):
            lbl = Label(
                text=f"{icon} {text}", font_size=dp(11),
                color=text_color, halign='left',
                text_size=(None, None), size_hint_y=None
            )
            lbl.bind(
                width=lambda *x: setattr(lbl, 'text_size', (lbl.width, None)),
                texture_size=lambda *x: setattr(lbl, 'height', lbl.texture_size[1])
            )
            lbl.height = dp(16)
            body.add_widget(lbl)
            return lbl

        mission_lbl = add_row("Objectif:", etab['mission'], (1, 0.9, 0.6, 1))
        desc_lbl = add_row("Info:", etab['description'])
        mentions_str = " • ".join(etab['mentions'])
        add_row("Cours:", f"Mentions : {mentions_str}")
        parcours_str = " | ".join(etab['parcours'])
        add_row("Parcours:", f"Parcours : {parcours_str}", (0.7, 1, 0.7, 1))

        # Hauteur dynamique
        def update_body_height(*a):
            total = sum(c.height for c in body.children if hasattr(c, 'height')) + dp(20)
            body.height = max(total, dp(80))

        for child in body.children:
            child.bind(height=update_body_height)
        body.height = dp(100)

        self.add_widget(body)
        self.height = dp(58) + dp(100) + dp(4)
