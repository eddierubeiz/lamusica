#!/usr/bin/env python
# (c) 2011-2017 Simon Budig <simon@budig.de>

import sys, struct, math, getopt, pdb
import cairo

# Mensch macht bequem ca. 120-180 UPM.

delta_ticks = 0

models = {
   # https://www.spieluhr.de/Artikel/varAussehen.asp?ArtikelNr=4905
   "sankyo15" : {
      # Gis Dur? SRSLY?
      "lowest"   : 56,
      "notes"    : [
                     #                       G#1, A#1,
                                               0,   2,
                     # C2, C#2, D#2, F2, G2, G#2, A#2,
                        4,   5,   7,  9, 11,  12,  14,
                     # C3, C#3, D#3, F3, G3, G#3,
                       16,  17,  19, 21, 23,  24 ],
      "program"  :  1,
      "height"   : 41.0,
      "offset"   :  6.0,
      "distance" :  2.0,
      "diameter" :  1.8,
      "step"     :  8.0,
      "speed"    :  300./49,     # mm/U
   },
   # https://www.spieluhr.de/Artikel/varAussehen.asp?ArtikelNr=4972
   "sankyo20" : {
      "lowest"   : 48,
      "notes"    : [ #  C,  D,  E,  F,  G,  A,  B,
                        0,  2,  4,  5,  7,  9, 11,
                     # C1, D1, E1, F1, G1, A1, B1,
                       12, 14, 16, 17, 19, 21, 23,
                     # C2, D2, E2, F2, G2, A2,
                       24, 26, 28, 29, 31, 33 ],
      "program"  :  2,
      "height"   : 70.0,
      "offset"   :  6.5,
      "distance" :  3.0,
      "diameter" :  2.4,
      "step"     :  7.0,
      "speed"    :  300./53,
   },
   # http://www.njdean.co.uk/musical-movements-mbm30hp.htm
   # http://www.mmdigest.com/Gallery/Sounds/mg_Teamola30n.html
   # https://www.spieluhr.de/Artikel/varAussehen.asp?ArtikelNr=5984
   "teanola30" : {
      "lowest"   : 41,
      "notes"    : [
                     #                        F,  F#,  G,  G#,  A,  A#,  B,
                                              0,       2,
                     # C1, C#1, D1, D#1, E1, F1, F#1, G1, G#1, A1, A#1, B1,
                        7,       9,      11, 12,      14,      16, 17,  18,
                     # C2, C#2, D2, D#2, E2, F2, F#2, G2, G#2, A2, A#2, B2,
                       19,  20, 21,  22, 23, 24,  25, 26,  27, 28, 29,  30,
                     # C3, C#3, D3, D#3, E3, F3,      G3,      A3
                       31,  32, 33,  34, 35, 36,      38,      40
                     ],
      "program"  :  3,
      "height"   : 70.0,
      "offset"   :  6.0,
      "distance" :  2.0,
      "diameter" :  1.8,
      "step"     :  8.0,
      "speed"    :  300./45.5,
      #"speed"    :  500./45.5,
   
      #"speed"    :  1000./45.5,

   },

   # http://www.leturlutain.fr/index.php?item=33-notes-sankyo-music-box&action=article&group_id=10000033&aid=5796&lang=EN
   # http://www.spieluhr.de/Artikel/varAussehen.asp?ArtikelNr=5663
   "sankyo33" : {
      "lowest"   : 48,
      "notes"    : [ #  C,       D,  D#,  E,  F,  F#,  G,  F#,  A,  A#,  B,
                        0,       2,   3,  4,  5,   6,  7,   8,  9,  10, 11,
                     # C1, C#1  D1, D#1, E1, F1, F#1, G1, G#1, A1, A#1, B1,
                       12,  13, 14,  15, 16, 17,  18, 19,  20, 21,  22, 23,
                     # C2, C#2, D2, D#2, E2, F2, F#2, G2, G#2, A2,
                       24,  25, 26,  27, 28, 29,  30, 31,  32, 33 ],
      "program"  :  4,
      "height"   : 70.0,
      "offset"   :  5.3,
      "distance" :  1.8,
      "diameter" :  1.7,
      "step"     :  8.0,
   }
}


