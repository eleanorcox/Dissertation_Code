#################################################################
# Runs from inside Maya.
#################################################################
import maya.api.OpenMaya as OpenMaya
import maya.cmds as cmds
import maya.mel as mel
import socket
import json
import math

# Names of joints stored here
class Character():
    def __init__(self):
        self.root = getRootName()
        self.joints = getJointNames([self.root], self.root)

class AnimInfo():
    def __init__(self):
        self.anim_frames  = 0
        self.delta_stand  = 0.0          # Units, from experimentation
        self.delta_walk   = 800.0/500.0  # Units, from experimentation
        self.delta_jog    = 800.0/250.0  # Units, from experimentation
        self.delta_crouch = 800.0/602.0  # Units, from experimentation

class Buffer():
    def __init__(self):
        self.commands = []

    def clear(self):
        self.commands = []

########## Main function ##########

def main():
    # Retrieve appropriate data from scene
    request = doGet()

    # Open a socket to PFNN
    pfnn_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    pfnn_address = ("35.246.116.151", 54321) # google compute engine addr
    print("Connecting to PFNN: %s port %s" % pfnn_address)
    pfnn_sock.connect(pfnn_address)

    # Send request to PFNN
    print("Sending request to PFNN...")
    pfnn_sock.sendall(request)
    print("Awaiting response...")

    # Receive responses from PFNN
    all_responses = False
    responses = ""
    while not all_responses:
        resp = pfnn_sock.recv(4096)
        responses = responses + resp
        if '#' in resp:
            all_responses = True
    print("Response received. Closing socket to PFNN.\n")
    pfnn_sock.close()

    # Separate out and correctly format the responses
    responses = responses.replace("#", "")
    responses = responses.split('}')
    for i in range(len(responses)):
        responses[i] = responses[i] + '}'
    responses = responses[:-1]

    # Buffer each response then execute buffer
    for response in responses:
        json_response = json.loads(response)
        doBuff(json_response)

########## GET requests ##########

def doGet():
    # Get gait info
    path_gaits = getGait()
    # Get path info
    left_pos, path_pos, right_pos, path_dir = getPathPosDir(path_gaits)
    path_heights = getPathHeights(left_pos, path_pos, right_pos)
    # Get character info
    joint_pos = getJointPos()
    joint_vel = getJointVel()
    # Format as JSON
    response = formatGetJson(path_pos, path_dir, path_heights, joint_pos, joint_vel, path_gaits)
    return response

# TODO: full implementation from user input
def getGait():
    # For gait, 0=stand, 1=walk, 2=jog, 4=crouch, 5=jump, 6=unused (in pfnn)
    # Want gait at each point along path - i.e. at each frame

    gait = []
    path = getPathName()
    path_length = cmds.arclen(path)

    # TODO: HARDCODED for testing
    # frames_walking = (path_length/2.0) / anim_info.delta_walk
    # frames_standing = 300
    # frames_jogging  = (path_length/2.0) / anim_info.delta_jog
    frames_jogging  = path_length / anim_info.delta_jog
    anim_info.anim_frames = math.floor(frames_jogging)

    for i in range(int(anim_info.anim_frames)):
        gait.append(2)
    # for i in range(frames_standing):
    #     gait.append(0)
    # for i in range(int(frames_walking)):
    #     gait.append(1)



    # total_frames = frames_walking + frames_standing + frames_jogging
    # anim_info.anim_frames = total_frames

    return gait

