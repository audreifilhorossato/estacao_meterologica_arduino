# -*- coding: utf-8 -*-
"""
Imagens de prévia (PNG) com o VTK, sem abrir janela.

render(objetos, arquivo, camera, ...)
  objetos: lista de (shape do CadQuery, cor RGB 0-1, opacidade 0-1, desenhar_arestas)
  camera:  (posição, ponto focal, vetor "pra cima")
"""
import vtk


def _malha(shape):
    verts, tris = shape.tessellate(0.05, 0.3)
    pts = vtk.vtkPoints()
    for v in verts:
        pts.InsertNextPoint(v.x, v.y, v.z)
    cells = vtk.vtkCellArray()
    for a, b, c in tris:
        cells.InsertNextCell(3)
        cells.InsertCellPoint(a)
        cells.InsertCellPoint(b)
        cells.InsertCellPoint(c)
    pd = vtk.vtkPolyData()
    pd.SetPoints(pts)
    pd.SetPolys(cells)
    return pd


def render(objetos, arquivo, camera, tamanho=(1600, 1100), titulo=None, zoom=1.15,
           paralela=False, fundo=(1, 1, 1), rotulos=()):
    """rotulos: lista de (texto, (x, y, z)) escritos na imagem perto desse ponto."""
    ren = vtk.vtkRenderer()
    ren.SetBackground(*fundo)
    ren.SetUseDepthPeeling(1)
    ren.SetMaximumNumberOfPeels(8)
    win = vtk.vtkRenderWindow()
    win.SetOffScreenRendering(1)
    win.SetAlphaBitPlanes(1)
    win.SetMultiSamples(0)
    win.AddRenderer(ren)
    win.SetSize(*tamanho)
    for shape, cor, opac, arestas in objetos:
        pd = _malha(shape)
        nrm = vtk.vtkPolyDataNormals()
        nrm.SetInputData(pd)
        nrm.SetFeatureAngle(30)
        nrm.SplittingOn()
        mp = vtk.vtkPolyDataMapper()
        mp.SetInputConnection(nrm.GetOutputPort())
        act = vtk.vtkActor()
        act.SetMapper(mp)
        act.GetProperty().SetColor(*cor)
        act.GetProperty().SetOpacity(opac)
        act.GetProperty().SetSpecular(0.2)
        ren.AddActor(act)
        if arestas:
            fe = vtk.vtkFeatureEdges()
            fe.SetInputData(pd)
            fe.BoundaryEdgesOn()
            fe.FeatureEdgesOn()
            fe.SetFeatureAngle(30)
            fe.ManifoldEdgesOff()
            fe.NonManifoldEdgesOff()
            fe.ColoringOff()
            m2 = vtk.vtkPolyDataMapper()
            m2.SetInputConnection(fe.GetOutputPort())
            a2 = vtk.vtkActor()
            a2.SetMapper(m2)
            a2.GetProperty().SetColor(0.15, 0.3, 0.45)
            a2.GetProperty().SetLineWidth(1.5)
            a2.GetProperty().SetOpacity(min(1.0, opac + 0.5))
            ren.AddActor(a2)
    cam = ren.GetActiveCamera()
    pos, foco, up = camera
    cam.SetPosition(*pos)
    cam.SetFocalPoint(*foco)
    cam.SetViewUp(*up)
    if paralela:
        cam.ParallelProjectionOn()
    ren.ResetCamera()
    cam.Zoom(zoom)
    for texto, ponto in rotulos:
        rt = vtk.vtkBillboardTextActor3D()
        rt.SetInput(texto)
        rt.SetPosition(*ponto)
        rt.GetTextProperty().SetFontSize(26)
        rt.GetTextProperty().SetColor(0.05, 0.2, 0.45)
        rt.GetTextProperty().SetBold(1)
        rt.GetTextProperty().SetJustificationToLeft()
        rt.GetTextProperty().SetVerticalJustificationToCentered()
        rt.GetTextProperty().SetBackgroundColor(1.0, 1.0, 1.0)
        rt.GetTextProperty().SetBackgroundOpacity(0.85)
        ren.AddActor(rt)
    if titulo:
        txt = vtk.vtkTextActor()
        txt.SetInput(titulo)
        txt.GetTextProperty().SetFontSize(28)
        txt.GetTextProperty().SetColor(0.1, 0.1, 0.1)
        txt.SetPosition(20, tamanho[1] - 50)
        ren.AddActor2D(txt)
    win.Render()
    w2i = vtk.vtkWindowToImageFilter()
    w2i.SetInput(win)
    w2i.Update()
    wr = vtk.vtkPNGWriter()
    wr.SetFileName(arquivo)
    wr.SetInputConnection(w2i.GetOutputPort())
    wr.Write()
