'''
Created on 8 Mar 2016

@author: paul.hester
'''
import sys
import xml.etree.ElementTree as ET
from xml.dom import minidom
import gpxpy
import gpxpy.gpx


from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from _ast import BitAnd

def AddWaypoints(tagroot, wps):
  for waypoint in wps:
    tagwpt = ET.SubElement(tagroot, 'wpt')
    tagwpt.attrib['lat'] = str(waypoint.latitude)
    tagwpt.attrib['lon'] = str(waypoint.longitude)
    ET.SubElement(tagwpt, 'ele').text=str(waypoint.elevation)
    ET.SubElement(tagwpt, 'name').text=waypoint.name
    if not waypoint.description:
      waypoint.description = "None"
    ET.SubElement(tagwpt, 'desc').text=waypoint.name+', '+ waypoint.description
    tagext=ET.SubElement(tagwpt, 'extensions')
    ET.SubElement(tagext, 'radius').text='400'

def AddRoute(tagroot, name, defCyl, waypoints, wps):
  tagrte = ET.SubElement(tagroot, 'rte')
  ET.SubElement(tagrte, 'name').text = name
  for fullwp in waypoints:
      cyl = defCyl
      wpBits=fullwp.split('|')
      wp = wpBits[0]
      if len(wpBits) > 1:
        cyl = wpBits[1]
      #find name
      for waypoint in wps:
        if wp.lower() == waypoint.name.lower():
          tagrpt = ET.SubElement(tagrte, 'rtept')
          tagrpt.attrib['lat'] = str(waypoint.latitude)
          tagrpt.attrib['lon'] = str(waypoint.longitude)
          ET.SubElement(tagrpt, 'ele').text = str(waypoint.elevation)
          ET.SubElement(tagrpt, 'name').text=waypoint.name
          ET.SubElement(tagrpt, 'desc').text=waypoint.name+', '+ waypoint.description
          tagext=ET.SubElement(tagrpt, 'extensions')
          if cyl == '':
            cyl = '400'
          ET.SubElement(tagext, 'radius').text = cyl
          break

def AddRoutes(tagroot, rtefilename, wps):
  used = {}
  err = False
  compAdded = False
  print('add routes')
  with open(rtefilename) as rte:
    routes = rte.readlines()
  for route in routes:
    route = route.rstrip()
    name=None
    isComp = False
    defCyl=None
    print('route is {}'.format(route))
    parts = route.split(';')
    if len(parts) == 3:
      name = parts[0]
      if name[0] == '*':
        isComp = True
        name = name[1:]
      defCyl = parts[1]
      waypoints = parts[2].split('-')
      if name in used:
        print('used route name {}'.format(name))
      else:
        used[name]=True
        AddRoute(tagroot, name, defCyl, waypoints, wps)
      if isComp == True:
        name = 'COMPETITION-ROUTE'
        if name in used:
          print('used route name {}'.format(name))
        else:
          used[name]=True
          compAdded = True
          AddRoute(tagroot, name, defCyl, waypoints, wps)
        
      if err==True:
        print('##Error')
        break
  if compAdded == False:
    print('#### Warning - no comp route - first one will be overwritten')
             
  

def WaypointConvert(wps, outfile, rtefilename):
  braun = open(outfile, 'w')
  nsm = {'xmlns': "http://www.topografix.com/GPX/1/1/",
         'version': "1.0",
         'xmlns:xsi':"http://www.w3.org/2001/XMLSchema-instance",
         'xsi:schemaLocation': "http://www.topografix.com/GPX/1/1/ http://www.topografix.com/GPX/1/1//gpx.xsd",
         'creator': "FlyChart, Version 4.57, Sep. 1st 2014 - http://www.flytec.ch"}
  taggpx = ET.Element('gpx', attrib=nsm)
  AddWaypoints(taggpx, wps)

  if rtefilename:
    AddRoutes(taggpx, rtefilename, wps)

  reparsed = minidom.parseString(ET.tostring(taggpx,'unicode'))
  
  #print(reparsed.toprettyxml(indent='  ', newl='\n'))
  braun.write(reparsed.toprettyxml(indent='  ', newl='\n'))
  #a = ET.Element('gpx', xmlns="http://www.topografix.com/GPX/1/1/",version="1.0", xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance",xsi:schemaLocation="http://www.topografix.com/GPX/1/1/ http://www.topografix.com/GPX/1/1//gpx.xsd",creator="FlyChart, Version 4.57, Sep. 1st 2014 - http://www.flytec.ch")
  #ET.SubElement(a, '<gpx xmlns="http://www.topografix.com/GPX/1/1/" version="1.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/1/ http://www.topografix.com/GPX/1/1//gpx.xsd" creator="FlyChart, Version 4.57, Sep. 1st 2014 - http://www.flytec.ch">\n'
  braun.close()
  


def GpxStuff(infile, outfile, rtefile):
    gpx_file = open(infile, 'r')
    numTracks = 0
    numWPts = 0
    numRtes = 0
    gpx = gpxpy.parse(gpx_file)
    gpx_file.close()
    
    for track in gpx.tracks:
      numTracks = numTracks + 1
      for segment in track.segments:
        for point in segment.points:
          print('Point at ({0},{1}) -> {2}'.format(point.latitude, point.longitude, point.elevation))
    
    for waypoint in gpx.waypoints:
      numWPts = numWPts + 1
      print('waypoint {0} -> ({1},{2}) {3}'.format(waypoint.name, waypoint.latitude, waypoint.longitude, waypoint.description))
    
    for route in gpx.routes:
      print('Route:')
      numRtes = numRtes + 1
      for point in route.points:
        print('Point at ({0},{1}) -> {2}'.format(point.latitude, point.longitude, point.elevation))
    
    print('Num tracks {}\r\nNum waypoints {}\r\nNum routes {}'.format(numTracks, numWPts, numRtes))
    
    if numWPts > 0:
      WaypointConvert(gpx.waypoints, outfile, rtefile)
    # There are many more utility methods and functions:
    # You can manipulate/add/remove tracks, segments, points, waypoints and routes and
    # get the GPX XML file from the resulting object:
    
    #print('GPX:', gpx.to_xml())








def main(argv=None): # IGNORE:C0111
    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    #try:
    # Setup argument parser
    parser = ArgumentParser(description='GPX stuff',formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument('infile', help='gpx file')
    parser.add_argument('outfile', help='output file')
    parser.add_argument('-r', '--rtefile', help='routes file. Format is routeName;default cyl diameter in metres;waypointName1;WaypointName2{non default cyl diameter} etc')
    # Process arguments
    args = parser.parse_args()
    GpxStuff(args.infile, args.outfile, args.rtefile)

    #except Exception as e:
        #sys.stderr.write(": " + repr(e) + "\n")
        #sys.stderr.write("For help use --help")
        #return 2


if __name__ == "__main__":
    sys.exit(main())