# Returns four lists of WORLD SPACE coordinates:
# path_pos = [x, z] coordinates of points along the path
# left_pos/right_pos = [x, z] coordinates of points 25cm to the left/right of the path, used later in getPathHeights
# psth_dir = [dir x, dir z] pairs
def getPathPosDir(path_gaits):
    path = getPathName()
    unit = 25       # cm
    path_pos = []
    left_pos = []
    right_pos = []
    path_dir = []

    selectionList = OpenMaya.MSelectionList()
    selectionList.add(path)
    nodeDagPath = selectionList.getDagPath(0)
    path_curve = OpenMaya.MFnNurbsCurve(nodeDagPath)

    prev_param = 0
    path_length = path_curve.length()

    for i in range(int(anim_info.anim_frames)):
        if path_gaits[i] == 0:
            point_dist = anim_info.delta_stand
        if path_gaits[i] == 1:
            point_dist = anim_info.delta_walk / path_length
        if path_gaits[i] == 2:
            point_dist = anim_info.delta_jog / path_length
        if path_gaits[i] == 3:
            point_dist = anim_info.delta_crouch / path_length

        if i == 0:
            param = 0
        else:
            param = prev_param + point_dist
            if param > 1:
                param = 1

        paramm = path_curve.findParamFromLength(path_curve.length() * param)
        prev_param = param

        pos = cmds.pointOnCurve(path, parameter=paramm, position=True)
        path_pos.append([pos[0], pos[2]])

        tangent = cmds.pointOnCurve(path, parameter=paramm, normalizedTangent=True)
        path_dir.append([tangent[0], tangent[2]])

        normal = cmds.pointOnCurve(path, parameter=paramm, normalizedNormal=True)

        a_pos = [pos[0] + unit*normal[0], pos[1] + unit*normal[1], pos[2] + unit*normal[2]]
        b_pos = [pos[0] - unit*normal[0], pos[1] - unit*normal[1], pos[2] - unit*normal[2]]
        t_pos = [pos[0] + unit*tangent[0], pos[1] + unit*tangent[1], pos[2] + unit*tangent[2]]

        d = (a_pos[0] - pos[0])*(t_pos[2] - pos[2]) - (a_pos[2] - pos[2])*(t_pos[0] - pos[0])
        if d < 0:
            left_pos.append([b_pos[0], b_pos[2]])
            right_pos.append([a_pos[0], a_pos[2]])
        else:
            left_pos.append([a_pos[0], a_pos[2]])
            right_pos.append([b_pos[0], b_pos[2]])

    return left_pos, path_pos, right_pos, path_dir

# Returns a list of WORLD SPACE [r, c, l] heights of the left, central and right sample points of the path
def getPathHeights(left_pos, path_pos, right_pos):
    ground = getGroundName()

    selectionList = OpenMaya.MSelectionList()
    selectionList.add(ground)
    nodeDagPath = selectionList.getDagPath(0)
    mFnMesh = OpenMaya.MFnMesh(nodeDagPath)

    vtx_pos = getGroundVertexPositions(mFnMesh)
    tri_vtx_indx = getGroundTriangleIndices(mFnMesh)

    lpr_pos = [[left_pos[i], path_pos[i], right_pos[i]] for i in range(len(path_pos))]
    lpr_heights = []

    for i in range(len(lpr_pos)):
        point_heights = []
        for point in lpr_pos[i]:
            closest_vtx_index = getClosestVertexIndex(point, vtx_pos)
            closest_vtx_pos = vtx_pos[closest_vtx_index]
            on_vertex = point[0] == closest_vtx_pos[0] and point[1] == closest_vtx_pos[2]

            if not on_vertex:
                poss_tri = getPossibleTriangles(closest_vtx_index, tri_vtx_indx)
                height = interpolateHeight(point, poss_tri, vtx_pos)
            else:
                height = closest_vtx_pos[1]

            point_heights.append(height)
        lpr_heights.append(point_heights)

    return lpr_heights

# Returns a list of WORLD SPACE joint positions
def getJointPos():
    joints_pos = []

    for joint in character.joints:
        pos = cmds.xform(joint, worldSpace=True, query=True, translation=True)
        for i in range(len(pos)):
            joints_pos.append(pos[i])

    return joints_pos

# TODO: full implementation
# Returns a list of WORLD SPACE joint velocities
def getJointVel():
    velocities = []
    for i in range(len(character.joints)*3):
        velocities.append(0)
    return velocities

def formatGetJson(path_pos, path_dir, path_heights, joint_pos, joint_vel, path_gaits):
    response = json.dumps({"AnimFrames": anim_info.anim_frames,
                           "PathPos": path_pos,
                           "PathDir": path_dir,
                           "PathHeight": path_heights,
                           "JointPos": joint_pos,
                           "JointVel": joint_vel,
                           "Gait": path_gaits})
    return response

