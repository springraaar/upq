# This file is part of the "upq" program used on springfiles.com to manage file
# uploads, mirror distribution etc. It is published under the GPLv3.
#
#Copyright (C) 2011 Daniel Troeder (daniel #at# admin-box #dot# com)
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

#
# upload_file

from upqjob import UpqJob
import ftplib
import time

class Test(UpqJob):
    def check(self):
        self.enqueue_job()
        self.msg="Test job: "+str(self.jobid)+" data:"+str(self.jobdata)
        return True

    def run(self):
        time.sleep(1)
        self.enqueue_newjob("test", {})
        self.msg="Success run"
        return True

