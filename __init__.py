bl_info = {
    "name": "Sound Nodes",
    "blender": (3, 00, 0),
    "category": "Sound",
}

import bpy
from bpy.types import NodeTree, Node, NodeSocket, NodeLink
import os
import sys
import bpy_extras

# Get the path to the add-on directory
addon_directory = os.path.dirname(__file__)

# Append the path to your add-on's external libraries folder
external_libs_path = os.path.join(addon_directory, "external_libs")
if external_libs_path not in sys.path:
    sys.path.append(external_libs_path)

# Now you can import the specific "pydub" modules you need
from pydub import AudioSegment
from pydub.playback import play

# UI Elements

class SoundNodeTree(NodeTree):
    bl_idname = 'SoundNodes'
    bl_label = 'Sound Nodes'
    bl_icon = 'OUTLINER_OB_SPEAKER'

    # Optional function for adding initial nodes when the node tree is created
    def init(self):
        self.nodes.new('GainEffect')
        self.nodes.new('SoundInput')
        self.nodes.new('SoundOutput')
                
# Derived from the NodeTree base type, similar to Menu, Operator, Panel, etc.
# Custom socket type
# Custom socket type
class SoundSocket(NodeSocket):
    # Description string
    """Custom node socket type"""
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'Sound'
    # Label for nice name display
    bl_label = "Sound"

    # Socket color
    def draw_color(self, context, node):
        return (0.4, 0.3, 1, 1.0)  # Purple color for sockets

    # Optional function for drawing the socket input value
    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text=text)
        else:
            # Custom drawing for socket outlines
            socket_rect = layout.box().row().column(align=True)
            socket_rect.scale_y = 1.2
            socket_rect.scale_x = 0.5
            socket_rect.label(text="Sound", icon='SOUND')

    # Add a property for the default value of the socket
    default_value: bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0)

    
# Custom Output Node
class SoundOutput(Node):
    # Description string
    '''Provides Output to the tracks.'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'SoundOutput'
    # Label for nice name display
    bl_label = "Output"
    # Icon identifier
    bl_icon = 'IMPORT'

    def init(self, context):
        self.inputs.new('Sound', "Sound")
        
class SoundInput(Node):
    # Description string
    '''Provides Input to your nodes.'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'SoundInput'
    # Label for nice name display
    bl_label = "Input"
    # Icon identifier
    bl_icon = 'EXPORT'

    def init(self, context):
        self.outputs.new('Sound', "Sound")
        
        
class SoundListener(Node):
    bl_idname = 'SoundListener'
    bl_label = "Listen"
    bl_icon = 'OUTLINER_OB_SPEAKER'

    is_listener_active: bpy.props.BoolProperty(name="Listener Active", default=False)

    def init(self, context):
        self.inputs.new('Sound', "Sound")

    def draw_buttons(self, context, layout):
        row = layout.row()
        if self.is_listener_active:
            row.operator("node.toggle_play_pause", text="Pause", icon="PAUSE")
        else:
            row.operator("node.toggle_play_pause", text="Play", icon="PLAY")

    def update(self):
        if self.is_listener_active:
            audio_data = self.get_audio_data()
            if audio_data:
                play(audio_data)

    def get_audio_data(self):
        input_socket = self.inputs.get('Sound')
        if input_socket and input_socket.is_linked:
            from_socket = input_socket.links[0].from_socket
            if from_socket.bl_idname == 'ImportAudio':
                audio_file = from_socket.audio_file
                if audio_file:
                    return AudioSegment.from_file(audio_file)
        return None

        
# Custom Music Node
class ImportAudio(Node):
    bl_idname = 'ImportAudio'
    bl_label = "Import Audio"
    bl_icon = "FILE_SOUND"

    audio_file: bpy.props.StringProperty(name="Audio File", subtype='FILE_PATH', options={'HIDDEN'}, update=lambda s, c: s.update_audio_file(c))

    def update_audio_file(self, context):
        if self.audio_file:
            ext = os.path.splitext(self.audio_file)[-1].lower()
            if ext not in {'.wav', '.mp3', '.ogg', '.flac', '.aiff', '.m4a', '.aac', '.wma'}:
                self.audio_file = ""
                self.report({'ERROR'}, "Invalid audio file format. Supported formats: WAV, MP3, OGG, FLAC, AIFF, M4A, AAC, WMA")

    def init(self, context):
        self.outputs.new(SoundSocket.bl_idname, "Sound")

    def draw_buttons(self, context, layout):
        layout.prop(self, "audio_file", text="")

    def draw_label(self):
        return os.path.basename(self.audio_file) if self.audio_file else "Import Audio"

    def filter_audio_files(self, folder, files):
        return [f for f in files if os.path.splitext(f.lower())[-1] in {'.wav', '.mp3', '.ogg', '.flac', '.aiff', '.m4a', '.aac', '.wma'}]
        
