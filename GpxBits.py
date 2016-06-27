'''
Created on 8 Mar 2016

@author: paul.hester
'''
import sys
import xml.etree.ElementTree as ET
from xml.dom import minidom
import gpxpy
import gpxpy.gpx
import math


from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from _ast import BitAnd

class RouteWp:
  pass

class Waypoint:
  def __init__(self, wp):
    self.name = wp.name
    self.lat = wp.latitude
    self.long = wp.longitude
    self.desc = wp.description
    self.cyl = 400

class Route:
  def __init__(self, name, routeWaypoints):
    self.name = name
    self.routeWaypoints = routeWaypoints

class Gpsdata(Waypoint, Route):
  def __init__(self):
    self.wps=[]
    self.rts=[]
  
  def addWaypoint(self, wp):
    self.wps.append(Waypoint(wp))
  
  def addRoute(self, name, defCyl, rtewps):
    rte = []
    for fullwp in rtewps:
      wp=RouteWp
      wp.cyl = defCyl
      wpBits=fullwp.split('|')
      wp.name = wpBits[0]
      if len(wpBits) > 1:
        wp.cyl = wpBits[1]
      if wp.cyl == '':
        wp.cyl = 400
      rte.append(wp)
    self.rts.append(Route(name, rte))
  
  
  def readWaypoints(self, infile):
    gpx_file = open(infile, 'r')
    gpx = gpxpy.parse(gpx_file)
    gpx_file.close()
    
    for waypoint in gpx.waypoints:
      self.addWaypoint(waypoint)

  def readRoutes(self, rtefile):
    used = {}
    err = False
    compAdded = False
    print('add routes')
    with open(rtefile) as rte:
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
          self.addRoute(name, defCyl, waypoints)
        if isComp == True:
          name = 'COMPETITION-ROUTE'
          if name in used:
            print('used route name {}'.format(name))
          else:
            used[name]=True
            compAdded = True
            self.addRoute(name, defCyl, waypoints)
          
        if err==True:
          print('##Error')
          break
    if compAdded == False:
      print('#### Warning - no comp route - first one will be overwritten')



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
      tagtsk = ET.Element('Task')
      tagtsk.attrib['fai_finish'] = str(0)
      tagtsk.attrib['finish_min_height_ref'] = 'AGL'
      tagtsk.attrib['finish_min_height'] = str(0)
      tagtsk.attrib['start_max_height_ref'] = str('AGL')
      tagtsk.attrib['start_max_height'] = str(0)
      tagtsk.attrib['start_max_speed'] = str(0)
      tagtsk.attrib['start_requires_arm'] = str(0)
      tagtsk.attrib['aat_min_time'] = str(10800)
      tagtsk.attrib['type'] = 'RT'
      reparsed = minidom.parseString(ET.tostring(tagtsk,'unicode'))
      tskfile = open(name+'.tsk','w')
      tskfile.write(reparsed.toprettyxml(indent='  ', newl='\n'))
      tskfile.close()

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
             
def cupWrite(wps, cupFile):
  print(cupFile)
  # open cupFile
  cupf = open(cupFile+'.cup', 'w')
  cupf.write('name,code,country,lat,lon,elev,style,rwdir,rwlen,freq,desc\n')
  for wpt in wps:
    latFrac, latInt = math.modf(wpt.latitude)
    longFrac, longInt = math.modf(wpt.longitude)
    if latInt < 0:
      latStr = 'S'
      latInt = -latInt
      latFrac = -latFrac
    else:
      latStr = 'N'
    if longInt < 0:
      longStr = 'W'
      longInt = -longInt
      longFrac = -longFrac
    else:
      longStr = 'E'
    print('"{}-{}","{}",,{:02.0f}{:06.3f}{},{:03.0f}{:06.3f}{},{}m,1,,,,'.format(wpt.name, wpt.description, wpt.name, latInt,latFrac*60,latStr, longInt, longFrac*60, longStr, wpt.elevation))
    cupf.write('"{}-{}","{}",,{:02.0f}{:06.3f}{},{:03.0f}{:06.3f}{},{}m,1,,,,\n'.format(wpt.name, wpt.description, wpt.name, latInt,latFrac*60,latStr, longInt, longFrac*60, longStr, wpt.elevation))
  #close cupFile
  cupf.close()

def WaypointConvert(wps, outfile, rtefilename):
  braun = open(outfile+'.fw5', 'w')
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
  cupWrite(wps, outfile)


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


    gpsdata = Gpsdata()
    gpsdata.readWaypoints(infile)
    cnt=0
    for waypoint in gpsdata.wps:
      print('class waypoint {0} -> ({1},{2}) {3}'.format(waypoint.name, waypoint.lat, waypoint.long, waypoint.desc))
      cnt = cnt + 1

    if rtefile:
      gpsdata.readRoutes(rtefile)
      for route in gpsdata.rts:
        ln='class rte {0}:'.format(route.name)
        for wp in route.routeWaypoints:
          ln = ln + 'wp {0}/{1} - '.format(wp.name, wp.cyl)
        print(ln)



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