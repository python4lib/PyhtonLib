"""
Creates a duplicate model of the current selection with the polygons separated
at the UV seams.  It then creates and attaches a blendshape to the new mesh
and shapes the geometry to match the mesh's UV layout.
"""

__author__ = 'Chris Lewis'
__version__ = '0.8.0'
__email__ = 'clewis1@c.ringling.edu'

from pymel.api import *
from pymel.core import *
from pymel.core.nodetypes import *

def createMesh(verts, faces, uvs=None, name='polySurface', meshParent=None):
    """Create a mesh with custom vertices, faces, and UVs.

    verts -- a list of 3D points
    faces -- a list of faces, which are lists of vertex indices
    uvs -- a list of UV tuples for each face vertex
    name -- the name of the mesh transform
    meshParent -- the node to parent the mesh transform to

    Example:
    # creates a cube
    createMesh(
        [
            [-1,-1,-1], [1,-1,-1], [1,-1,1], [-1,-1,1],
            [-1,1,-1], [-1,1,1], [1,1,1], [1,1,-1]
        ],
        [
            [0, 1, 2, 3], [4, 5, 6, 7], [3, 2, 6, 5],
            [0, 3, 5, 4], [0, 4, 7, 1], [1, 7, 6, 2]
        ],
        [
            [0.375, 0.0], [0.625, 0.0], [0.625, 0.25], [0.375, 0.25],
            [0.375, 0.25], [0.625, 0.25], [0.625, 0.5], [0.375, 0.5],
            [0.375, 0.5], [0.625, 0.5], [0.625, 0.75], [0.375, 0.75],
            [0.375, 0.75], [0.625, 0.75], [0.625, 1.0], [0.375, 1.0],
            [0.625, 0.0], [0.875, 0.0], [0.875, 0.25], [0.625, 0.25],
            [0.125, 0.0], [0.375, 0.0], [0.375, 0.25], [0.125, 0.25]
        ],
        'polyCube'
    )
    
    """
    # build vert list
    vertArray = MFloatPointArray()
    for vert in verts:
        vertArray.append(float(vert[0]), float(vert[1]), float(vert[2]))
    # build polyArray and polyConnect lists
    polyArray = MIntArray()
    polyConnect = MIntArray()
    for face in faces:
        polyArray.append(len(face))
        for vertIndex in face:
            polyConnect.append(vertIndex)
    if uvs is not None:
        # build UV lists
        uvIds = MIntArray()
        uArray = MFloatArray()
        vArray = MFloatArray()
        for i, uv in enumerate(uvs):
            uArray.append(float(uv[0]))
            vArray.append(float(uv[1]))
            uvIds.append(i)
    meshTransform = MFnTransform()
    meshTransformNode = meshTransform.create()
    mesh = MFnMesh()
    if uvs is not None:
        mesh.create(len(verts), len(faces),
                               vertArray, polyArray, polyConnect,
                               uArray, vArray,
                               meshTransformNode)
        mesh.assignUVs(polyArray, uvIds)
    else:
        mesh.create(len(verts), len(faces),
                               vertArray, polyArray, polyConnect,
                               meshTransformNode)
    meshTransform.setName(name)
    mesh.setName(name + 'Shape')
    MGlobal().clearSelectionList()
    MGlobal().selectByName(meshTransform.name())
    if meshParent is not None:
        parent(selected()[0], meshParent)

def genUVMesh(mesh, progress=None):
    # build the vertex list by iterating through the uvs list
    # causes UV seams to be actual gaps in the geometry
    verts = []
    for uv in ls(mesh.map, fl=1):
        vert = ls(polyListComponentConversion(uv, fuv=1, tv=1)[0])[0]
        vertPosition = vert.getPosition(space='object')
        verts.append(vertPosition)
    # build the face vertex indices out of the face uv indices
    faces = []
    uvs = []
    for i, face in enumerate(ls(mesh.faces, fl=1)):
        faceVerts = []
        for vert in range(face.polygonVertexCount()):
            faceVerts.append(face.getUVIndex(vert))
            uvs.append(face.getUV(vert))
        faces.append(faceVerts)
        # update progress bar
        if progress is not None:
            curProgress = math.floor(50.0 * float(i) / float(len(mesh.faces)))
            progress.setProgress(curProgress)
    createMesh(verts, faces, uvs, mesh.name() + 'UV')

def createUVBlendShape(mesh, progress=None):
    blendMesh = duplicate(mesh)[0].getShape()
    # set all vertex positions to (U, V, 0)
    for i, face in enumerate(ls(blendMesh.faces, fl=1)):
        for vert in range(face.polygonVertexCount()):
            uv = face.getUV(vert)
            face.setPoint(dt.Point(uv[0] - 0.5, uv[1] - 0.5, 0), vert)
        # update progress bar
        if progress is not None:
            curProgress = 50 + math.floor(50.0 * float(i) / float(len(blendMesh.faces)))
            progress.setProgress(curProgress)
    # scale the blendshape up to an approximately correct size
    blendBB = xform(blendMesh.getParent(), q=1, bb=1)
    meshBB = xform(mesh.getParent(), q=1, bb=1)
    blendScale = math.sqrt(math.sqrt(math.pow(blendBB[3] - blendBB[0], 2) + math.pow(blendBB[4] - blendBB[1], 2)) + math.pow(blendBB[5] - blendBB[2], 2))
    meshScale =  math.sqrt(math.sqrt(math.pow(meshBB[3] - meshBB[0], 2) + math.pow(meshBB[4] - meshBB[1], 2)) + math.pow(meshBB[5] - meshBB[2], 2))
    diff = 2.0 * meshScale / blendScale
    xform(blendMesh.getParent(), r=1, s=(diff, diff, diff))
    makeIdentity(blendMesh.getParent(), a=1, t=1, r=1, s=1)
    # make the blendshape
    blendShape(blendMesh, mesh)
    
def createUVMeshBlend():
    assert len(selected()) == 1, 'Select a mesh'
    assert isinstance(selected()[0].getShape(), Mesh), 'Select a mesh'
    progBar = getMainProgressBar()
    progBar.beginProgress()
    progBar.setProgress(0)
    genUVMesh(selected()[0].getShape(), progBar)
    createUVBlendShape(selected()[0].getShape(), progBar)
    progBar.endProgress()
    
createUVMeshBlend()
