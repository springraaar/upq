# This file is part of the "upq" program used on springfiles.com to manage file
# uploads, mirror distribution etc. It is published under the GPLv3.
#
#Copyright (C) 2011 Daniel Troeder (daniel #at# admin-box #dot# com)
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

#
# null task, does nothing
#

import upqtask
import upqqueuemngr

class Null_task(upqtask.UpqTask):
    def run(self):
        self.msg=""
	return True