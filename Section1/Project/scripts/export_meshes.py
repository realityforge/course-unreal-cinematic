import maya.mel as mel
import maya.cmds as cmds
import json

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

    _selected = cmds.ls(selection=True,shortNames=True)
    print(_selected)

    _matched = polyCleanup(allMeshes = False, selectOnly = True)
    if 0 != len(_matched):
        raise Exception("Unable to export object " + object_name + " to '" + filename + "' for Substance Painter as the object has " + str(len(_matched)) + " components that need cleaning up.")

    # Select object again as cleanup identified no isssues
    cmds.select(_selected, replace=True)
    
    cmds.file(filename, force=True, options="groups=1;ptgroups=1;materials=0;smoothing=1;normals=1", type="OBJexport", preserveReferences=False, exportSelected=True)
    
    return filename

def export_file_to_unreal(base_directory, object_name):
    '''Export file to be imported into Unreal in the place required for Substance Painter.
    
    Expects that the currently selected objects should be exported.
    '''
    filename = base_directory + "/" + object_name + "/SM_" + object_name + ".fbx"

    _selected = cmds.ls(selection=True,shortNames=True)

    _matched = polyCleanup(allMeshes = False, selectOnly = True)
    if 0 != len(_matched):
        raise Exception("Unable to export object " + object_name + " to '" + filename + "' for Unreal as the object has " + str(len(_matched)) + " components that need cleaning up.")

    # Select object again as cleanup identified no isssues
    cmds.select(_selected, replace=True)
    

    # get current user settings for FBX export and store them
    mel.eval('FBXPushSettings')
    try:
        # This ensures the user’s settings are ignored.
        mel.eval("FBXResetExport") 

        # FBX version FBX202000 | FBX201900 | FBX201800 | FBX201600 | FBX201400 | FBX201300 | FBX201200 | FBX201100 | FBX201000 | FBX200900 | FBX200611
        mel.eval('FBXExportFileVersion -v FBX202000')  
                
        mel.eval("FBXExportUpAxis y")
        
        # "Smoothing Groups" option - Required for correct behaviour in Unreal (?)
        mel.eval("FBXExportSmoothingGroups -v true")

        # "Tangent and Binormals" option - yes export this and make sure we import it back in Unrela
        mel.eval("FBXExportTangents -v true")

        # "Smooth Mesh" option - Export the subdivided version of the mesh
        mel.eval("FBXExportSmoothMesh -v true")

        # "Preserve Instances" option - Don't, convert instances into regular geometry
        mel.eval("FBXExportInstances -v false")
        
        # "Split per-vertex Binormals" option - should not be needed and can change UVs
        mel.eval("FBXExportHardEdges -v false")
        
        # "Reference Assets Content" option
        mel.eval("FBXExportReferencedAssetsContent -v false")
        
        # Do NOT Embed Media
        mel.eval("FBXExportEmbeddedTextures -v false")
        # No Connections
        mel.eval("FBXExportInputConnections -v false")        
        # No Constraints
        mel.eval("FBXExportConstraints -v false")
        # No Cameras
        mel.eval("FBXExportCameras -v false")
        # No Lights
        mel.eval("FBXExportLights -v false")
        
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
        mel.eval('FBXPopSettings')
        
    return filename


def export_files():
    '''Export files required for Substance Painter and Unreal.
    
    The export process will remove the current selection, bake history and perform the export.
    '''
    cmds.SelectFacetMask()
    cmds.select(clear=True)
    cmds.selectMode(component=True)
    cmds.select(clear=True)
    cmds.selectMode(object=True)
    cmds.select(clear=True)

    scene_short_name = get_scene_short_name()
    
    model_repository_filename = "scenes/model_repository.json"

    model_repository_data = load_json_data(model_repository_filename)
    substance_painter_dir = require_json_value(model_repository_filename, model_repository_data, "Substance Painter Asset Directory", "substance_painter", "dir")
    unreal_export_dir = require_json_value(model_repository_filename, model_repository_data, "Unreal Import Directory", "unreal", "dir")
    
    substance_painter_export_directory = cmds.workspace(expandName = substance_painter_dir)
    unreal_export_directory = cmds.workspace(expandName = unreal_export_dir)
    
    scenes_data = model_repository_data["scenes"] if None != model_repository_data["scenes"] else []
    scene_data = scenes_data[scene_short_name] if None != scenes_data[scene_short_name] else []
    unreal_section_data = scene_data["unreal"] if None != scene_data["unreal"] else []
    unreal_object_name = unreal_section_data["object"] if None != unreal_section_data["object"] else scene_short_name
    sp_section_data = scene_data["substance_painter"] if None != scene_data["substance_painter"] else []
    substance_painter_object_name = sp_section_data["object"] if None != sp_section_data["object"] else unreal_object_name

    cmds.bakePartialHistory(all = True, prePostDeformers = True)
    
    substance_painter_filename = None
    if select_if_present(substance_painter_object_name):
        substance_painter_filename = export_file_to_substance_painter(substance_painter_export_directory, scene_short_name)
    else:
        raise Exception("Unable to identify object to export for texturing. No object named " + substance_painter_object_name)

    unreal_filename = None
    if select_if_present(scene_short_name):
        unreal_filename = export_file_to_unreal(unreal_export_directory, scene_short_name)
    else:
        raise Exception("Unable to identify object to export for import into Unreal. No object named " + scene_short_name)


    print("\n")

    if substance_painter_filename:
        print("Exported {} for texturing in SubstancePainter".format(substance_painter_filename))

    if unreal_filename:
        print("Exported {} for use in Unreal".format(unreal_filename))

    cmds.select(clear=True)