########## BUFF requests ##########

def doBuff(request):
    buffer.commands.append(request["JointPos"])

    # If last frame, execute buffer
    frame = request["Frame"]
    if frame == anim_info.anim_frames - 1:
        executeBuffer()

def executeBuffer():
    for i in range(len(buffer.commands)):
        setJointKeyframes()
        updateFrame()
        joint_pos = buffer.commands[i]
        moveJoints(joint_pos)
    setJointKeyframes()
    buffer.clear()

def setJointKeyframes():
    for joint in character.joints:
        cmds.setKeyframe(joint, attribute="translate")

def updateFrame():
    now = cmds.currentTime(query=True)
    cmds.currentTime(now + 1)

def moveJoints(joint_pos):
    for i in range(len(character.joints)):
        x_pos = joint_pos[i*3+0]
        y_pos = joint_pos[i*3+1]
        z_pos = joint_pos[i*3+2]
        cmds.move(x_pos, y_pos, z_pos, character.joints[i], worldSpace=True, preserveChildPosition=True)

def transform_joints(xforms):
    for i in range(len(character.joints)):
        # Choose joint
        selectionList = OpenMaya.MSelectionList()
        selectionList.add(character.joints[i])
        nodeDagPath = selectionList.getDagPath(0)
        mFnTransform = OpenMaya.MFnTransform(nodeDagPath)
        xform_matrix = mFnTransform.transformation().asMatrix()

        # New transformation matrix from pfnn
        transformation = OpenMaya.MMatrix(xforms[i])

        # Transform joint
        new_mat = xform_matrix * transformation     # In maya matrices are post-multiplied
        new_xform = OpenMaya.MTransformationMatrix(new_mat)
        mFnTransform.setTransformation(new_xform)

########## Helper functions ##########

### Joints ###

def getRootName():
    joints = cmds.ls(type='joint')
    root = joints[0]
    found = False

    while not found:
        parent = cmds.listRelatives(root, parent=True)
        if parent is not None:
            root = parent[0]
        elif parent is None:
            found = True
    return root

def getJointNames(joints, joint):
    children = cmds.listRelatives(joint)
    if children is not None:
        for child in children:
            joints.append(child)
            joints = getJointNames(joints, child)
    return joints

### Path ###

# TODO: get from user input
def getPathName():
    path = "curve1"     # Hardcoded
    return path

### Heights ###

# TODO: get from user input
def getGroundName():
    ground = "pPlane1"  # Hardcoded
    return ground

def getGroundVertexPositions(mFnMesh):
    space = OpenMaya.MSpace.kWorld
    vtx = mFnMesh.getPoints(space)

    vtx_pos = []
    for i in range(len(vtx)):
        vtx_pos.append([vtx[i].x, vtx[i].y, vtx[i].z])
    return vtx_pos

def getGroundTriangleIndices(mFnMesh):
    triangle_count, triangle_indices = mFnMesh.getTriangles()

    tri_vtx_indx = [triangle_indices[i:i + 3] for i in xrange(0, len(triangle_indices), 3)]
    return tri_vtx_indx

def getClosestVertexIndex(point, vertices):
    closest = -1
    shortest_dist = float('inf')
    for i in range(len(vertices)):
        xdist = (point[0] - vertices[i][0]) ** 2
        zdist = (point[1] - vertices[i][2]) ** 2
        euc_dist = math.sqrt(xdist + zdist)
        if euc_dist <= shortest_dist:
            closest = i
            shortest_dist = euc_dist
    return closest

def getPossibleTriangles(closest_vtx_index, tri_vtx_indx):
    possTriangles = []
    for i in range(len(tri_vtx_indx)):
        if closest_vtx_index in tri_vtx_indx[i]:
            possTriangles.append(tri_vtx_indx[i])
    return possTriangles

