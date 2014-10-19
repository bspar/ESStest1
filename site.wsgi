import sys, os

sys.path.append('/var/www/ESStest1/')
os.chdir('var/www/ESStest1/')
import ess_site
application = ess_site.getapp()
