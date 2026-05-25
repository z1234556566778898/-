import math
import os
from mathutils import Euler
import bpy


def deselect_all():
    for o in bpy.context.selected_objects:
        o.select_set(False)


def delete_all():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for block in (
        bpy.data.meshes,
        bpy.data.materials,
        bpy.data.images,
        bpy.data.armatures,
        bpy.data.actions,
    ):
        for b in list(block):
            if b.users == 0:
                block.remove(b)


def ensure_scene():
    scn = bpy.context.scene
    scn.render.fps = 24
    scn.unit_settings.system = "METRIC"
    scn.unit_settings.scale_length = 1.0
    scn.frame_start = 1
    scn.frame_end = 240


def mat(name, base_color, rough=0.55, metallic=0.1, alpha=1.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*base_color, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metallic
    if alpha < 1.0:
        bsdf.inputs["Alpha"].default_value = alpha
        m.blend_method = "BLEND"
    return m


def add(obj, m):
    if obj.data.materials:
        obj.data.materials[0] = m
    else:
        obj.data.materials.append(m)


def join(objs, name):
    deselect_all()
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    objs[0].name = name
    return objs[0]


def primitive(kind, **kwargs):
    if kind == "sphere":
        bpy.ops.mesh.primitive_uv_sphere_add(**kwargs)
    elif kind == "cylinder":
        bpy.ops.mesh.primitive_cylinder_add(**kwargs)
    elif kind == "capsule":
        bpy.ops.mesh.primitive_capsule_add(**kwargs)
    elif kind == "cube":
        bpy.ops.mesh.primitive_cube_add(**kwargs)
    elif kind == "cone":
        bpy.ops.mesh.primitive_cone_add(**kwargs)
    else:
        raise ValueError(kind)
    return bpy.context.active_object


def make_astronaut_mesh():
    m_suit = mat("Suit", (0.93, 0.95, 0.98), rough=0.75, metallic=0.05)
    m_trim = mat("Trim", (0.22, 0.36, 0.95), rough=0.4, metallic=0.2)
    m_black = mat("Black", (0.08, 0.09, 0.10), rough=0.65, metallic=0.0)
    m_glass = mat("Glass", (0.55, 0.82, 1.0), rough=0.12, metallic=0.0, alpha=0.22)
    m_gold = mat("Gold", (1.0, 0.78, 0.32), rough=0.2, metallic=0.85)

    body = []

    head = primitive("sphere", radius=0.23, location=(0, 0, 1.18))
    add(head, m_suit)
    body.append(head)

    helmet = primitive("sphere", radius=0.26, location=(0, 0, 1.18))
    add(helmet, m_trim)
    body.append(helmet)

    visor = primitive("sphere", radius=0.205, location=(0.085, 0, 1.175))
    visor.scale = (0.6, 0.82, 0.62)
    add(visor, m_glass)
    body.append(visor)

    backpack = primitive("cube", size=0.28, location=(-0.13, 0, 1.0))
    backpack.scale = (0.55, 0.65, 0.9)
    add(backpack, m_black)
    body.append(backpack)

    torso = primitive("capsule", radius=0.18, depth=0.42, location=(0, 0, 0.93))
    torso.scale = (1.0, 0.88, 1.05)
    add(torso, m_suit)
    body.append(torso)

    chest = primitive("cube", size=0.18, location=(0.13, 0, 0.98))
    chest.scale = (0.75, 0.55, 0.55)
    add(chest, m_black)
    body.append(chest)

    badge = primitive("cube", size=0.11, location=(0.14, 0.07, 1.02))
    badge.scale = (0.5, 0.25, 0.25)
    add(badge, m_gold)
    body.append(badge)

    belt = primitive("cylinder", radius=0.18, depth=0.06, location=(0, 0, 0.77))
    belt.scale = (1.02, 1.02, 1.0)
    add(belt, m_trim)
    body.append(belt)

    hip = primitive("capsule", radius=0.16, depth=0.24, location=(0, 0, 0.66))
    hip.scale = (1.0, 0.92, 1.0)
    add(hip, m_suit)
    body.append(hip)

    def limb_capsule(radius, depth, loc, rot, scale=(1, 1, 1), material=None):
        o = primitive("capsule", radius=radius, depth=depth, location=loc, rotation=rot)
        o.scale = scale
        add(o, material or m_suit)
        return o

    arm_l_u = limb_capsule(0.07, 0.22, (0.0, 0.22, 1.01), (0, math.radians(90), 0), scale=(1.0, 1.0, 1.0))
    arm_l_u.location = (0.0, 0.22, 1.01)
    arm_l_u.rotation_euler = Euler((0, math.radians(90), math.radians(90)))
    body.append(arm_l_u)

    arm_l_f = limb_capsule(0.065, 0.22, (0.0, 0.35, 0.89), (0, 0, 0))
    arm_l_f.rotation_euler = Euler((0, math.radians(90), math.radians(90)))
    arm_l_f.location = (0.0, 0.35, 0.89)
    body.append(arm_l_f)

    glove_l = primitive("sphere", radius=0.075, location=(0.0, 0.44, 0.82))
    add(glove_l, m_trim)
    body.append(glove_l)

    arm_r_u = limb_capsule(0.07, 0.22, (0.0, -0.22, 1.01), (0, 0, 0))
    arm_r_u.rotation_euler = Euler((0, math.radians(90), math.radians(-90)))
    arm_r_u.location = (0.0, -0.22, 1.01)
    body.append(arm_r_u)

    arm_r_f = limb_capsule(0.065, 0.22, (0.0, -0.35, 0.89), (0, 0, 0))
    arm_r_f.rotation_euler = Euler((0, math.radians(90), math.radians(-90)))
    arm_r_f.location = (0.0, -0.35, 0.89)
    body.append(arm_r_f)

    glove_r = primitive("sphere", radius=0.075, location=(0.0, -0.44, 0.82))
    add(glove_r, m_trim)
    body.append(glove_r)

    leg_l_u = limb_capsule(0.08, 0.24, (0.0, 0.10, 0.52), (0, 0, 0))
    leg_l_u.rotation_euler = Euler((0, math.radians(90), 0))
    body.append(leg_l_u)

    leg_l_s = limb_capsule(0.075, 0.26, (0.0, 0.10, 0.32), (0, 0, 0))
    leg_l_s.rotation_euler = Euler((0, math.radians(90), 0))
    body.append(leg_l_s)

    boot_l = primitive("cube", size=0.16, location=(0.07, 0.10, 0.17))
    boot_l.scale = (0.8, 0.6, 0.35)
    add(boot_l, m_black)
    body.append(boot_l)

    leg_r_u = limb_capsule(0.08, 0.24, (0.0, -0.10, 0.52), (0, 0, 0))
    leg_r_u.rotation_euler = Euler((0, math.radians(90), 0))
    body.append(leg_r_u)

    leg_r_s = limb_capsule(0.075, 0.26, (0.0, -0.10, 0.32), (0, 0, 0))
    leg_r_s.rotation_euler = Euler((0, math.radians(90), 0))
    body.append(leg_r_s)

    boot_r = primitive("cube", size=0.16, location=(0.07, -0.10, 0.17))
    boot_r.scale = (0.8, 0.6, 0.35)
    add(boot_r, m_black)
    body.append(boot_r)

    mesh = join(body, "Astronaut_Mesh")
    bpy.ops.object.shade_smooth()
    mesh.data.use_auto_smooth = True
    mesh.data.auto_smooth_angle = math.radians(55)
    return mesh


def make_armature():
    bpy.ops.object.armature_add(enter_editmode=True, location=(0, 0, 0.9))
    arm = bpy.context.active_object
    arm.name = "Astronaut_Rig"
    amt = arm.data
    amt.name = "Astronaut_RigData"
    eb = amt.edit_bones
    root = eb[0]
    root.name = "root"
    root.head = (0, 0, 0.85)
    root.tail = (0, 0, 0.95)

    spine = eb.new("spine")
    spine.head = root.tail
    spine.tail = (0, 0, 1.12)
    spine.parent = root

    head = eb.new("head")
    head.head = spine.tail
    head.tail = (0, 0, 1.33)
    head.parent = spine

    ua_l = eb.new("upper_arm.L")
    ua_l.head = (0, 0.16, 1.06)
    ua_l.tail = (0, 0.34, 1.00)
    ua_l.parent = spine

    fa_l = eb.new("forearm.L")
    fa_l.head = ua_l.tail
    fa_l.tail = (0, 0.45, 0.84)
    fa_l.parent = ua_l

    ua_r = eb.new("upper_arm.R")
    ua_r.head = (0, -0.16, 1.06)
    ua_r.tail = (0, -0.34, 1.00)
    ua_r.parent = spine

    fa_r = eb.new("forearm.R")
    fa_r.head = ua_r.tail
    fa_r.tail = (0, -0.45, 0.84)
    fa_r.parent = ua_r

    th_l = eb.new("thigh.L")
    th_l.head = (0, 0.09, 0.72)
    th_l.tail = (0, 0.09, 0.45)
    th_l.parent = root

    sh_l = eb.new("shin.L")
    sh_l.head = th_l.tail
    sh_l.tail = (0, 0.09, 0.18)
    sh_l.parent = th_l

    th_r = eb.new("thigh.R")
    th_r.head = (0, -0.09, 0.72)
    th_r.tail = (0, -0.09, 0.45)
    th_r.parent = root

    sh_r = eb.new("shin.R")
    sh_r.head = th_r.tail
    sh_r.tail = (0, -0.09, 0.18)
    sh_r.parent = th_r

    bpy.ops.object.mode_set(mode="OBJECT")
    return arm


def bind(mesh, arm):
    deselect_all()
    mesh.select_set(True)
    arm.select_set(True)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.parent_set(type="ARMATURE_AUTO")
    mod = mesh.modifiers.get("Armature")
    if mod:
        mod.use_deform_preserve_volume = True


def set_pose(arm, bone, rot=None, loc=None):
    pb = arm.pose.bones[bone]
    pb.rotation_mode = "XYZ"
    if rot is not None:
        pb.rotation_euler = Euler(rot, "XYZ")
    if loc is not None:
        pb.location = loc


def key(arm, frame, bones):
    bpy.context.scene.frame_set(frame)
    for b in bones:
        pb = arm.pose.bones[b]
        pb.keyframe_insert(data_path="rotation_euler", frame=frame)
        pb.keyframe_insert(data_path="location", frame=frame)


def make_action(arm, name, start, end):
    act = bpy.data.actions.new(name)
    arm.animation_data_create()
    arm.animation_data.action = act
    bpy.context.scene.frame_start = min(bpy.context.scene.frame_start, start)
    bpy.context.scene.frame_end = max(bpy.context.scene.frame_end, end)
    return act


def clear_pose(arm):
    for pb in arm.pose.bones:
        pb.location = (0, 0, 0)
        pb.rotation_mode = "XYZ"
        pb.rotation_euler = (0, 0, 0)


def build_animations(arm):
    bones = ["root", "spine", "head", "upper_arm.L", "forearm.L", "upper_arm.R", "forearm.R", "thigh.L", "shin.L", "thigh.R", "shin.R"]

    def idle():
        make_action(arm, "Idle", 1, 48)
        clear_pose(arm)
        set_pose(arm, "spine", rot=(math.radians(2), 0, 0))
        set_pose(arm, "head", rot=(math.radians(-2), 0, 0))
        key(arm, 1, bones)
        set_pose(arm, "spine", rot=(math.radians(-2), 0, 0))
        set_pose(arm, "head", rot=(math.radians(2), 0, 0))
        key(arm, 24, bones)
        set_pose(arm, "spine", rot=(math.radians(2), 0, 0))
        set_pose(arm, "head", rot=(math.radians(-2), 0, 0))
        key(arm, 48, bones)

    def walk():
        make_action(arm, "Walk", 60, 108)
        clear_pose(arm)
        set_pose(arm, "upper_arm.L", rot=(0, 0, math.radians(18)))
        set_pose(arm, "upper_arm.R", rot=(0, 0, math.radians(-18)))
        set_pose(arm, "thigh.L", rot=(math.radians(25), 0, 0))
        set_pose(arm, "shin.L", rot=(math.radians(-12), 0, 0))
        set_pose(arm, "thigh.R", rot=(math.radians(-25), 0, 0))
        set_pose(arm, "shin.R", rot=(math.radians(12), 0, 0))
        key(arm, 60, bones)

        set_pose(arm, "upper_arm.L", rot=(0, 0, math.radians(-18)))
        set_pose(arm, "upper_arm.R", rot=(0, 0, math.radians(18)))
        set_pose(arm, "thigh.L", rot=(math.radians(-25), 0, 0))
        set_pose(arm, "shin.L", rot=(math.radians(12), 0, 0))
        set_pose(arm, "thigh.R", rot=(math.radians(25), 0, 0))
        set_pose(arm, "shin.R", rot=(math.radians(-12), 0, 0))
        key(arm, 84, bones)

        set_pose(arm, "upper_arm.L", rot=(0, 0, math.radians(18)))
        set_pose(arm, "upper_arm.R", rot=(0, 0, math.radians(-18)))
        set_pose(arm, "thigh.L", rot=(math.radians(25), 0, 0))
        set_pose(arm, "shin.L", rot=(math.radians(-12), 0, 0))
        set_pose(arm, "thigh.R", rot=(math.radians(-25), 0, 0))
        set_pose(arm, "shin.R", rot=(math.radians(12), 0, 0))
        key(arm, 108, bones)

    def run():
        make_action(arm, "Run", 120, 156)
        clear_pose(arm)
        set_pose(arm, "spine", rot=(math.radians(-4), 0, 0))
        set_pose(arm, "upper_arm.L", rot=(0, 0, math.radians(30)))
        set_pose(arm, "upper_arm.R", rot=(0, 0, math.radians(-30)))
        set_pose(arm, "thigh.L", rot=(math.radians(42), 0, 0))
        set_pose(arm, "shin.L", rot=(math.radians(-20), 0, 0))
        set_pose(arm, "thigh.R", rot=(math.radians(-42), 0, 0))
        set_pose(arm, "shin.R", rot=(math.radians(20), 0, 0))
        key(arm, 120, bones)

        set_pose(arm, "upper_arm.L", rot=(0, 0, math.radians(-30)))
        set_pose(arm, "upper_arm.R", rot=(0, 0, math.radians(30)))
        set_pose(arm, "thigh.L", rot=(math.radians(-42), 0, 0))
        set_pose(arm, "shin.L", rot=(math.radians(20), 0, 0))
        set_pose(arm, "thigh.R", rot=(math.radians(42), 0, 0))
        set_pose(arm, "shin.R", rot=(math.radians(-20), 0, 0))
        key(arm, 138, bones)

        set_pose(arm, "upper_arm.L", rot=(0, 0, math.radians(30)))
        set_pose(arm, "upper_arm.R", rot=(0, 0, math.radians(-30)))
        set_pose(arm, "thigh.L", rot=(math.radians(42), 0, 0))
        set_pose(arm, "shin.L", rot=(math.radians(-20), 0, 0))
        set_pose(arm, "thigh.R", rot=(math.radians(-42), 0, 0))
        set_pose(arm, "shin.R", rot=(math.radians(20), 0, 0))
        key(arm, 156, bones)

    def attack():
        make_action(arm, "Attack", 168, 204)
        clear_pose(arm)
        set_pose(arm, "upper_arm.R", rot=(math.radians(10), 0, math.radians(-10)))
        set_pose(arm, "forearm.R", rot=(math.radians(-20), 0, 0))
        key(arm, 168, bones)
        set_pose(arm, "upper_arm.R", rot=(math.radians(-10), 0, math.radians(-110)))
        set_pose(arm, "forearm.R", rot=(math.radians(18), 0, 0))
        set_pose(arm, "spine", rot=(0, 0, math.radians(-10)))
        key(arm, 186, bones)
        clear_pose(arm)
        key(arm, 204, bones)

    def hit():
        make_action(arm, "Hit", 210, 228)
        clear_pose(arm)
        key(arm, 210, bones)
        set_pose(arm, "spine", rot=(math.radians(6), 0, math.radians(12)))
        set_pose(arm, "head", rot=(math.radians(-6), 0, math.radians(-12)))
        key(arm, 219, bones)
        clear_pose(arm)
        key(arm, 228, bones)

    def death():
        make_action(arm, "Death", 234, 270)
        clear_pose(arm)
        key(arm, 234, bones)
        set_pose(arm, "root", rot=(0, math.radians(30), math.radians(80)), loc=(0, 0, -0.25))
        set_pose(arm, "spine", rot=(math.radians(-10), 0, 0))
        set_pose(arm, "head", rot=(math.radians(10), 0, 0))
        set_pose(arm, "upper_arm.L", rot=(0, 0, math.radians(60)))
        set_pose(arm, "upper_arm.R", rot=(0, 0, math.radians(-60)))
        set_pose(arm, "thigh.L", rot=(math.radians(12), 0, 0))
        set_pose(arm, "thigh.R", rot=(math.radians(-12), 0, 0))
        key(arm, 270, bones)

    idle()
    walk()
    run()
    attack()
    hit()
    death()


def add_nla_tracks(arm):
    if not arm.animation_data:
        arm.animation_data_create()
    if not arm.animation_data.nla_tracks:
        arm.animation_data.nla_tracks.new()
    for act in bpy.data.actions:
        if act.name in {"Idle", "Walk", "Run", "Attack", "Hit", "Death"}:
            tr = arm.animation_data.nla_tracks.new()
            tr.name = act.name
            strip = tr.strips.new(act.name, 1, act)
            strip.action_frame_start = act.frame_range[0]
            strip.action_frame_end = act.frame_range[1]


def export_glb(path):
    deselect_all()
    for o in bpy.context.scene.objects:
        if o.type in {"MESH", "ARMATURE"} and (o.name.startswith("Astronaut_") or o.name == "Astronaut_Rig"):
            o.select_set(True)
    bpy.ops.export_scene.gltf(
        filepath=path,
        export_format="GLB",
        export_yup=True,
        export_apply=True,
        export_animations=True,
        export_animation_mode="ACTIONS",
        export_nla_strips=True,
        use_selection=True,
    )


def main():
    delete_all()
    ensure_scene()

    mesh = make_astronaut_mesh()
    arm = make_armature()
    bind(mesh, arm)

    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="POSE")
    build_animations(arm)
    bpy.ops.object.mode_set(mode="OBJECT")
    add_nla_tracks(arm)

    out = os.path.join(os.path.expanduser("~"), "Desktop", "Astronaut_Chibi.glb")
    export_glb(out)
    print(out)


main()

