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


def setup_world_offset_control(target, target_parent=None):
    """Create the rig setup for a separate "World Offset Control" for the specified target object

    :param target: the object that will be driven by this control
    :param target_parent: the parent of the target that the "World Offset Control" group will be constrained to if specified
    :return: the name of the locator/control
    """
    # Note: That this was mostly inspired by https://www.youtube.com/watch?v=Ci3ve3_nkfA&list=PLydvFUGQqgRj3_uCmIGp9jC8wnRrqDy8B

    # Create the objects
    locator_name = cmds.spaceLocator(name='{}_loc'.format(target))[0]
    offset_locator_name = cmds.spaceLocator(name='{}_loc_world_offset'.format(target))[0]
    group_name = cmds.grp(name='{}_loc_grp'.format(target), empty=True)

    # Setup hierarchy
    # Note: Params are ordered child, parent
    cmds.parent(locator_name, offset_locator_name)
    cmds.parent(offset_locator_name, group_name)

    # Move the group to the location of target by using the trick of creating a
    # parent constraint and removing it
    parent_constraint_name = cmds.parentConstraint(target, group_name, maintainOffset=False)[0]
    cmds.delete(parent_constraint_name)

    # if the target has a parent that we should be constrained to then make it so
    if target_parent:
        # Note: Params are ordered driver, driven
        cmds.parentConstraint(target_parent, group_name)
        cmds.scaleConstraint(target_parent, group_name)

    # Transfer animations from the target to the newly created locator
    # as we are about to drive the target from the locator
    transfer_animation(target, locator_name, cut=True)

    # Constraint the target object to the locator
    # Note: Params are ordered - driver, driven
    cmds.parentConstraint(locator_name, target)
    cmds.scaleConstraint(locator_name, target)
