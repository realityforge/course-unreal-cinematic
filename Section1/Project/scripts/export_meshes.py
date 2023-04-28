import maya.mel as mel
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

def export_file_to_substance_painter(base_directory, object_name):
    '''Export file to be textured in the place required for Substance Painter.
    
    Expects that the currently selected objects should be exported.
    '''
    filename = base_directory + "/" + object_name + "/" + object_name + ".obj"

    cmds.file(filename, force=True, options="groups=1;ptgroups=1;materials=0;smoothing=1;normals=1", type="OBJexport", preserveReferences=False, exportSelected=True)
    
    return filename

def export_file_to_unreal(base_directory, object_name):
    '''Export file to be imported into Unreal in the place required for Substance Painter.

    Expects that the currently selected objects should be exported.
    '''
    filename = base_directory + "/" + object_name + "/SM_" + object_name + ".fbx"

    # get current user settings for FBX export and store them
    mel.eval('FBXPushSettings;')
    try:
        # This ensures the user’s settings are ignored.
        mel.eval("FBXResetExport") 

        # FBX version FBX202000 | FBX201900 | FBX201800 | FBX201600 | FBX201400 | FBX201300 | FBX201200 | FBX201100 | FBX201000 | FBX200900 | FBX200611
        mel.eval('FBXExportFileVersion -v FBX202000')  
                
        # do not export subdivision version
        mel.eval("FBXExportSmoothMesh -v false")
        
        mel.eval("FBXExportUpAxis y")
        
        # Required for correct behaviour in Unreal (?)
        mel.eval("FBXExportSmoothingGroups -v true")
        
        # No need for a log
        mel.eval('FBXExportGenerateLog -v false')
        
        try:
            # Export selected object
            mel.eval('FBXExport -f "{}" -s'.format(filename))
        except Exception as e:
            sys.stdout.write(str(e) + '\n')
            return None
            
    finally:
        # set user-defined FBX settings back after export
        mel.eval('FBXPopSettings;')

    return filename

def export_files(workspace_relative_substance_dir, workspace_relative_unreal_dir):
    '''Export files required for Substance Painter and Unreal.

    The export process will remove the current selection, bake history and perform the export.
    '''
    cmds.select(clear=True)

    scene_short_name = get_scene_short_name()
    substance_painter_export_directory = cmds.workspace(expandName = workspace_relative_substance_dir)
    unreal_export_directory = cmds.workspace(expandName = workspace_relative_unreal_dir)

    cmds.bakePartialHistory(all = True, prePostDeformers = True)

    substance_painter_filename = None
    if select_if_present(scene_short_name + "Tile"):
        substance_painter_filename = export_file_to_substance_painter(substance_painter_export_directory, scene_short_name)
    elif select_if_present(scene_short_name):
        substance_painter_filename = export_file_to_substance_painter(substance_painter_export_directory, scene_short_name)
    else:
        raise Exception("Unable to identify object to export for texturing. No object named " + tile_name + " and no object named " + scene_short_name)

    if not select_if_present(scene_short_name):
        raise Exception("Unable to identify object to export for import into Unreal. No object named " + scene_short_name)

    unreal_filename =export_file_to_unreal(unreal_export_directory, scene_short_name)

    print("\n")

    if substance_painter_filename:
        print("Exported {} for texturing in SubstancePainter".format(substance_painter_filename))

    if unreal_filename:
        print("Exported {} for use in Unreal".format(unreal_filename))


    cmds.select(clear=True)
