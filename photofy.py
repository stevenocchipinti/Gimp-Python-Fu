#!/usr/bin/env python

#   Python-Fu-Photofy - Makes the selected layer look like a printed photo
#
#   Copyright (C) 2011  Steven Occhipinti <StevenOcchipinti.com>
#   Creative Commons - Attribution 3.0 Unported (CC BY 3.0)
#   http://creativecommons.org/licenses/by/3.0/
#
#   This is my first attempt at a python-fu gimp plugin, so there are
#   a few hacks that I didn't know how to get around due to lack of
#   understanding. Also, this plugin is heavily commented so I can use
#   this an example for future attempts. A few note-worthy points are to
#   ensure the file is in ~/.gimp-2.6/plug-ins/ (with your particular
#   version of course) and is executable. 

from gimpfu import *

def photofy(image, layer, margin=50):

    # Separate contectual changes (brush, colors, etc.) from the user
    gimp.context_push()
    # Allow all these changes to apprear as 1 atomic action (1 undo)
    image.undo_group_start()

    # These commands were used while testing interactively
    #image = gimp.image_list()[0]
    #layer = pdb.gimp_image_get_active_layer(image)

    # Ensure black foreground (for stroking) and white background
    pdb.gimp_context_set_background('#FFF')
    pdb.gimp_context_set_foreground('#000')

    # Resize the layer and add a 50px white border
    pdb.gimp_layer_resize(layer, layer.width+(margin*2), 
                          layer.height+(margin*2), margin, margin)

    # Make the extra space (created from the resize) white 
    # (sometimes this doesnt need to be done.. redundant?)
    # Duplicate the layer
    layer2 = layer.copy()
    image.add_layer(layer2)
    pdb.gimp_image_lower_layer(image, layer2)
    # Fill with white and merge
    pdb.gimp_drawable_fill(layer2, 2)
    # Merge down with the new white layer 
    # Carry across the original layers name
    name = pdb.gimp_drawable_get_name(layer)
    layer = pdb.gimp_image_merge_down(image, layer, 0)
    pdb.gimp_drawable_set_name(layer, name)

    # To search for available brushes, use this with a string pattern:
    #num_brushes, brush_list = pdb.gimp_brushes_get_list("")
    #num_brushes, brush_list = pdb.gimp_brushes_get_list("circle")

    # Set the brush to a single pixel
    pdb.gimp_brushes_set_brush('Circle (01)')

    # Select all and assign the selection to a variable for later
    pdb.gimp_selection_all(image)
    selection = pdb.gimp_image_get_selection(image)

    # Stroking with a 2 pixel brush would put 1px on the inside of the
    # selection and 1px on the outside of the selection (We only care about the
    # inside of the selection) - but there is no 2px brush by default.
    # HACK: Stroking the selection with 1px will only pick the inside of the
    # selection on 2 of 4 sides, so to get the other 2 sides, flip the image
    # upside down and repeat the steps.
    # Flip 180 degrees, stroke, flip 180 degrees, stroke
    pdb.gimp_image_rotate(image, 1)
    pdb.gimp_edit_stroke(layer)
    pdb.gimp_image_rotate(image, 1)
    pdb.gimp_edit_stroke(layer)

    # Select none and drop a shadow (for the entire layer)
    pdb.gimp_selection_none(image)
    pdb.script_fu_drop_shadow(image, layer, 8, 8, 15, "#000", 80, 1)

    # Merge down with the new drop-shadow layer 
    # Carry across the original layers name
    name = pdb.gimp_drawable_get_name(layer)
    layer = pdb.gimp_image_merge_down(image, layer, 0)
    pdb.gimp_drawable_set_name(layer, name)

    # Leave the user in the same context they were in before
    image.undo_group_end()
    # Return the user to the context they were in before
    gimp.context_pop()

# ==============================================================================
# This puts the filter in the menu :)

register(
    "python-fu-photofy",
    "This will put a margin around the layer, stroke it and drop a shadow on it so it basically looks like a printed photo.",
    "Make the selected layer look like a printed photo",
    "Steven Occhipinti",
    "Steven Occhipinti",
    "2011",
    "P_hotofy...",
    "*",
    [
        (PF_IMAGE,    "image",      "Input image",      None),
        (PF_DRAWABLE, "drawable",   "Input drawable",   None),
        (PF_INT,      "margin",     "_Margin",          50)
    ],
    [],
    photofy,
    menu="<Image>/Filters/Artistic",
    )

main()
