# Sound Nodes Documentation

Sound Nodes allow you to have sound in Blender.

## Nodes

### Inputs/Output Nodes

#### Input Node
The Input node is a primary node that supplies your nodes with sound. This node is in coordination with the Sound Sequencer as it cannot be used with Speaker objects.

##### Outputs
Sound Socket - Sound

#### Import Audio Node
The Import Audio node allows the ability to import audio from a file.

##### Inputs
File - Allows the ability to select an audio file

##### Outputs
Sound Socket - Sound



#### Output Node
The Output node is the output to both the Speaker object and the Sound Sequencer. This node outputs sound to your Sound Sequencer track and your speaker object.

##### Inputs
Sound Socket - Sound for Output

#### Listener Node
The Listener node allows you to temporarily listen in from inside a node graph. It can be plugged into the Sound Socket to listen to the audio in your node tree.

##### Inputs
Sound Socket - Sound Input

### Effect Nodes

#### Gain Node
The Gain node adjusts the gain of the sound passed into the node.

##### Inputs
Sound Socket - Sound Input
Gain - Gain Input 

##### Outputs
Sound Socket - Effected Sound

### Converter Nodes

### Sound to Float Node
The Sound to Float node converts sound to a Value based on a dropdown. 

##### Inputs
Sound Socket - Sound Input
Dropdown
Volume at Time
Sound Length
Time at Time

##### Outputs
Float Socket - Value

