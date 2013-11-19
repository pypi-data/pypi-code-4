import os, sys
import numpy
import bob
import vtk
import vtk.util.numpy_support as VN
import matplotlib.delaunay as triang
import argparse

def main():

  parser = argparse.ArgumentParser(description='View accumulated models in HDF5 files as a mesh and a point cloud with accumulated (averaged) texture.')
  parser.add_argument('path', metavar='path', type=str, help='path to the HDF5 file to be viewed')
  args = parser.parse_args(sys.argv[1:])

  try:
    f = bob.io.HDF5File(args.path)
    Shape = f.read('Shape_Data')
    Color = f.read('Color_Data')
    
    points = vtk.vtkPoints()
    colors = vtk.vtkUnsignedCharArray()
    colors.SetNumberOfComponents(3)
    colors.SetName("Colors")
    triangle = vtk.vtkTriangle()
    triangles = vtk.vtkCellArray()
    for i in range(0,Shape.shape[1]):
      for j in range(0,Shape.shape[2]):
        if Shape[2,j,i] != 0:
          p = points.InsertNextPoint(Shape[0,j,i],Shape[1,j,i],Shape[2,j,i])
          c = colors.InsertNextTuple3(Color[0,j,i],Color[1,j,i],Color[2,j,i])
    pts = VN.vtk_to_numpy(points.GetData())
    cens,edg,tris,neig = triang.delaunay(pts[:,0],pts[:,1])
    for t in range(0,len(tris)):
      tr = triangle.GetPointIds().SetId(0,tris[t][0])
      tr = triangle.GetPointIds().SetId(1,tris[t][1])
      tr = triangle.GetPointIds().SetId(2,tris[t][2])
      tr = triangles.InsertNextCell(triangle)
      
    polydata1 = vtk.vtkPolyData()
    polydata1.SetPoints(points)
    polydata1.GetPointData().SetScalars(colors)
    polydata1.SetPolys(triangles)
    polydata1.Modified()
    
    polydata2 = vtk.vtkPolyData()
    polydata2.SetPoints(points)
    polydata2.GetPointData().SetScalars(colors)
    polydata2.Modified()  
    vxft = vtk.vtkVertexGlyphFilter()
    vxft.SetInputConnection(polydata2.GetProducerPort())
    vxft.Update()
    polydata2 = vxft.GetOutput()
    
    mapper1 = vtk.vtkDataSetMapper()
    mapper2 = vtk.vtkDataSetMapper()
    mapper1.SetInput(polydata1)
    mapper2.SetInput(polydata2)  
    actor1 = vtk.vtkActor()
    actor2 = vtk.vtkActor()
    actor1.SetMapper(mapper1)
    actor2.SetMapper(mapper2)
    
    ren1 = vtk.vtkRenderer()
    ren2 = vtk.vtkRenderer()
    ren1.SetViewport([0.0, 0.0, 0.5, 1.0])
    ren2.SetViewport([0.5, 0.0, 1.0, 1.0])
    ren1.SetBackground(0.6,0.5,0.4)
    ren2.SetBackground(0.4,0.5,0.6)
    ren1.AddActor(actor1)
    ren2.AddActor(actor2)
    ren1.ResetCamera()
    ren2.ResetCamera()
      
    renWin = vtk.vtkRenderWindow()
    iren = vtk.vtkRenderWindowInteractor()
    renWin.SetSize(800, 400)
    renWin.AddRenderer(ren1)
    renWin.AddRenderer(ren2)
    iren.SetRenderWindow(renWin)  
    iren.Initialize()
    renWin.Render()
    iren.Start()    
    
    '''#Save the mesh (not the point cloud):
    exporter = vtk.vtkVRMLExporter()
    exporter.SetFileName(args.path.replace('.hdf5','.wrl'))
    exporter.SetRenderWindow(ren1.GetRenderWindow())
    exporter.Write()'''

  except IOError:
    print "The given file cannot be read."
  
  return 0

if __name__ == "__main__":
  main()
