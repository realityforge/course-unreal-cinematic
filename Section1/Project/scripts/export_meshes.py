import maya.cmds as cmds


def get_scene_short_name():
    '''Return the basename of the scene file.
    
    Returns:
        the basename of the scene file.
    '''

    # Get Full path of maya scene
    scene_filename = cmds.file(query=True, sceneName=True)
    # Get last part of the path
    local_scene_filename = scene_filename.split('/')[-1]
    size = len(local_scene_filename)
    # Remove ".mb" from the filename
    scene_short_name = local_scene_filename[:size - 3]
    return scene_short_name


def select_if_present(object_name):
    '''Check if object with that name exists and select it if present
    
    Args:
        object_name: the name of the object to select

    Returns:
        bool: True if node was selected, False otherwise
    '''

    try:
        cmds.select(object_name, replace=True)
        return True
    except:
        return False
    return True

def export_file_to_texture(base_directory, object_name):
    '''Export file to be textured in the place required for Substance Painter.
    
    Expects that the currently selected objects should be exported.

    '''
    filename = base_directory + "/" + object_name + "/" + object_name + ".obj"

    cmds.file(filename, force=True, options="groups=1;ptgroups=1;materials=0;smoothing=1;normals=1", type="OBJexport", preserveReferences=True, exportSelected=True)

cmds.select(clear=True)

scene_short_name = get_scene_short_name()
substance_painter_export_directory = "C:/Projects/course-unreal-cinematic/Section1/SubstancePainter/Assets/Import"

tile_name = scene_short_name + "Tile"
if select_if_present(tile_name):
    export_file_to_texture(substance_painter_export_directory, scene_short_name)
elif select_if_present(scene_short_name):
    export_file_to_texture(substance_painter_export_directory, scene_short_name)
else:
    raise Exception("Unable to identify object to export for texturing. No object named " + tile_name + " and no object named " + scene_short_name)
    

cmds.select(clear=True)