def output_file (model, filename, is_pdf, notelist, mindelta):
   # This is 2x A4 in  millimeters.
   # pwidth  = 420.0
   # pheight = 297.0

   # pwidth  = 700.0 - 20
   # pheight = 500.0 - 20

   # US Letter:
   # 215.9mm x 279.4mm
   #pwidth  = 279.4
   #pheight = 215.9

   # US Letter with a 10mm border
   pwidth  = 269.4
   pheight = 205.9

   # US Legal
   #pwidth = 356   
   #pheight = 215.9

   # US Legal 2
   #pwidth = 336   
   #pheight = 195.9


   pborder = 4
   #pborder = 10    - 8
   height  = model["height"]
   offset  = model["offset"]
   radius  = model["diameter"] / 2
   dist    = model["distance"]
   step    = model["step"] / mindelta
   leadin  = 20.0
   leadout = 20.0

   alltimes = list (set (sum (notelist, [])))
   alltimes.sort ()
   start   = alltimes[0]
   end     = alltimes[-1]
   length  = int (end - start) * step + radius * 2 + leadin + leadout

   splits = [0.0]
   startpos = splits[0]
   breakpos = splits[0]

   for i in range (1, len(alltimes)):
      middlepos = leadin + (alltimes[i] + alltimes[i-1]) * step / 2
      if middlepos - startpos > pwidth - 2 * pborder:
         splits.append (breakpos)
         startpos = breakpos

      if (alltimes[i] - alltimes[i-1]) * step > radius * 4:
         breakpos = middlepos

   splits.append (length)
   
   holes = [(leadin + (n - start) * step, i * dist + offset) for i in range (len (notelist)) for n in notelist[i]]
   holes.sort ()

   if is_pdf:
      surface = cairo.PDFSurface (filename,
                                  pwidth / 25.4 * 72,
                                  pheight / 25.4 * 72)
   else:
      # cairo svg cannot deal with multiple pages
      pheight = len (splits) * (height + pborder) - height + 1
      surface = cairo.SVGSurface (filename,
                                  pwidth / 25.4 * 72,
                                  pheight / 25.4 * 72)

   cr = cairo.Context (surface)

   cr.scale (2.83464, -2.83464)
   cr.translate (0.0, -pheight)
   cr.set_line_width (0.2)

   cr.move_to (4, 5)
   cr.line_to (7, 7)
   cr.line_to (7, 5.7)
   cr.line_to (17, 5.7)
   cr.line_to (17, 4.3)
   cr.line_to (7, 4.3)
   cr.line_to (7, 3)
   cr.close_path ()
   cr.fill ()

   y0 = pborder
   y1 = y0 + height

   x0 = splits.pop (0)
   while splits:
      x1 = splits.pop (0)
      cr.set_source_rgb (0, 0, 1)
      cr.set_line_width (0.4)
      # cr.rectangle (pborder, y0, x1 - x0, y1 - y0)
      cr.move_to (pborder, y0)
      cr.line_to (pborder, y1)
      cr.move_to (pborder + x1 - x0, y0)
      cr.line_to (pborder + x1 - x0, y1)
      cr.stroke ()

      if 0:
         cr.set_source_rgb (0.7, 0.7, 0.7)
         for i in range (len (model["notes"])):
            y = y0 + offset + i * dist
            cr.move_to (pborder, y)
            cr.line_to (pborder + x1 - x0, y)
            if model["notes"][i] % 12 in [0, 2, 4, 5, 7, 9, 11]:
               if model["notes"][i] % 12 == 0:
                  cr.set_line_width (0.4)
               else:
                  cr.set_line_width (0.2)
               cr.set_dash ([], 0)
            else:
               cr.set_line_width (0.2)
               cr.set_dash ([.5, 1], 0)
            cr.stroke ()

      cr.set_dash ([], 0)
      cr.set_line_width (0.4)
      border_end = pborder;
      while holes and holes[0][0] < x1:
         x, y = holes.pop (0)
         cr.new_sub_path ()
         cr.arc (x - x0 + pborder, y + y0, radius, 0.0*math.pi, 0.5*math.pi)
         cr.arc (x - x0 + pborder, y + y0, radius, 0.5*math.pi, 1.0*math.pi)
         cr.arc (x - x0 + pborder, y + y0, radius, 1.0*math.pi, 1.5*math.pi)
         cr.arc (x - x0 + pborder, y + y0, radius, 1.5*math.pi, 2.0*math.pi)
         cr.close_path ()
         if x - x0 + pborder - border_end >= 50:
            cr.move_to (border_end, y0)
            cr.line_to (x - x0 + pborder, y0)
            cr.move_to (border_end, y1)
            cr.line_to (x - x0 + pborder, y1)
            cr.new_sub_path ()
            border_end = x - x0 + pborder

      if border_end < x1:
         cr.move_to (border_end, y0)
         cr.line_to (x1 - x0 + pborder, y0)
         cr.move_to (border_end, y1)
         cr.line_to (x1 - x0 + pborder, y1)
         cr.new_sub_path ()

      cr.set_source_rgb (1, 0, 0)
      cr.stroke ()

      x0 = x1
      y0 = y1 + pborder
      if y0 + height + pborder > pheight:
         y0 = pborder
         cr.show_page ()
      y1 = y0 + height

   del cr
   del surface


