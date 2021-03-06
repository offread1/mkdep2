#!/usr/bin/env python

import sys

def usage():
    print("""
usage:
   mergedotfiles <sourcedir>

mergedotfiles expects at least one argument, the name of a directory containing a mkdep
generated .files to be merged with the .files in $PWD. The resulting file is (over)written
to .files

mergedotfiles also generates the .mkdep_rules file, containing explicit build rules for each file.
""")
if len(sys.argv)<2:
    usage()
    sys.exit(2)

orgfiles={}

if sys.argv[1]!="NOORGSRCDIR":
    f=open((sys.argv[1] + "/" + ".files"), "r")
    orgdotfile = f.readlines()
    f.close()

    for line in orgdotfile:
        s = line.split()
        if len(s)==0: continue

        if len(s) > 1:
            orgfiles[s[0]] = s[1]
        else:
            orgfiles[s[0]] = ""


f=open(".files", "r")
dotfile = f.readlines()
f.close()

modfiles={}
for line in dotfile:
    s = line.split()
    if len(s)==0: continue

    seppos = s[0].rfind("/")

    if len(s) > 1:
        modfiles[s[0]] = s[1]
    else:
        modfiles[s[0]] = ""

modfilelist = list(modfiles.keys())
orgfilelist = list(orgfiles.keys())

#print "orgfiles=", orgfiles
#print "modfiles=", modfiles

def writerule(fullsrcfilename, sourcedir, group, file):
    flag="$(FLAGS)"
    if group == "OPT2":
        flag="$(FLAGS2)"
    if sourcedir!="":
        if sourcedir[-1]!="/":
            sourcedir += "/"

    slashpos = fullsrcfilename.rfind("/")
    srcfilename = fullsrcfilename[slashpos+1:]

# write rules that look like this
#   build/mod_bound.o : src/mod_bound.f90 ; $(FORTRANCOMPILER) -c "+flag+" $(FREEFLAGS) -o $@ $<
# we assume all .o files to be in "build" with a uniqe name. if that fails add hash to names in build later.
    
    if srcfilename.find(".f90") > 0:
        file.write(("build/"+srcfilename.replace(".f90",".o")+" : "+sourcedir+fullsrcfilename+" ; $(FORTRANCOMPILER) -c "+flag+" $(FREEFLAGS) -o $@ $<\n"))
    elif srcfilename.find(".f") > 0:
        file.write(("build/"+srcfilename.replace(".f",".o")+" : "+sourcedir+fullsrcfilename+" ; $(FORTRANCOMPILER) -c "+flag+" $(FIXEDFLAGS) -o $@ $<\n"))
    elif srcfilename.find(".F90") > 0:
        file.write(("build/"+srcfilename.replace(".F90",".o")+" : "+sourcedir+fullsrcfilename+" ; $(FORTRANCOMPILER) -c "+flag+" $(PFREEFLAGS) -o $@ $<\n"))
    elif srcfilename.find(".F") > 0:
        file.write(("build/"+srcfilename.replace(".F",".o")+" : "+sourcedir+fullsrcfilename+" ; $(FORTRANCOMPILER) -c "+flag+" $(PFIXEDFLAGS) -o $@ $<\n"))
    elif srcfilename.find(".c") > 0:
        file.write(("build/"+srcfilename.replace(".c",".o")+" : "+sourcedir+fullsrcfilename+" ; $(CC) -c $(CFLAGS) -o $@ $<\n"))
    elif srcfilename.find(".s") > 0:
        file.write(("build/"+srcfilename.replace(".s",".o")+" : "+sourcedir+fullsrcfilename+" ; $(FORTRANCOMPILER) -c "+flag+" -o $@ $<\n"))


f=open(".files", "w")
rules=open(".mkdep_rules", "w")

# first overwrite original files with modified files
for key in list(orgfiles.keys()):
    if key in modfilelist:
        f.write((key + " " + modfiles[key] + "\n" ))
        writerule(key, "", modfiles[key], rules)
    else:
        f.write((sys.argv[1] + "/" + key + " " + orgfiles[key] + "\n" ))
        writerule(key, sys.argv[1], orgfiles[key], rules)

# then add new files to the list
for key in list(modfiles.keys()):
    if key not in orgfilelist:
        f.write((key + " " + modfiles[key] + "\n" ))
        writerule(key, "", modfiles[key], rules)

f.close()
rules.close()
