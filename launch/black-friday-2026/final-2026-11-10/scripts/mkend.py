import sys
src=open('/home/claude/bf/end_std.py').read()
tag,hl,out=sys.argv[1],sys.argv[2],sys.argv[3]
src=src.replace("E=mk('BLACK FRIDAY','10% OFF ALL MERCH','10% OFF')",f"E=mk('BLACK FRIDAY','{tag}','{hl}')").replace("'end_std.mp4'",f"'{out}'")
exec(src)