def output_midi (model, filename, notelist, mindelta):
   # fix up notes to correspond to midi notes
   notes = [ n + model["lowest"] for n in model["notes"] ]

   events = []
   for i in range (len (notelist)):
      events += [(t, notes[i], 1) for t in notelist[i]]
      # add events to shut off the notes
      events += [(t+mindelta, notes[i], 0) for t in notelist[i]]

   events.sort()

   last_time = 0
   eventdata = bytearray()
   # program select
   eventdata += bytearray([0x00 , 0xc0 , model["program"]])

   for t, i, on in events:
      dt = t - last_time
      if (dt >> 21):
         eventdata += bytearray([ (0x80 | ((dt >> 21) & 0x7f)) ])
      if (dt >> 14):
         eventdata += bytearray([  (0x80 | ((dt >> 14) & 0x7f))  ])
      if (dt >> 7):
         eventdata += bytearray([  (0x80 | ((dt >> 7) & 0x7f))  ])

      eventdata += bytearray([  (0x00 | ((dt >> 0) & 0x7f)) ])
      if on:
         eventdata += bytearray([ 0x90, i , 127 ])
      else:
         eventdata += bytearray([ 0x80, i, 127  ])
      last_time += dt

   eventdata += bytearray([ 0x00, 0xFF, 0x2F, 0x00 ]) 

   outfile = open(filename, 'wb')
   outfile.write (bytes("MThd", 'ascii') + struct.pack (">ihhh", 6, 0, 1, delta_ticks))
   outfile.write (bytes("MTrk", 'ascii') + struct.pack (">i", len (eventdata)))
   outfile.write (eventdata)
   outfile.close ()



class Note (object):
   def __init__ (self, note, ticks, channel, track):
      self.note = note
      self.ticks = ticks
      self.channel = channel
      self.track = track
      self.filtered = set()


   def __repr__ (self):
      return "Note (%s, %d, %d, %d)" % (self.note, self.ticks, self.channel, self.track)


class PianoRoll (object):
   def __init__ (self, notes=[]):
      self.notes = notes
      self.transpose = 0


   def __repr__ (self):
      return "PianoRoll (%r)" % (self.notes)


   def add (self, note):
      self.notes.append (note)


   def get_compat_band (self, model):
      self.notes.sort (key=lambda x: x.ticks)

      # all the notes in the piece

      notes = [n + model["lowest"] for n in model["notes"]]
      # available notes

      band = [[] for i in range (len(notes))]
      for i in range (len (notes)):
         source_notes = [notes[i]]
         n = notes[i] - 12
         while n >= 0 and n not in notes:
            source_notes.append (n)
            n -= 12
         n = notes[i] + 12
         while n <= 127 and  n not in notes:
            source_notes.append (n)
            n += 12

         band[i] = [n.ticks for n in self.notes
                        if n.note + self.transpose in source_notes
                        #if n.note + self.transpose[n.track % len (self.transpose)] in source_notes
                        if not n.filtered]
         band[i] = sorted (list (set (band[i])))
      return band


   def min_repetition (self):
      self.notes.sort (key=lambda x: x.ticks)
      self.notes.sort (key=lambda x: x.note)
      mindelta = sys.maxsize
      n0 = self.notes[0]
      for n in self.notes[1:]:
         d = n.ticks - n0.ticks
         # notes at the same tick are considered identical
         if n.note == n0.note and d > 0 and d < mindelta:
            mindelta = n.ticks - n0.ticks
         n0 = n

      return mindelta


   def find_transpose (self, available_notes,
                       allow_octaves=True, allow_halftones=True):
      transpose = 0
      transpose_error = sys.maxsize #sys.maxint

      highest = max ([n.note for n in self.notes])
      lowest  = min ([n.note for n in self.notes])

      notecount = [len ([n for n in self.notes if n.note == i])
                   for i in range (128)]

      for trans in range (min (available_notes) - highest - 1,
                          max (available_notes) - lowest + 2):

         if not allow_halftones and trans % 12 != 0:
            continue

         if not allow_halftones and not allow_octaves and trans % 12 == 0:
            continue
         
         errcount = 0
         for i in range (128):
            if (i+trans) not in available_notes:
               errcount += notecount[i]
         if errcount < transpose_error or (errcount == transpose_error and abs(trans) < abs (transpose)):
            transpose_error = errcount
            transpose = trans

      
      # sys.stderr.write(  "transposing by %d octaves and %d halftones\n" % (transpose / 12, transpose % 12))
      # sys.stderr.write(  "    --> %d notes not playable\n" % (transpose_error))
      print(  "transposing by %d octaves and %d halftones" % (transpose / 12, transpose % 12))
      print(  "    --> %d notes not playable" % (transpose_error))

      return transpose


   def filter_repetition (self, delta):
      self.notes.sort (key=lambda x: x.ticks)
      self.notes.sort (key=lambda x: x.note)
      count = 0
      n0 = self.notes[0]
      for n1 in self.notes[1:]:
         if n1.note == n0.note:
            d = n1.ticks - n0.ticks
            if d < delta:
               n1.filtered.add ("delta")
               count += 1
            else:
               n1.filtered.discard ("delta")
               n0 = n1
         else:
            n0 = n1
            n0.filtered.discard ("delta")

      return count



