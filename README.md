# Python Ray Tracing Renderer

## Überblick

Dieses Projekt ist eine Ray Tracing Rendering-Engine, implementiert in Python. Sie ermöglicht die Erstellung komplexer 3D-Szenen mit fortschrittlichen Rendering-Techniken, einschließlich Reflexionen, Brechungen, Schatten und 3D-Text-Rendering.

## Funktionen

- 🌈 Fortschrittliches Ray Tracing Rendering
- 📷 Konfigurierbares Kamerasystem
- 🧊 Prozedurale 3D-Formengenerierung
- 💡 Unterstützung mehrerer Lichtquellen
- 📝 3D-Text-Rendering
- 🎨 Anpassbare Materialien
- 🌟 Reflexion und Brechung
- 🕯️ Schattenwurf

## Projektstruktur

%%{init: {'theme': 'neutral', 'themeVariables': {
    'primaryColor': '#E6F3FF',
    'primaryTextColor': '#1A1A2E',
    'primaryBorderColor': '#4D5566',
    'lineColor': '#667085'
}}}%%
graph TD
    Scene -->|Configure| Renderer
    Renderer -->|Cast Rays| Ray
    Renderer -->|Generate Rays| Camera
    Renderer -->|Apply Lighting| Lighting
    Renderer -->|Use Materials| Materials
    Renderer -->|Create Shapes| MeshBuilder
    Renderer -->|Render Text| FontRenderer

    Ray --> Vector
    Camera --> Vector
    MeshBuilder --> Vector
    FontRenderer --> Vector

## Kernkomponenten

### Kerndateien
- `vector.py`: 3D-Vektoroperationen
- `ray.py`: Strahlenverfolgung und Schnittlogik
- `camera.py`: Kamerapositionierung und Strahlengenerierung
- `renderer.py`: Hauptmotor des Ray Tracings

### Geometrieerzeugung
- `mesh_builder.py`: Erstellt 3D-Formen (Würfel, Pyramiden, Zylinder)
- `scene_utils.py`: Formmanipulation und Rotationshilfen

### Szenenverwaltung
- `main.py`: Kommandozeilen-Schnittstelle zum Rendern von Szenen
- Szenen-Skripte (`scene_1.py`, `scene_text.py`, usw.): Vordefinierte Szenenkonfigurationen

### Erweiterte Funktionen
- `font_renderer.py`: Konvertiert Text in 3D-Dreiecks-Meshes
- `lighting.py`: Punkt- und Richtungslichtimplementierungen
- `materials.py`: Vordefinierte Materialtypen mit optischen Eigenschaften

## Rendering-Techniken

Der Renderer unterstützt mehrere fortschrittliche Rendering-Techniken:
- Strahl-Objekt-Schnittberechnung (Kugeln, Dreiecke)
- Reflexion und Brechung
- Schattenwurf
- Ambiente, diffuse und spekulative Beleuchtung
- Perspektivische Kameraprojektion
- Mehrfach-Sampling-Antialiasing

## Beispiel zur Szenenerstellung

```python
from vector import Vector
from materials import create_standard_materials

def setup_scene(raster):
    # Materialien erstellen
    materials = create_standard_materials()

    # Reflektierende Kugel hinzufügen
    raster.add_sphere(
        center=Vector(0, 0, 50),
        radius=60,
        material=materials['glass']
    )

    # Beleuchtung einrichten
    raster.add_light(PointLight(
        position=Vector(-300, -300, -200),
        intensity=0.5
    ))

    # Kamera konfigurieren
    raster.set_camera(
        position=Vector(0, 0, -400),
        look_at=Vector(0, 0, 0),
        fov=45
    )
```

## Renderer ausführen

```bash
# Grundlegende Nutzung
python main.py scene_1.py

# Rendering mit benutzerdefinierter Auflösung
python main.py scene_1.py 1920 1080

# Vorschau generieren
python main.py scene_1.py --preview 0.25
```

## Abhängigkeiten

- NumPy
- Pillow (PIL)
- Python 3.7+

## Installation

1. Repository klonen
2. Abhängigkeiten installieren: `pip install numpy pillow`
3. Szenen ausführen mit `python main.py [Szenendatei]`

## Mitwirken

Beiträge sind willkommen! Bitte zögern Sie nicht, einen Pull Request einzureichen.

## Zukünftige Verbesserungen

- Implementierung komplexerer Materialien
- Unterstützung weiterer geometrischer Primitive
- Optimierung der Rendering-Leistung
- Implementierung globaler Beleuchtungstechniken