# Custom panel for the ImportAudio Node
class ImportAudioPanel(bpy.types.Panel):
    bl_idname = "NODE_PT_import_audio"
    bl_label = "Import Audio Panel"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_context = "node"

    @classmethod
    def poll(cls, context):
        return context.active_node and context.active_node.bl_idname == 'ImportAudio'

    def draw(self, context):
        layout = self.layout
        node = context.active_node
        layout.prop(node, "audio_file", text="Audio File")
        
# Custom GainEffect Node
class GainEffect(Node):
    # Description string
    '''Increases/Decreases Gain on Input.'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'GainEffect'
    # Label for nice name display
    bl_label = "Gain"
    # Yeah
    bl_icon = "MODIFIER"

    def update_sockets(self):
        # Find the link from the SoundInput node to this node
        if self.inputs.get("Gain") and self.outputs.get("Sound"):
            link = next((link for link in self.outputs["Sound"].links if link.from_socket.node != self), None)
            if link and link.from_socket.node.bl_idname == 'SoundInput':
                link.to_socket = self.inputs["Gain"]

    def init(self, context):
        self.inputs.new(SoundSocket.bl_idname, "Sound")
        self.outputs.new(SoundSocket.bl_idname, "Sound")
        self.inputs.new('NodeSocketFloat', "Gain").default_value = 1.0 # Add the float input
        
def draw(self, context):
        layout = self.layout
        # Use the color of the Hue/Saturation/Value node (the color of the socket)
        socket_color = (0.2, 0.8, 0.4, 1.0)  # Modify the values to match your desired color
        layout.template_node_header(node=self, text="", icon_value=layout.icon(socket_color))


class SoundToFloatConverter(Node):
    # Description string
    '''Converts Sound into Float'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'STFConverter'
    # Label for nice name display
    bl_label = "Sound to Float"
    # Yeah
    bl_icon = "UV_SYNC_SELECT"

    def init(self, context):
        self.inputs.new('Sound', "Sound")
        self.outputs.new('NodeSocketFloat', "Value")
        
#xtra ui shit

class TogglePlayPauseOperator(bpy.types.Operator):
    bl_idname = "node.toggle_play_pause"
    bl_label = "Toggle Play/Pause"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.space_data.type == 'NODE_EDITOR' and context.space_data.tree_type == 'SoundNodes'

    def execute(self, context):
        tree = context.space_data.node_tree
        listener_node = None

        for node in tree.nodes:
            if node.bl_idname == 'SoundListener':
                listener_node = node
                break

        if listener_node:
            listener_node.is_listener_active = not listener_node.is_listener_active

        return {'FINISHED'}

class SOUNDNODE_PT_view(bpy.types.Panel):
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_label = "Sound Nodes"
    bl_category = "View"

    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'SoundNodes'

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        tree = context.space_data.node_tree
        listener_node = None

        for node in tree.nodes:
            if node.bl_idname == 'SoundListener':
                listener_node = node
                break

        if listener_node:
            if listener_node.is_active:
                row.operator("node.toggle_play_pause", text="Pause", icon="PAUSE")
            else:
                row.operator("node.toggle_play_pause", text="Play", icon="PLAY")



### Node Categories ###
# Node categories are a python system for automatically
# extending the Add menu, toolbar panels and search operator.
# For more examples see scripts/startup/nodeitems_builtins.py

import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem

# our own base class with an appropriate poll function,
# so the categories only show up in our own tree type
class InputCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'SoundNodes'

class OutputCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'SoundNodes'
    
class EffectsCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'SoundNodes'
    
class ConvertersCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'SoundNodes'
    
# all categories in a list
node_categories = [
    # identifier, label, items list
    InputCategory('INPUT_NODES', "Input", items=[
        NodeItem("SoundInput"),
        NodeItem("ImportAudio"),  # Add the ImportAudio node to the Input category
    ]),
    OutputCategory('OUTPUT_NODES', "Output", items=[
        NodeItem("SoundOutput"),
        NodeItem("SoundListener"),
    ]),
    EffectsCategory('EFFECT_NODES', "Effect", items=[
        NodeItem("GainEffect"),
    ]),
    ConvertersCategory('CONVERTER_NODES', "Converter", items=[
        NodeItem("STFConverter"),
    ]),
]



classes = (TogglePlayPauseOperator, SoundNodeTree, SoundSocket, SoundToFloatConverter, SoundInput, SoundOutput, SoundListener, GainEffect, ImportAudio, ImportAudioPanel, SOUNDNODE_PT_view)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    # Register the SoundNodeTree as a subtype of bpy.types.NodeTree
    bpy.types.SoundNodes = SoundNodeTree

    nodeitems_utils.register_node_categories('CUSTOM_NODES', node_categories)

    bpy.types.NodeLink = CustomNodeLink
    bpy.app.handlers.load_post.append(GainEffect.update_sockets)

def unregister():
    nodeitems_utils.unregister_node_categories('CUSTOM_NODES')

    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

    # Unregister the SoundNodeTree
    del bpy.types.SoundNodes

    bpy.types.NodeLink = CustomNodeLink
    bpy.app.handlers.load_post.remove(update_sockets)

if __name__ == "__main__":
    register()