class MidiImporter (object):
   def __init__ (self, target):
      self.target = target
      self.timediv = 0
      self.num_tracks = 0
      self.cur_program = -1


   def import_event (self, ticks, track, eventdata):
      cur_program = -1;
      mc = eventdata[0] >> 4
      
      ch = eventdata[0] & 0x0f

      # fix up noteon with velocity = 0 to noteoff.
      if mc == 0x09 and eventdata[2] == 0:
         mc = 0x08

      if mc == 0x08:
         pass
         # print >>sys.stderr, ticks, ": noteoff"
      elif mc == 0x09:
         # print >>sys.stderr, ticks, ": noteon (%d)" % (ord(eventdata[0]) & 0x0f), ord (eventdata[1]), ord (eventdata[2])
         if self.cur_program != 127: # exclude percussion track
            n = Note (eventdata[1], ticks, ch, track)
            self.target.add (n)
      elif mc == 0x0b:
         # print >>sys.stderr, ticks, ": controller", ord (eventdata[1])
         pass
      elif mc == 0x0c:
         #print >>sys.stderr, ticks, ": program change", ord (eventdata[1])
         self.cur_program = eventdata[1]
         
         pass
      elif mc == 0x0d:
         # print >>sys.stderr, ticks, ": aftertouch", ord (eventdata[1])
         pass
      elif mc == 0x0e:
         # print >>sys.stderr, ticks, ": pitch bend"
         pass
      else:
         #print("ticks: %d, event %r" % (ticks, eventdata))
         # sys.stderr.write("ticks: %d, event %r" % (ticks, eventdata))
         pass


   def import_ticked_events (self, track, eventdata):
      ticks = 0
      mc = None
      t = eventdata
      while t:
         dt = 0
         while t[0] & 0x80:
            dt = (dt + (t[0] & 0x7f)) << 7
            
            t = t[1:]
         dt += t[0]

         t = t[1:]

         if t[0] & 0x80:
            mc = t[0]
            t = t[1:]

         if mc >> 4 in [0x08, 0x09, 0x0a, 0x0b, 0x0e]:
            command = bytes([mc]) + t[:2]
            t = t[2:]
         
         elif mc >> 4 in [0x0c, 0x0d]:
            command = bytes([mc]) + t[:1]
            t = t[1:]
         elif mc in [0xf8, 0xfa, 0xfb, 0xfc]:
            command = mc
         elif mc == 0xff:            
            type = t[0]
            t = t[1:]
            
            command = [mc] + [type]


            l = 0
            while t[0] & 0x80:
               command += t[0]
               l = (l + (t[0] & 0x7f)) << 7
               t = t[1:]
            l += t[0]
            
            command += t[:l+1]
            
            t = t[l+1:]
         elif mc in [0xf0, 0xf7]:
            command = mc
            l = 0
            while t[0] & 0x80:
               command += t[0]
               l = (l + (t[0] & 0x7f)) << 7
               t = t[1:]
            l += t[0]
            command = bytes([command]) + t[:l+1]
            t = t[l+1:]
         else:
            raise Exception('unknown MIDI event: %d' % ord (t[0]))

         ticks += dt
         self.import_event (ticks, track, command)


   def import_chunk (self, chunkname, chunkdata):
      if self.timediv == 0 and chunkname != b'MThd':
         raise Exception("first chunk is not MThd\n")

      if chunkname == b'MThd':
         
         global delta_ticks

         if self.timediv != 0:
            raise Exception("multiple MThd chunks\n")

         if len (chunkdata) != 6:
            raise Exception("invalid MThd chunk\n")
         mtype, n_tracks, delta_ticks = struct.unpack (">hhh", chunkdata)
         self.timediv = delta_ticks

         #sys.stderr.write("type: %d, n_tracks: %d, delta_ticks: %d\n" % (mtype, n_tracks, delta_ticks))

      elif chunkname == b'MTrk':
         self.import_ticked_events (self.num_tracks, chunkdata)
         self.num_tracks += 1
      

   def import_file (self, filename):

      with open(filename, 'rb') as f:
         t = f.read()

         while t:
            if len (t) < 8:
               sys.stderr.write( "%d bytes remaining at end of MIDI file\n" % len(t))
               break
            chunkname = t[:4]
            chunklen = struct.unpack (">I", t[4:8])[0]
            if len (t) < 8+chunklen:
               raise Exception("Not enough bytes in MIDI file")
            chunkdata = t[8:8+chunklen]
            sys.stderr.write( chunkname.decode('utf-8'))
            sys.stderr.write(str(chunklen))
            self.import_chunk(chunkname, chunkdata)
            t = t[8+chunklen:]
      f.closed


