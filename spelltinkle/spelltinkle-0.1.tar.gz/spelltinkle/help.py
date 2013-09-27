"""
Fast and simple editor based on Python, curses and pygments.

Put help for opening files on the filelist page


line numbers and scrollbar
      |
      v
     ____________
    | 1          |
    | 2          |
    | 3          |
    | 4          |
    |line:2 col:3|
     ------------
     

When selcting area with mouse use scrollbar to scroll up or down

session.py: result=actions.method(doc);isgenerator(result)? (for questions and other input)

Colors: in color array: search, syntax, match ()[]{}''"", errors
at update time: current line, marked region

remove tabs when reading (or replace with 4 tabs that display as spaces?)
* open terminal in current dir
smooth scrolling when jumping?
indent/dedent
a home
b block: b:begin, r:rectangle, l:lines
c copy
d delete
e end
f replace,x:regex
g goto 123,()[]{},x:inner
h help,x:search in help
i-(tab) x:insert file or !shell
j- x:join
k kill,x:backwards
l delete line
m- x:makro
n
o open file or !shell
p paste
q quit,x:ask
r reverse find,x:word under cursor
s find
t
u undo,x:redo
v view: 0,1,2,v:open list
w write, x:saveas
x
y mark: wl()[]{},x:inner
z delete wl()[]{},x:inner
spc format

How about ^Z?

^#12 or ^1^2?

Jump to marked point? Put position on stack

crash: report to launchpad

Modes: normal, mark(block,line,rectangle), find
close single doc
<c-1><c-2>: repeat 12 times
spell check
move to other tab
scroll:up, down,center,top, bottom
upper/lower case
big movements
swap two chars
look at to vim plugins: svn,snippets,easymove
complete

scripting: abc<enter><up><end>

Modeline: row:1/234 col:1 (python) 0%

When moving: show movement in "popup": [moved 240 lines forward]

Use number columns to show stuff: last changed line(s)

aliases: imoprt=import

check state of file every two seconds when active?

write docs on errors and write debug info

python3 -m spelltinkle

spt --beginner --verbose --read-only --black-and-white

colors:
fg:pygments(normal,comment,keyword,number,string),error,lineno,status
bg:normal,mark(normal,rectangle,lines),search,currenst line,lineno,error,
notice,status,outside-doc

pep8

"""
