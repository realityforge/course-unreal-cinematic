import maya.cmds as cmds

def transfer_animation(source_object, target_object, cut: bool = False):
    """Transfer animations from a source object to a target object.

    :param source_object: the object to transfer animations from.
    :param target_object: the object to transfer animations to.
    :param cut: True if the transfer should remove the animations from the source object, False if they should remain on the source object
    :return: None
    """
    if cut:
        cmds.cutKey(source_object, animation='objects', option='keys')
    else:
        cmds.copyKey(source_object, animation='objects', option='keys')
    cmds.pasteKey(target_object, animation='objects', option='keys')