def usage ():
   sys.stderr.write( "Usage: %s [arguments] <midi-file>" % sys.argv[0])
   sys.stderr.write( "  -h, --help: show usage\n")
   sys.stderr.write( "  -t, --transpose=number: transpose by n halftones (avoid auto)\n")
   sys.stderr.write( "  -f, --filter=number: ignore note-repetition faster than <ticks>\n")
   sys.stderr.write( "  -b, --box=type: music box type: sankyo15, sankyo20, teanola30, sankyo33\n")
   sys.stderr.write( "  -m, --midi=filename: output midi file name (omit if not wanted)\n")
   sys.stderr.write( "  -p, --pdf=filename: output pdf file name (omit if not wanted)\n")
   sys.stderr.write( "  -s, --svg=filename: output svg file name (omit if not wanted)\n")



if __name__=='__main__':
   try:
      opts, args = getopt.getopt (sys.argv[1:],
                                  "ht:f:b:m:s:p:",
                                  ["help", "transpose=",
                                  "filter=", "box=",
                                  "midi=", "svg=", "pdf="])
   except getopt.GetoptError as err:
      usage()
      sys.exit (2)

   if len (args) != 1:
      usage()
      sys.exit (2)

   midifile = None
   svgfile = None
   pdffile = None
   filter = 1
   boxtype = "sankyo20"
   transpose = None

   for o, a in opts:
      if o in ("-h", "--help"):
         usage()
         sys.exit()
      elif o in ("-t", "--transpose"):
         transpose = [ int (t) for t in a.split (",") ]
      elif o in ("-f", "--filter"):
         filter = int (a)
      elif o in ("-b", "--box"):
         boxtype = a
      elif o in ("-m", "--midi"):
         midifile = a
      elif o in ("-s", "--svg"):
         svgfile = a
      elif o in ("-p", "--pdf"):
         pdffile = a
      else:
         assert False, "unhandled option"

   model = models.get (boxtype, None)
   if not model:
      sys.stderr.write("Boxtype unknown. Available boxtypes are:")
      ms = models.keys ()
      ms.sort ()
      sys.stderr.write( "  * %s" % "\n  * ".join (ms))
      sys.exit (2)

   roll = PianoRoll()
   mi = MidiImporter (roll)
   mi.import_file (args[0])

   roll.filter_repetition (filter)

   if transpose == None:
      roll.transpose = roll.find_transpose ([model["lowest"] + i for i in model["notes"]])
   else:
      roll.transpose = transpose

   notelist = roll.get_compat_band (model)
   mindelta = roll.min_repetition ()

   if midifile:
      output_midi (model, midifile, notelist, mindelta)

   if pdffile:
      output_file (model, pdffile, True, notelist, mindelta)
   if svgfile:
      output_file (model, svgfile, False, notelist, mindelta)