def interpolateHeight(point, poss_tri, vtx_pos):
    # Takes list of possible triangles point lies within and creates list of the world space coordinates of the vertices defining the triangles
    possible_triangles = []
    for tri in poss_tri:
        a_index = tri[0]
        b_index = tri[1]
        c_index = tri[2]
        possible_triangles.append([vtx_pos[a_index], vtx_pos[b_index], vtx_pos[c_index]])

    # Using barycetric coordinates, find which triangle the point lies in and interpolate to find the height of the point
    in_triangle = False
    for triangle in possible_triangles:
        A = triangle[0]
        B = triangle[1]
        C = triangle[2]
        P = point

        # TODO: make vectorsub function
        v0 = [C[0] - A[0], C[2] - A[2]]    # v0 = C-A
        v1 = [B[0] - A[0], B[2] - A[2]]    # v1 = B-A
        v2 = [P[0] - A[0], P[1] - A[2]]    # v2 = P-A

        # Dot product is commutative (for real numbers)
        dot00 = dotProduct2D(v0, v0)
        dot01 = dotProduct2D(v0, v1)
        dot02 = dotProduct2D(v0, v2)
        dot11 = dotProduct2D(v1, v1)
        dot12 = dotProduct2D(v1, v2)

        # Compute barycentric coordinates
        inv_denominator = 1 / float(dot00 * dot11 - dot01 * dot01)
        u = (dot11 * dot02 - dot01 * dot12) * inv_denominator
        v = (dot00 * dot12 - dot01 * dot02) * inv_denominator

        # Check if point is in triangle
        in_triangle = (u >= 0) and (v >= 0) and (u + v <= 1)
        if in_triangle:
            # Interpolate to find height
            height = A[1] + u*(C[1] - A[1]) + v*(B[1] - A[1])
            break

    return height

### Root Xform ###

def getRootXformPos():
    ### TODO: HARDCODED NAMES
    left_hip = "JOINT_LeftUpLeg"
    right_hip = "JOINT_RightUpLeg"
    l_hip_global_pos = cmds.xform(left_hip, worldSpace=True, query=True, translation=True)
    r_hip_global_pos = cmds.xform(right_hip, worldSpace=True, query=True, translation=True)

    mid_global_pos = [0,0,0]
    for i in range(len(l_hip_global_pos)):
        mid_global_pos[i] = (l_hip_global_pos[i] + r_hip_global_pos[i]) / 2

    root_x = mid_global_pos[0]
    root_y = 0                  # TODO: Hardcoded
    root_z = mid_global_pos[2]

    return [root_x, root_y, root_z]

def getRootXformDir():
    ### TODO: HARDCODED NAMES
    left_hip = "JOINT_LeftUpLeg"
    right_hip = "JOINT_RightUpLeg"
    left_shoulder = "JOINT_LeftArm"
    right_shoulder = "JOINT_RightArm"
    l_hip_global_pos = cmds.xform(left_hip, worldSpace=True, query=True, translation=True)
    r_hip_global_pos = cmds.xform(right_hip, worldSpace=True, query=True, translation=True)
    l_shoulder_global_pos = cmds.xform(left_shoulder, worldSpace=True, query=True, translation=True)
    r_shoulder_global_pos = cmds.xform(right_shoulder, worldSpace=True, query=True, translation=True)

    v1 = []    # vector between the hips
    v2 = []    # vector between the shoulders
    for i in range(3):
        v1.append(l_hip_global_pos[i] - r_hip_global_pos[i])
        v2.append(l_shoulder_global_pos[i] - r_shoulder_global_pos[i])

    v3 = []    # average of hip and shoulder vectors
    for i in range(3):
        v3.append((v1[i] + v2[i])/2)

    # Facing direction: cross product between v3 and upward direction (0,1,0)
    root_xform_dir = crossProduct3D(v3, [0, 1, 0])

    return root_xform_dir

### Other ###

def crossProduct3D(a, b):
    c = [a[1]*b[2] - a[2]*b[1],
         a[2]*b[0] - a[0]*b[2],
         a[0]*b[1] - a[1]*b[0]]
    return c

def dotProduct2D(a, b):
    dot = a[0]*b[0] + a[1]*b[1]
    return dot

########## Main ##########

if __name__ == "__main__":
    character = Character()
    buffer = Buffer()
    anim_info = AnimInfo()
    main()
