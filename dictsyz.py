#! /usr/bin/env python3

import collections
import re


# parse all the dictionary entries
dd     = collections.defaultdict(list)
counts = collections.Counter()

with open('dictionary.txt') as lines:
 try:
   for line in lines:
      if not re.match(r'\S', line):
         continue # skip empty lines
      #print(line)
      mch = re.fullmatch(r'\"?(.*?)\s*\(.*?\)\s*(.*)\s*', line)
      if not mch:
         continue
      word = mch.group(1).lower()
      defn = mch.group(2).lower()

      for dw in re.finditer(r'(\w+)', defn):
         w = dw.group(0)
         if len(w)==1:
            continue
         if w == 'd':
            stophere=1
         counts[w] += 1
         if w not in dd[word]:
            dd[word].append(w)
 except:
    print('borked a line!', line)

# just for yux
print(counts.most_common(20))


# Check for words in definitions which do not have definitions
missing = collections.Counter()
for ws in dd.values():
   for w in ws:
      if w not in dd:
         missing[w] += 1

exceptions = 'america england europe china russia scotland california france ' \
   + 'asia africa rome spain italy australia mexico germany egypt ireland florida ' \
   + 'york britain brazil persia anglo zealand athens americana switzerland charles ' \
   + 'mississippi arabia norway syria madagascar cambridge mohammed portugal james ' \
   + 'sweden alba venice william thomas peru borneo washington chaucer carolina ' \
   + 'constantinople plato alexandria palestine guiana belgium poland israel ' \
   + 'shakespeare austria sumatra oregon elizabeth aristotle milton prussia edward ' \
   + 'greenland abyssinia andrew linnaeus denmark netherlands hindostan ceylon thibet sicily' \
   + 'cornwall iliad johnson andes siberia ohio cuba ' \
   + 'etc esp illust cf pl specif de gr pres co dr adv iimr ch pr eng vb adj fr iii un gen  ' \
   + 'shak abbrev naut compar obs st ii mr zool chem di var '
for exception in re.finditer(r'\S+', exceptions):
   del missing[exception.group(0)]

for m,n in missing.most_common():
   if re.search(r'\d', m):                 # 1st, c6h4
      del missing[m]
      continue

   base = re.sub(r'^un', '', m)               # unsuitable --> suitable
   if base != m and base in dd:
      del missing[m]
      continue
   m = base

   # clean up standard grammatical patterns
   singular = re.sub(r's$', '', m)        # plants --> plant
   if singular != m and singular in dd:
      del missing[m]
      continue
   singular = re.sub(r'(s|ch|sh|x)es', r'\1', m)  # dresses --> dress
   if singular != m and singular in dd:           # churches --> church etc
      del missing[m]
      continue
   singular = re.sub(r'ies', 'y', m)      # armies --> army
   if singular != m and singular in dd:
      del missing[m]
      continue

   present = re.sub(r'ed$', '', m)        # represented --> represent
   if present != m and present in dd:
      del missing[m]
      continue
   present = re.sub(r'ed$', 'e', m)       # repplaced --> replace
   if present != m and present in dd:
      del missing[m]
      continue

   normal = re.sub(r'(er|est)$', '', m)         # higher --> high
   if normal != m and normal in dd:
      del missing[m]
      continue
   normal = re.sub(r'(er|est)$', 'e', m)        # larger --> large
   if normal != m and normal in dd:
      del missing[m]
      continue
   normal = re.sub(r'(ier|iest)$', 'y', m)      # earlier --> earliest
   if normal != m and normal in dd:
      del missing[m]
      continue


   adjective = re.sub(r'ly$', '', m)        # usually --> usual
   if adjective != m and adjective in dd:
      del missing[m]
      continue
   adjective = re.sub(r'ly$', 'le', m)      # unsuitably --> unsuitable
   if adjective != m and adjective in dd:
      del missing[m]
      continue
   adjective = re.sub(r'ness$', '', m)      # lewness --> lewd
   if adjective != m and adjective in dd:
      del missing[m]
      continue

   verb = re.sub(r'ing$', '', m)          # representing --> represent
   if verb != m and verb in dd:
      del missing[m]
      continue


   base = re.sub(r'a?tion', 't', m)       # inspection --> inspect
   if base != m and base in dd:           # solicitation --> solicit
      del missing[m]
      continue
   base = re.sub(r'tion', 'te', m)          # inspection --> inspect
   if base != m and base in dd:
      del missing[m]
      continue

   base = re.sub(r'(like|ment)$', '', m)   # assorted common endings
   if base != m and base in dd:
      del missing[m]
      continue


   print(m, n)




num = len(missing)
tot = sum(missing.values())
print('Total {} missing words, used {} times'.format(num, tot))