def load_json_data(filename):
    '''Load json data as dictionary from filename.
    
    The filename is relative to the project or absolute.
    
    Args:
        filename: the name of the file to load

    Returns:
        dictionary|None: Dictionary if loaded, false otherwise
    '''
    qualified_filename = cmds.workspace(expandName = filename)
    with open(qualified_filename, "r") as file: 
        try:
            return json.load(file)
        except Exception as e:
            raise Exception("Unable to load json from filename '" + filename + "' resolved to '" + qualified_filename + "' due to " + str(e))

def require_json_value(filename, data, label, primary_key, secondary_key):
    '''Extract a value from json that is expected to be present.
    
    Args:
        filename: the name of the file which the json was loaded
        data: the json data in Dictionary form
        label: the human oriented description of the property
        primary_key: the name of the top level object to return
        secondary_key: the name of the property to return

    Returns:
        the value of the property
    '''
    if None != data[primary_key] and None != data[primary_key][secondary_key]:
        return data[primary_key][secondary_key]
    else:
        raise Exception("Unable to extract " + label + " from configuration file " + filename + ". No json property named " + primary_key + "." + secondary_key + ".")

def polyCleanup(allMeshes, selectOnly, historyOn = False, quads = False, nsided = True, concave = True, holed = True, nonplanar = False, zeroGeom = True, zeroGeomTol = 0.000010, zeroEdge = True, zeroEdgeTol = 0.000010, zeroMap = True, zeroMapTol = 0.000010, sharedUVs = False, nonmanifold = True, lamina = True, invalidComponents = False):
    '''Run the cleanup command on polygonal meshes
    
    Args:
		allMeshes : Run on all selectable meshes or only the currently selected?
		selectOnly : Should cleanup occur or should we just select matched components?
		historyOn : Keep construction history if we have chose to cleanup rather than select

		quads : match quad faces
		nsided : match 4+-sided faces
		nonplanar : match non-planar faces
		holed : match faces with holes
		concave : match concave faces

		zeroGeom : match 0 area faces
		zeroGeomTol : tolerance for face areas
		zeroEdge : match 0 length edges
		zeroEdgeTol : tolerance for edge length
		zeroMap : match 0 uv face area 
		zeroMapTol : tolerance for uv face areas
        
        sharedUVs: Match uvs that are shared across vertices
        nonmanifold: Match nonmanifold faces (0 = Do not match, 1 means Geometry and Normals, 2 means Geometry Only)
        
        lamina: Match lamina faces
        invalidComponents: Match invalid components

    Returns:
        list of items selected or cleaned up. None if none
    '''
    
    _allMeshes = '1' if allMeshes else '0'
    _selectOnly = '2' if selectOnly else '0'
    _historyOn = '1' if historyOn else '0'
    _quads = '1' if quads else '0'
    _nsided = '1' if nsided else '0'
    _nonplanar = '1' if nonplanar else '0'
    _holed = '1' if holed else '0'
    _concave = '1' if concave else '0'
    _zeroGeom = '1' if zeroGeom else '0'
    _zeroEdge = '1' if zeroEdge else '0'
    _zeroMap = '1' if zeroMap else '0'
    _sharedUVs = '1' if sharedUVs else '0'
    _nonmanifold = '1' if nonmanifold else '0'
    _lamina = '1' if lamina else '0'
    _invalidComponents = '1' if invalidComponents else '0'
    
    _args = '"{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}"'.format(_allMeshes, _selectOnly, _historyOn, _quads, _nsided, _concave, _holed, _nonplanar, _zeroGeom, zeroGeomTol, _zeroEdge, zeroEdgeTol, _zeroMap, zeroMapTol, _sharedUVs, _nonmanifold, _lamina, _invalidComponents)
    return mel.eval('polyCleanupArgList 4 { ' + _args + ' }')
