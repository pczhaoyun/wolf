import os
import os.path
from scrapy.utils.misc import load_object, walk_modules

filter_list = set(['__init__.py', 'base_wolf.py', 'yayaxz.py', 'seehd.py',
    #'cnscg.py',
    #'kuyi.py', 'mp4ba.py', 'hdbird.py', 'bt5156.py', 
    #'henbt.py', 'btbbt.py', 'lwgod.py', 
    #'btpanda.py',
    #'vhao.py',
    #'friok.py',
    #'mu.py', 
    #'bttiantang.py',
    #'simplecd.py',
    #'jinxiujiaqi.py',
])

def get_wolves(spider):
    wolves = list()
    for f in os.listdir(os.path.dirname(__file__)):
        if f.endswith('.py') and f not in filter_list:
            wolves.append(load_object("wolf.spiders.wolves.%s.Wolf" % f.split('.')[0])(spider))
    
    return wolves
